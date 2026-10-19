"""11 - Search visibility agent: SEO topical map + GEO/AEO answer visibility.

Counts and rates come from skills/search-visibility/scripts/search_visibility.py
(the single source of truth). The model only drafts page outlines and edits for
the top-ranked actions, for a human and legal/compliance to approve.

Examples:
    python 11-search-visibility-agent/agent.py --stats-only
    python 11-search-visibility-agent/agent.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, computed_block, run  # noqa: E402
from common.skills import load_skill_script  # noqa: E402

sv = load_skill_script("search-visibility", "search_visibility")

HERE = Path(__file__).parent
DEFAULT_PAGES = HERE / "sample-pages.csv"
DEFAULT_ANSWERS = HERE / "sample-answers.csv"

TASK = """You are a B2B growth marketer on a Value Added Services (VAS) team who owns
search visibility: SEO (ranking and clicks in search) and GEO/AEO (being named and cited
in AI answers). Clients are issuers, acquirers, merchants and fintechs. Code has checked
the topical map and measured AI answer visibility. Write:
1. A three-line summary for your manager: biggest gap, biggest quick win, what to track next.
2. For each of the top actions listed, a draft:
   - CREATE PAGE: the page's one question as the H1, a direct two- or three-sentence answer
     to put at the top, 4-6 question-style subheadings, the pillar page it must link to,
     and 3 FAQ questions.
   - IMPROVE PAGE: the specific edits (answer at the top, headings, sources, structured
     data, internal links), including any structure issue listed for that page.
3. Two title-and-description variants to test for each high-impression, low-CTR page.
4. What still needs a human: facts to confirm, claims needing legal/compliance approval.
Write answers in neutral, factual language. Use [UNKNOWN: ...] for product facts you were
not given. Do not name or compare competitors."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SEO topical-map checks and GEO/AEO answer visibility (math by code, drafts by model).")
    parser.add_argument("--pages", default=str(DEFAULT_PAGES),
                        help="topical map CSV: url,topic,role,target_question,links_to,impressions,clicks")
    parser.add_argument("--answers", default=str(DEFAULT_ANSWERS),
                        help="answer log CSV: checked_on,question,persona,engine,brand_mentioned,"
                             "our_url_cited,competitor_mentions")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="share of answers citing your page that counts as visible (default 0.5)")
    parser.add_argument("--top", type=int, default=3, help="how many actions the model drafts (default 3)")
    parser.add_argument("--stats-only", action="store_true",
                        help="print the computed review and stop (no model call)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()

    if args.top < 1:
        raise ValueError("--top must be at least 1")
    pages = sv.load_pages(args.pages)
    map_report = sv.check_topical_map(pages)
    vis = sv.answer_visibility(sv.load_checks(args.answers), pages, args.threshold)
    text = sv.format_report(map_report, vis)
    if args.stats_only:
        print(text)
        return 0
    todo = [q for q in vis.questions if q.action != "MAINTAIN"][:args.top]
    focus = "\n".join(f"- {q.action}: \"{q.question}\" (page {q.page or 'none yet'}, persona {q.persona})"
                      for q in todo) or "- none: every question is at or above the threshold"
    user = ("Review this search-visibility report and draft the work.\n\n" + computed_block(text)
            + f"\n\nTop {len(todo)} action(s) to draft:\n{focus}")
    print(ask(TASK, user, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
