"""08 - A/B test analyzer: offer test results by client segment.

Statistics come from skills/ab-test-analyzer/scripts/ab_stats.py (the single
source of truth). The model only explains the computed results and proposes
hypotheses, which it must label as untested.

Examples:
    python 08-ab-test-analyzer/agent.py --csv 08-ab-test-analyzer/sample-ab-results.csv --stats-only
    python 08-ab-test-analyzer/agent.py --csv 08-ab-test-analyzer/sample-ab-results.csv --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, computed_block, run  # noqa: E402
from common.skills import load_skill_script  # noqa: E402

ab = load_skill_script("ab-test-analyzer", "ab_stats")

DEFAULT_CSV = Path(__file__).with_name("sample-ab-results.csv")

TASK = """You are a B2B marketing analyst on a Value Added Services (VAS) team.
Clients are issuers, acquirers, merchants and fintechs. Code has run the statistics;
"visitors" means client contacts exposed to the offer. Write:
1. Result per segment in one line each, using the verdicts exactly as computed.
2. Why the pooled result is or is not a safe basis for a decision.
3. Possible explanations for any segment differences. Label every one
   "HYPOTHESIS (untested)" and say what evidence would test it.
4. A recommended next step per segment, with what still needs human sign-off.
Do not claim either offer "works" beyond what the verdicts say."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze an A/B offer test by client segment (stats by code, explanation by model).")
    parser.add_argument("--csv", default=str(DEFAULT_CSV),
                        help="CSV with segment,variant,visitors,conversions; visitors = contacts exposed")
    parser.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    parser.add_argument("--label-a", default="ROI assessment offer", help="name of variant A")
    parser.add_argument("--label-b", default="free pilot offer", help="name of variant B")
    parser.add_argument("--metric", default="demo requests", help="what a conversion counts")
    parser.add_argument("--stats-only", action="store_true",
                        help="print the computed statistics and stop (no model call)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()

    if not 0 < args.alpha < 1:
        raise ValueError("--alpha must be between 0 and 1")
    result = ab.analyze(ab.load_rows(args.csv), args.alpha)
    text = ab.format_report(result, args.label_a, args.label_b, args.metric)
    if args.stats_only:
        print(text)
        return 0
    print(ask(TASK, "Explain these offer-test results.\n\n" + computed_block(text), dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
