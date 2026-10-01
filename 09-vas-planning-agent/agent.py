"""09 - VAS planning agent: grow live client programs net of attrition.

Python works out how many new client programs are needed each month to hit a net
growth target after attrition (clients that deactivate or do not renew), then
fills that need from the cheapest channels first. The model explains the plan.

Example:
    python 09-vas-planning-agent/agent.py --current-active 300 --target-net 100 \\
        --months 6 --monthly-churn 0.01 \\
        --channels "email_nurture:3000:0.001:0.5,account_manager:120:0.08:150,webinar:600:0.01:20,workshop:25:0.2:2000" \\
        --stats-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, computed_block, run  # noqa: E402
from common.skills import load_skill_script  # noqa: E402

capacity = load_skill_script("vas-capacity-planner", "capacity")

TASK = """You are a B2B growth planner on a Value Added Services (VAS) marketing team.
Clients are issuers, acquirers, merchants and fintechs; a "program" is one client live
on one VAS product. Code has computed the plan. Write:
1. The headline: new programs needed per month and why (attrition replacement + net growth).
2. Channel plan: which channels carry the load, which is the costly marginal channel,
   and what it would take to shift volume to cheaper channels.
3. Which inputs are assumptions the team must replace with real data (channel costs,
   conversion rates, attrition), labeled [UNKNOWN: ...] where not supplied.
Cost per contact for account managers is the loaded cost of a client conversation."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan new VAS client programs per month to reach a net growth target "
                    "after attrition, and allocate channels cheapest-first.")
    parser.add_argument("--current-active", type=int, required=True,
                        help="live client programs today")
    parser.add_argument("--target-net", type=int, required=True,
                        help="net new live client programs wanted by the end of the horizon")
    parser.add_argument("--months", type=int, required=True, help="planning horizon in months")
    parser.add_argument("--monthly-churn", type=float, required=True,
                        help="monthly attrition: share of live client programs that deactivate "
                             "or do not renew each month, for example 0.01 for 1%%")
    parser.add_argument("--channels", required=True,
                        help="comma-separated name:monthly_contacts:conversion_to_signed:cost_per_contact; "
                             "for account managers, cost per contact is the loaded cost of one client "
                             "conversation (an assumption you replace)")
    parser.add_argument("--stats-only", action="store_true",
                        help="print the computed plan and stop (no model call)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()

    channels = capacity.parse_channels(args.channels)
    text = capacity.format_plan(capacity.plan(args.current_active, args.target_net, args.months,
                                              args.monthly_churn, channels))
    if args.stats_only:
        print(text)
        return 0
    print(ask(TASK, "Explain this plan.\n\n" + computed_block(text), dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
