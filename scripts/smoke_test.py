"""Smoke-test every Python agent without calling a model.

For each agent: --help must work, and each case below must exit with the
expected code and print the expected text. API keys are removed from the
environment, so nothing can reach a real model.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FUNNEL = "reached:0.70,engaged:0.25,pilot:0.60,signed:0.30"
CHANNELS = ("email_nurture:3000:0.001:0.5,account_manager:120:0.08:150,"
            "webinar:600:0.01:20,workshop:25:0.2:2000")
PLAN_07 = ["--target", "20", "--eligible", "600", "--funnel", FUNNEL, "--budget", "120000", "--weeks", "12"]
PLAN_09 = ["--current-active", "300", "--target-net", "100", "--months", "6",
           "--monthly-churn", "0.01", "--channels", CHANNELS]

# (agent folder, args, expected exit code, must contain, must not contain)
CASES = [
    ("04-tool-use-python", ["--stats-only"], 0,
     ["Risk Scoring Service", "active 8 | inactive 4"], []),
    ("04-tool-use-python", ["--dry-run"], 0,
     ["DRY RUN", "COMPUTED", "client_id, client_type, vas_product"], ["C001", "2025-02-03"]),
    ("05-multi-agent-workflow", ["--dry-run"], 0,
     ["1/3 planner", "2/3 writer", "3/3 critic", "Regional marketing-consent rules", "Risk Scoring Service"], []),
    ("07-planning-agent", PLAN_07 + ["--stats-only"], 0,
     ["INFEASIBLE", "supports about 18 signed clients, not 20"], []),
    ("07-planning-agent", PLAN_07 + ["--dry-run"], 0, ["DRY RUN", "COMPUTED", "INFEASIBLE"], []),
    ("07-planning-agent", ["--target", "20", "--eligible", "600", "--funnel", "reached=0.7",
                           "--budget", "1", "--weeks", "1"], 2, ["Input error"], ["Traceback"]),
    ("08-ab-test-analyzer", ["--csv", "08-ab-test-analyzer/sample-ab-results.csv", "--stats-only"], 0,
     ["fintech_acquirers", "B better", "A better", "segments disagree"], []),
    ("08-ab-test-analyzer", ["--dry-run"], 0, ["HYPOTHESIS (untested)", "COMPUTED"], []),
    ("08-ab-test-analyzer", [], 2, ["ANTHROPIC_API_KEY is not set"], ["Traceback"]),
    ("09-vas-planning-agent", PLAN_09 + ["--stats-only"], 0,
     ["20.09", "Marginal (most costly) channel in use: workshop", "FEASIBLE"], []),
    ("09-vas-planning-agent", PLAN_09 + ["--dry-run"], 0, ["DRY RUN", "COMPUTED"], []),
    ("10-agents-in-production", ["--static-only"], 0,
     ["Static checks: 1/10 passed", "[FLAG] confidentiality / client-data rule",
      "[FLAG] claims need substantiation/approval"], []),
    ("10-agents-in-production", ["--dry-run"], 0, ["DRY RUN", "Prompt under review"], []),
]


def clean_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
    for key in ("LLM_PROVIDER", "ANTHROPIC_MODEL", "OPENAI_MODEL"):
        env.pop(key, None)
    return env


def run(folder: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, f"{folder}/agent.py", *args], cwd=ROOT, env=clean_env(),
                          capture_output=True, text=True, timeout=60)


def main() -> int:
    failures = []
    agents = sorted(p.parent.name for p in ROOT.glob("[0-9][0-9]-*/agent.py"))
    for folder in agents:
        result = run(folder, ["--help"])
        if result.returncode != 0 or "--dry-run" not in result.stdout:
            failures.append(f"{folder} --help failed:\n{result.stderr}")
    covered = {case[0] for case in CASES}
    for folder in agents:
        if folder not in covered:
            failures.append(f"{folder}: no smoke case; add one to scripts/smoke_test.py")
    for folder, args, code, must, must_not in CASES:
        if folder not in agents:
            continue
        result = run(folder, args)
        output = result.stdout + result.stderr
        label = f"{folder} {' '.join(args)}".strip()
        if result.returncode != code:
            failures.append(f"{label}: exit {result.returncode}, expected {code}\n{output[-800:]}")
            continue
        failures += [f"{label}: missing {text!r}" for text in must if text not in output]
        failures += [f"{label}: should not contain {text!r}" for text in must_not if text in output]
    if failures:
        print("Smoke test FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"Smoke test OK: {len(agents)} agents passed --help, {len(CASES)} cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
