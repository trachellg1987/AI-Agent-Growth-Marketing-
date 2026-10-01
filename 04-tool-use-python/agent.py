"""04 - Tool use with Python: summarize a client-program export, then ask the model.

Python reads the CSV and counts live and inactive client programs per VAS
product. The model sees only the column names and those counts, never the
client rows, and suggests where account managers should focus.

Examples:
    python 04-tool-use-python/agent.py --stats-only
    python 04-tool-use-python/agent.py --dry-run
    python 04-tool-use-python/agent.py --question "Which product needs a win-back play?"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, computed_block, run  # noqa: E402
from common.skills import load_skill_script  # noqa: E402

summary_lib = load_skill_script("client-program-summary", "program_summary")

DEFAULT_CSV = Path(__file__).with_name("sample-vas-client-programs.csv")
DEFAULT_QUESTION = "Which VAS products should account managers prioritize next quarter, and why?"

TASK = """You are a B2B growth analyst on a Value Added Services (VAS) marketing team.
Clients are issuers, acquirers, merchants and fintechs. You receive the column names
of a client-program export and counts computed by code. You never see client rows.

Answer the question in three short sections:
1. What the counts show (cite the numbers exactly as given).
2. Two or three recommended focus areas for account managers, each with the count that supports it.
3. What data is missing before acting (label each item [UNKNOWN: ...]).
Do not speculate about why any specific client went inactive."""


def build_prompt(columns: list[str], stats_text: str, question: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Export columns (no rows shared): {', '.join(columns)}\n\n"
        + computed_block(stats_text)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Count live and inactive VAS client programs per product from a CSV, "
                    "then ask a model where account managers should focus.")
    parser.add_argument("--csv", default=str(DEFAULT_CSV),
                        help="client-program export (default: the fictional sample CSV)")
    parser.add_argument("--question", default=DEFAULT_QUESTION, help="question for the model")
    parser.add_argument("--stats-only", action="store_true",
                        help="print the computed counts and stop (no model call)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()

    columns, rows = summary_lib.load(args.csv)
    stats_text = summary_lib.format_summary(summary_lib.summarize(rows))
    if args.stats_only:
        print(stats_text)
        return 0
    print(ask(TASK, build_prompt(columns, stats_text, args.question), dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
