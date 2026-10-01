---
name: agent-prompt-review
description: Review a B2B marketing agent prompt before launch with ten repeatable static checks (approval step, performance claims, disparagement, sensitive data, confidentiality, claims approval, consent, secrets, unknowns, output format), then a model review.
---

# Agent prompt review

## When to use

Before any agent that drafts or sends client-facing material goes live, or when its prompt changes.

## Inputs

The agent's prompt as a text or Markdown file.

## Steps

1. Run the static checks (no model): `python 10-agents-in-production/agent.py --static-only --prompt-file <file>`.
2. Fix every FLAG, or record why it is acceptable.
3. Run the model review for risks regex cannot see (tone, implied claims, tool permissions).
4. A human signs off. Legal/compliance approves any claim the agent may make.

## Output

`Static checks: N/10 passed`, one PASS/FLAG line per check, then the model's risk table and
a rewritten prompt.

## Guardrails

- Static checks catch obvious gaps only. Passing them is necessary, not sufficient.
- Never paste real client data into a prompt under review.

## Used by

`10-agents-in-production`
