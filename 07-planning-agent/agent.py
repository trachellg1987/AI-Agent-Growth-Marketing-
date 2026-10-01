"""07 - Planning agent: work backward from a new-client target to weekly activity.

Python does the funnel math (backward from the target, forward from the eligible
base) and raises a feasibility flag. The model turns the numbers into a plan and
proposes ways to close any gap.

Examples:
    python 07-planning-agent/agent.py --target 20 --eligible 600 \\
        --funnel "reached:0.70,engaged:0.25,pilot:0.60,signed:0.30" \\
        --budget 120000 --weeks 12 --stats-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, computed_block, run  # noqa: E402
from common.skills import load_skill_script  # noqa: E402

funnel = load_skill_script("funnel-planner", "funnel")

TASK = """You are a B2B growth planner on a Value Added Services (VAS) marketing team.
Clients are issuers, acquirers, merchants and fintechs. Code has already computed
the funnel numbers. Write a short plan:
1. Feasibility: restate the FEASIBLE/INFEASIBLE line and what it means.
2. Weekly activity: what account managers and marketing must do each week (cite the per-week numbers).
3. If infeasible, compare the options given (lower target, widen base, lift a rate) and say what
   evidence would be needed before committing to each. Do not invent new rates.
4. Risks and [UNKNOWN: ...] items."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backward-plan new signed clients through a B2B funnel and flag feasibility.")
    parser.add_argument("--target", type=int, required=True, help="new signed clients wanted")
    parser.add_argument("--eligible", type=int, required=True,
                        help="eligible clients in scope (for example regional issuers without the product)")
    parser.add_argument("--funnel", required=True,
                        help="ordered stages as name:rate, each rate a share of the previous stage, "
                             "for example reached:0.70,engaged:0.25,pilot:0.60,signed:0.30")
    parser.add_argument("--budget", type=float, required=True, help="marketing budget in dollars")
    parser.add_argument("--weeks", type=int, required=True, help="planning horizon in weeks")
    parser.add_argument("--stats-only", action="store_true",
                        help="print the computed plan and stop (no model call)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()

    stages = funnel.parse_funnel(args.funnel)
    text = funnel.format_plan(funnel.plan(args.target, args.eligible, stages, args.budget, args.weeks))
    if args.stats_only:
        print(text)
        return 0
    print(ask(TASK, "Build the plan from these numbers.\n\n" + computed_block(text), dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
