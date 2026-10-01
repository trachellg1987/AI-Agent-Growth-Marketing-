"""10 - Agents in production: review an agent prompt before it goes live.

Step 1 (code): repeatable static checks for common B2B risks.
Step 2 (model): a deeper review that uses the static results as evidence.

Examples:
    python 10-agents-in-production/agent.py --static-only
    python 10-agents-in-production/agent.py --prompt-file my-agent-prompt.md --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, computed_block, run  # noqa: E402
from common.skills import load_skill_script  # noqa: E402

checks_lib = load_skill_script("agent-prompt-review", "static_checks")

DEFAULT_PROMPT = Path(__file__).with_name("sample-agent-prompt.md")

TASK = """You review prompts for AI agents used by a B2B Value Added Services (VAS) marketing
team. Clients are issuers, acquirers, merchants and fintechs. Before an agent goes live, check:
- Performance claims: any promised result (for example a fraud-reduction percentage) must be
  substantiated and approved by legal/compliance, or removed.
- Client confidentiality: no non-public client data (incident or fraud-case notes, contract
  terms) in prompts or outputs; no naming of real clients.
- Regional marketing consent: recipients must have consent or a contract basis; honor opt-outs.
- Competitor disparagement.
- Human approval before anything client-facing is sent.
- Tool permissions: least privilege (read only what is needed, no bulk exports).
- Failure handling: what the agent does with missing data.
Output: (1) a risk table with severity (high/medium/low), the quoted line, and the fix;
(2) a rewritten prompt that fixes every high and medium risk. The static results below
came from code; do not contradict them, but you may add risks they missed."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review a B2B marketing agent prompt with static checks plus a model review.")
    parser.add_argument("--prompt-file", default=str(DEFAULT_PROMPT),
                        help="agent prompt to review (default: the deliberately weak sample)")
    parser.add_argument("--static-only", action="store_true",
                        help="run the static checks only (no model call)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()

    path = Path(args.prompt_file)
    if not path.is_file():
        raise FileNotFoundError(f"prompt file not found: {args.prompt_file}")
    text = path.read_text(encoding="utf-8")
    report = checks_lib.format_checks(checks_lib.run_checks(text))
    if args.static_only:
        print(report)
        return 0
    user = f"Prompt under review:\n<<<\n{text.strip()}\n>>>\n\n" + computed_block(report)
    print(ask(TASK, user, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
