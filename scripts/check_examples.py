"""Check that computed blocks in the docs match a fresh run of the agents.

A computed block in any Markdown file looks like this:

    <!-- computed: python 07-planning-agent/agent.py --target 20 ... --stats-only -->
    ````text
    ...exact output...
    ````

Four-backtick fences let the output itself contain ``` fences.

This script re-runs every command (no model calls: only --stats-only,
--static-only and --dry-run are allowed) and fails if the text differs.
Run with --update to rewrite the blocks from fresh output.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK = re.compile(r"(<!-- computed: (?P<cmd>.+?) -->\n````text\n)(?P<body>.*?)(\n````)", re.DOTALL)
OFFLINE_FLAGS = ("--stats-only", "--static-only", "--dry-run")


def run_command(cmd: str) -> str:
    argv = shlex.split(cmd)
    if not argv or argv[0] != "python":
        raise ValueError(f"computed command must start with 'python': {cmd}")
    if not any(flag in argv for flag in OFFLINE_FLAGS) and "ab_stats.py" not in cmd:
        raise ValueError(f"computed command must run offline ({', '.join(OFFLINE_FLAGS)}): {cmd}")
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
    for key in ("LLM_PROVIDER", "ANTHROPIC_MODEL", "OPENAI_MODEL"):
        env.pop(key, None)
    result = subprocess.run([sys.executable, *argv[1:]], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {cmd}\n{result.stderr}")
    return result.stdout.rstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify (or --update) computed blocks in Markdown files.")
    parser.add_argument("--update", action="store_true", help="rewrite blocks from fresh output")
    args = parser.parse_args()

    files = [p for p in sorted(ROOT.rglob("*.md")) if ".git" not in p.parts and "node_modules" not in p.parts]
    checked, stale = 0, []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "<!-- computed:" not in text:
            continue

        def replace(match: re.Match) -> str:
            nonlocal checked
            checked += 1
            fresh = run_command(match.group("cmd"))
            if fresh != match.group("body"):
                stale.append(f"{path.relative_to(ROOT)}: {match.group('cmd')}")
            return match.group(1) + fresh + match.group(4)

        new_text = BLOCK.sub(replace, text)
        if args.update and new_text != text:
            path.write_text(new_text, encoding="utf-8")

    if stale and not args.update:
        print("Computed blocks are out of date (run: make examples-update):")
        for item in stale:
            print(f"  - {item}")
        return 1
    action = "updated" if args.update and stale else "match a fresh run"
    print(f"Computed blocks OK: {checked} block(s) {action}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
