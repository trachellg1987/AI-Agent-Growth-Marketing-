"""Shared test helpers."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.skills import load_skill_script  # noqa: E402

ab_stats = load_skill_script("ab-test-analyzer", "ab_stats")
funnel = load_skill_script("funnel-planner", "funnel")
capacity = load_skill_script("vas-capacity-planner", "capacity")
program_summary = load_skill_script("client-program-summary", "program_summary")
static_checks = load_skill_script("agent-prompt-review", "static_checks")
