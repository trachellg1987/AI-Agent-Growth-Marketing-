# Skill template

Copy this into `skills/<skill-name>/SKILL.md`. The front matter `name` must match the folder
name (`make validate` checks this).

```markdown
---
name: skill-name
description: One sentence saying what the skill does and when to use it.
---

# Skill name

## When to use

## Inputs

## Steps

## Output

## Guardrails

## Used by
```

If the skill needs math, put it in `skills/<skill-name>/scripts/<name>.py` (standard library
only), load it from agents with `common.skills.load_skill_script`, and add unit tests in `tests/`.
