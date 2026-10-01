"""Validate repo structure and content rules. Standard library only; no model calls.

Checks:
- numbered agent folders (01-..., 02-...) are contiguous and each has README.md,
  prompt.md and example-output.md; Python agents support --dry-run
- every example-output.md and case study is labeled ILLUSTRATIVE
- every skill has a SKILL.md whose front matter names the folder
- context templates keep their [FILL IN] placeholders
- no leftover consumer-VAS terms, and nothing that looks like a secret
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = re.compile(r"^(\d{2})-[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED_ROOT_FILES = [
    "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "SECURITY.md", "Makefile",
    "requirements.txt", ".gitignore", ".env.example", ".markdownlint.json",
    "common/llm.py", "images/banner.svg", "skills/README.md", "skills/SKILL-TEMPLATE.md",
    "case-studies/README.md", "case-studies/_template.md",
    ".agents/product-marketing-context.md", ".agents/growth-metrics-context.md",
]
AGENT_FILES = ("README.md", "prompt.md", "example-output.md")
# This repo is about B2B VAS. These words signal leftover consumer/telecom framing.
CONSUMER_TERMS = re.compile(
    r"\b(subscribers?|subscriptions?|prepaid|postpaid|SMS|free trials?|trial users?|"
    r"Cloud Backup|Device Protection|Premium Support|customers?|consumers?)\b",
    re.IGNORECASE,
)
SECRET = re.compile(r"\b(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16})\b")
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".csv", ".txt", ".svg", ".toml", ""}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
TERM_CHECK_EXEMPT = {"scripts/validate.py"}


def text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file() and (path.suffix in TEXT_SUFFIXES or path.name == "Makefile"):
            files.append(path)
    return sorted(files)


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_ROOT_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")

    agents = sorted(p for p in ROOT.iterdir() if p.is_dir() and AGENT_DIR.match(p.name))
    numbers = [int(p.name[:2]) for p in agents]
    if numbers != list(range(1, len(numbers) + 1)):
        errors.append(f"agent folders must be numbered 01..NN with no gaps or repeats: {numbers}")
    python_agents = 0
    for folder in agents:
        for name in AGENT_FILES:
            if not (folder / name).is_file():
                errors.append(f"{folder.name}: missing {name}")
        example = folder / "example-output.md"
        if example.is_file() and "ILLUSTRATIVE" not in example.read_text(encoding="utf-8"):
            errors.append(f"{folder.name}/example-output.md: not labeled ILLUSTRATIVE")
        agent = folder / "agent.py"
        if agent.is_file():
            python_agents += 1
            if "--dry-run" not in agent.read_text(encoding="utf-8"):
                errors.append(f"{folder.name}/agent.py: no --dry-run option")

    for study in sorted((ROOT / "case-studies").glob("*.md")):
        if study.name != "README.md" and "ILLUSTRATIVE" not in study.read_text(encoding="utf-8"):
            errors.append(f"case-studies/{study.name}: not labeled ILLUSTRATIVE")

    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    for skill in skills:
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"skills/{skill.name}: missing SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        front = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not front:
            errors.append(f"skills/{skill.name}/SKILL.md: missing --- front matter ---")
            continue
        meta = dict(line.split(":", 1) for line in front.group(1).splitlines() if ":" in line)
        if meta.get("name", "").strip() != skill.name:
            errors.append(f"skills/{skill.name}/SKILL.md: front matter name must be {skill.name!r}")
        if not meta.get("description", "").strip():
            errors.append(f"skills/{skill.name}/SKILL.md: empty description")

    for rel in (".agents/product-marketing-context.md", ".agents/growth-metrics-context.md"):
        path = ROOT / rel
        if path.is_file() and "[FILL IN" not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel}: [FILL IN] placeholders were removed; keep the template generic")

    for path in text_files():
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if rel not in TERM_CHECK_EXEMPT:
            for lineno, line in enumerate(text.splitlines(), start=1):
                match = CONSUMER_TERMS.search(line)
                if match:
                    errors.append(f"{rel}:{lineno}: consumer-VAS term {match.group(0)!r} (use client terms)")
        if SECRET.search(text):
            errors.append(f"{rel}: looks like it contains an API key or secret")

    if errors:
        print("Validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"Validation OK: {len(agents)} numbered agent folders ({python_agents} with agent.py), "
          f"{len(skills)} skills, {len(text_files())} text files checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
