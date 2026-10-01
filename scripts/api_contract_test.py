"""API contract test: run real agents against a local fake model server.

Starts an HTTP server on a free port that answers like the Anthropic Messages
API (/v1/messages) and the OpenAI Chat Completions API (/v1/chat/completions),
points the official SDKs at it with ANTHROPIC_BASE_URL / OPENAI_BASE_URL and fake
keys, and checks what the agents send and print. No real API is called.

Requires the SDKs: pip install -r requirements.txt
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUESTS: list[dict] = []
LOCK = threading.Lock()


class FakeModelAPI(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:  # keep test output quiet
        pass

    def do_POST(self) -> None:
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        path = self.path.split("?", 1)[0]
        with LOCK:
            REQUESTS.append({"path": path, "body": body, "headers": {k.lower(): v for k, v in self.headers.items()}})
            n = len(REQUESTS)
        text = f"FAKE-MODEL-TEXT-{n}"
        if self.headers.get("x-api-key") == "bad-key":
            return self._send(401, {"type": "error", "error": {"type": "authentication_error",
                                                               "message": "invalid x-api-key"}})
        if path == "/v1/messages":
            return self._send(200, {
                "id": f"msg_{n}", "type": "message", "role": "assistant", "model": body.get("model"),
                "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 5},
            })
        if path == "/v1/chat/completions":
            return self._send(200, {
                "id": f"chatcmpl-{n}", "object": "chat.completion", "created": 0, "model": body.get("model"),
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": text}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            })
        self._send(404, {"error": {"message": f"unknown path {path}"}})

    def _send(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_agent(port: int, folder: str, args: list[str], **env_overrides: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
    for key in ("LLM_PROVIDER", "ANTHROPIC_MODEL", "OPENAI_MODEL"):
        env.pop(key, None)
    env.update({
        "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{port}",
        "OPENAI_BASE_URL": f"http://127.0.0.1:{port}/v1",
        "NO_PROXY": "127.0.0.1,localhost",
        "no_proxy": "127.0.0.1,localhost",
    })
    env.update(env_overrides)
    return subprocess.run([sys.executable, f"{folder}/agent.py", *args], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=120)


def take_requests() -> list[dict]:
    with LOCK:
        out = list(REQUESTS)
        REQUESTS.clear()
    return out


def anthropic_prompt(req: dict) -> tuple[str, str]:
    body = req["body"]
    user = body["messages"][0]["content"]
    return body.get("system", ""), user if isinstance(user, str) else json.dumps(user)


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeModelAPI)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    failures: list[str] = []

    def check(cond: bool, message: str) -> None:
        print(f"  [{'ok' if cond else 'FAIL'}] {message}")
        if not cond:
            failures.append(message)

    try:
        print(f"Fake model API on 127.0.0.1:{port}")

        print("Agent 08 via Anthropic:")
        result = run_agent(port, "08-ab-test-analyzer", [], ANTHROPIC_API_KEY="test-key")
        reqs = take_requests()
        check(result.returncode == 0, f"exit code 0 (got {result.returncode}) {result.stderr[-300:]}")
        check("FAKE-MODEL-TEXT-1" in result.stdout, "prints the model text")
        check(len(reqs) == 1 and reqs[0]["path"] == "/v1/messages", "one call to /v1/messages")
        if reqs:
            system, user = anthropic_prompt(reqs[0])
            check("COMPUTED (by code" in user, "prompt includes the COMPUTED block")
            check("confidential information" in system, "system prompt includes the shared RULES")
            check(reqs[0]["headers"].get("x-api-key") == "test-key", "sends the key from ANTHROPIC_API_KEY")
            check(reqs[0]["body"].get("fallbacks") == "default", "requests server-side refusal fallback")

        print("Agent 04 via Anthropic:")
        result = run_agent(port, "04-tool-use-python", [], ANTHROPIC_API_KEY="test-key")
        reqs = take_requests()
        check(result.returncode == 0, f"exit code 0 (got {result.returncode}) {result.stderr[-300:]}")
        if reqs:
            _, user = anthropic_prompt(reqs[0])
            check("client_id, client_type, vas_product, status, start_date, source" in user,
                  "sends the column names")
            check("COMPUTED (by code" in user, "prompt includes the COMPUTED block")
            leaked = [v for v in ("C001", "C012", "2025-02-03", "2024-11-18") if v in user]
            check(not leaked, f"sends no data rows (leaked: {leaked})")
        else:
            check(False, "made a model call")

        print("Agent 05 via Anthropic:")
        result = run_agent(port, "05-multi-agent-workflow", [], ANTHROPIC_API_KEY="test-key")
        reqs = take_requests()
        check(result.returncode == 0, f"exit code 0 (got {result.returncode}) {result.stderr[-300:]}")
        check(len(reqs) == 3, f"makes three calls (got {len(reqs)})")
        if len(reqs) == 3:
            check("FAKE-MODEL-TEXT-1" in anthropic_prompt(reqs[1])[1], "writer receives the planner output")
            check("FAKE-MODEL-TEXT-2" in anthropic_prompt(reqs[2])[1], "critic receives the writer output")
            check("CRITIC" in anthropic_prompt(reqs[2])[0], "third call uses the critic role")
        check("FAKE-MODEL-TEXT-3" in result.stdout, "prints the critic review")

        print("Agent 08 via OpenAI:")
        result = run_agent(port, "08-ab-test-analyzer", [], LLM_PROVIDER="openai", OPENAI_API_KEY="test-key")
        reqs = take_requests()
        check(result.returncode == 0, f"exit code 0 (got {result.returncode}) {result.stderr[-300:]}")
        check("FAKE-MODEL-TEXT-1" in result.stdout, "prints the model text")
        check(len(reqs) == 1 and reqs[0]["path"] == "/v1/chat/completions", "one call to /v1/chat/completions")
        if reqs:
            messages = reqs[0]["body"]["messages"]
            check(messages[0]["role"] == "system" and "confidential information" in messages[0]["content"],
                  "system message includes the shared RULES")
            check("COMPUTED (by code" in messages[1]["content"], "prompt includes the COMPUTED block")

        print("Errors:")
        result = run_agent(port, "08-ab-test-analyzer", [])
        check(result.returncode == 2 and "ANTHROPIC_API_KEY is not set" in result.stderr,
              "missing key gives a clear message and exit code 2")
        check("Traceback" not in result.stderr, "missing key shows no traceback")
        result = run_agent(port, "08-ab-test-analyzer", [], ANTHROPIC_API_KEY="bad-key")
        check(result.returncode == 2 and "rejected the key" in result.stderr, "rejected key gives a clear message")
        check("Traceback" not in result.stderr, "rejected key shows no traceback")
        take_requests()
    finally:
        server.shutdown()

    if failures:
        print(f"API contract test FAILED: {len(failures)} check(s).")
        return 1
    print("API contract test OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
