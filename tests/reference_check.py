"""Check that references in the docs point at things that exist.

- Relative Markdown links and images resolve to files or folders.
- `python <path>.py` commands in Markdown point at existing scripts.
- `make <target>` in inline code names a real Makefile target.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
PY_CMD = re.compile(r"\bpython3? ((?:[\w.-]+/)*[\w.-]+\.py)\b")
MAKE_CMD = re.compile(r"`make ([a-z][a-z-]*)\b")


def markdown_files() -> list[Path]:
    return [p for p in sorted(ROOT.rglob("*.md"))
            if not any(part in (".git", "node_modules") for part in p.parts)]


def make_targets() -> set[str]:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    return set(re.findall(r"^([a-z][a-z-]*):", text, re.MULTILINE))


def main() -> int:
    errors = []
    targets = make_targets()
    for path in markdown_files():
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            file_part = target.split("#", 1)[0]
            if file_part and not (path.parent / file_part).resolve().exists():
                errors.append(f"{rel}: broken link {target}")
        for script in PY_CMD.findall(text):
            if not (ROOT / script).is_file():
                errors.append(f"{rel}: command refers to missing script {script}")
        for target in MAKE_CMD.findall(text):
            if target not in targets:
                errors.append(f"{rel}: unknown make target 'make {target}'")
    if errors:
        print("Reference check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"Reference check OK: {len(markdown_files())} Markdown files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
