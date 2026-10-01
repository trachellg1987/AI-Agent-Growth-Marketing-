"""05 - Multi-agent workflow: Planner -> Writer -> Critic.

Three chained model calls. Each role has a narrow job, and each call's output
becomes the next call's input. The Critic checks B2B risks before a human sees
the draft. Nothing is sent to a client by this script.

Examples:
    python 05-multi-agent-workflow/agent.py --dry-run
    python 05-multi-agent-workflow/agent.py --question "How do we raise adoption of the Dispute Management Tool among acquirers?"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, run  # noqa: E402

DEFAULT_QUESTION = ("How should we raise adoption of the Risk Scoring Service among "
                    "regional issuers next quarter?")
DEFAULT_CONTEXT = ROOT / ".agents" / "product-marketing-context.md"

PLANNER = """You are the PLANNER on a B2B Value Added Services (VAS) marketing team.
Clients are issuers, acquirers, merchants and fintechs. Turn the question into a plan
with: goal, target client segment, buyer personas, channels (account-manager
conversations, client webinars, email nurture, workshops), a pilot offer if relevant,
and how success is measured. Use only facts in the context; mark gaps [UNKNOWN: ...]."""

WRITER = """You are the WRITER. Using the plan, draft (a) a 120-word email for the buyer
persona and (b) five account-manager talking points. Use fictional client names only.
Where a performance claim would help, write [CLAIM NEEDS SUBSTANTIATION] instead."""

CRITIC = """You are the CRITIC, a compliance-minded reviewer for B2B client marketing.
Review the draft against this checklist and report PASS or FIX for each, quoting the line:
1. Unsupported performance claims (any figure or promise not in the supplied context).
2. Client confidentiality (naming or implying a real client, or using non-public client data).
3. Regional marketing-consent rules (is the audience one we have consent or a contract basis to contact?).
4. Claims needing legal/compliance approval before use.
5. Competitor disparagement.
End with a revised draft that fixes every FIX, and a line: "Requires human and legal/compliance approval before use." """

PLACEHOLDER = "[{role} output appears here in a live run]"


def load_context(path: str | None) -> str:
    if not path:
        return "[UNKNOWN: no product-marketing context supplied]"
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"context file not found: {path}")
    return file.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Planner -> Writer -> Critic chain for a B2B VAS marketing question.")
    parser.add_argument("--question", default=DEFAULT_QUESTION, help="the growth question to work on")
    parser.add_argument("--context", default=str(DEFAULT_CONTEXT),
                        help="product-marketing context file (default .agents/product-marketing-context.md)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print all three prompts that would be sent, without calling a model")
    args = parser.parse_args()

    context = load_context(args.context)
    plan = ask(PLANNER, f"Question: {args.question}\n\nContext:\n{context}",
               dry_run=args.dry_run, label="1/3 planner")
    if args.dry_run:
        print(plan + "\n")
        plan = PLACEHOLDER.format(role="Planner")

    draft = ask(WRITER, f"Question: {args.question}\n\nPlan:\n{plan}",
                dry_run=args.dry_run, label="2/3 writer")
    if args.dry_run:
        print(draft + "\n")
        draft = PLACEHOLDER.format(role="Writer")

    review = ask(CRITIC, f"Context:\n{context}\n\nDraft to review:\n{draft}",
                 dry_run=args.dry_run, label="3/3 critic")
    if args.dry_run:
        print(review)
        return 0

    print("## Plan\n\n" + plan.strip() + "\n\n## Draft\n\n" + draft.strip()
          + "\n\n## Critic review\n\n" + review.strip())
    return 0


if __name__ == "__main__":
    run(main)
