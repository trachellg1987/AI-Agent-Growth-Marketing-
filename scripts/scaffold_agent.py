"""Create the next numbered agent folder from a template.

Usage:
    python scripts/scaffold_agent.py --name pilot-follow-up            # prompt-only agent
    python scripts/scaffold_agent.py --name pilot-follow-up --python   # adds agent.py
(or: make scaffold NAME=pilot-follow-up PYTHON=1)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

README = """# {num} - {title}

What this agent does, in one sentence: [FILL IN]

## When to use it

[FILL IN]

## How to run

{run}

## Files

- `prompt.md`: the prompt
- `example-output.md`: an illustrative example
"""

PROMPT = """# Prompt: {title}

## Role

You are [FILL IN] on a B2B Value Added Services (VAS) marketing team. Clients are
issuers, acquirers, merchants and fintechs.

## Task

[FILL IN]

## Rules

- Use only facts and numbers you are given. Label gaps [UNKNOWN: ...].
- No performance claims unless supplied; write [CLAIM NEEDS SUBSTANTIATION].
- Client-facing output is a draft for human and legal/compliance approval.
"""

EXAMPLE = """# Example output: {title}

> ILLUSTRATIVE: fictional clients and data. Not real results.

[FILL IN]
"""

AGENT = '''"""{num} - {title}."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.llm import ask, run  # noqa: E402

TASK = (Path(__file__).with_name("prompt.md")).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="{title}")
    parser.add_argument("--input", required=True, help="text to work on")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the prompt that would be sent, without calling a model")
    args = parser.parse_args()
    print(ask(TASK, args.input, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    run(main)
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold the next numbered agent folder.")
    parser.add_argument("--name", required=True, help="lowercase-hyphenated name, for example pilot-follow-up")
    parser.add_argument("--python", action="store_true", help="also create agent.py")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.name):
        print("Input error: --name must be lowercase letters, digits and hyphens", file=sys.stderr)
        return 2
    existing = [int(p.name[:2]) for p in ROOT.glob("[0-9][0-9]-*") if p.is_dir()]
    num = f"{max(existing, default=0) + 1:02d}"
    folder = ROOT / f"{num}-{args.name}"
    folder.mkdir()
    title = args.name.replace("-", " ").capitalize()
    run_text = (f"```bash\npython {folder.name}/agent.py --input \"...\" --dry-run\n```"
                if args.python else "Paste `prompt.md` into your model of choice.")
    (folder / "README.md").write_text(README.format(num=num, title=title, run=run_text), encoding="utf-8")
    (folder / "prompt.md").write_text(PROMPT.format(title=title), encoding="utf-8")
    (folder / "example-output.md").write_text(EXAMPLE.format(title=title), encoding="utf-8")
    if args.python:
        (folder / "agent.py").write_text(AGENT.format(num=num, title=title), encoding="utf-8")
    print(f"Created {folder.relative_to(ROOT)}/")
    if args.python:
        print("Add a smoke case for it in scripts/smoke_test.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
