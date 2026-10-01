"""Load a skill's helper script by path.

Skill folders use hyphens (skills/ab-test-analyzer/), so they are not Python
packages. Agents load the math from the skill instead of copying it, which keeps
each calculation in exactly one place.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_skill_script(skill: str, script: str) -> ModuleType:
    path = ROOT / "skills" / skill / "scripts" / f"{script}.py"
    if not path.is_file():
        raise FileNotFoundError(f"Skill script not found: {path.relative_to(ROOT)}")
    name = f"skill_{skill.replace('-', '_')}_{script}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
