---
name: account-brief
description: Turn an account manager's raw notes about a client into a one-page meeting brief with goals, open questions, relevant VAS products, and risks. Use before a client meeting.
---

# Account brief

## When to use

An account manager has a client meeting coming up and has scattered notes.

## Inputs

Fictional or properly approved notes: client type, current products, stated goals, open issues.

## Steps

1. Use `01-prompt-basics/prompt.md`.
2. Keep facts separate from assumptions; mark gaps `[UNKNOWN: ...]`.
3. Suggest products only from the portfolio in `.agents/product-marketing-context.md`.

## Output

Brief with: situation, client goals, proposed agenda, products to discuss, questions to ask, risks.

## Guardrails

- Internal document. Do not paste it into client-facing material.
- No performance claims; no information about other clients.

## Used by

`01-prompt-basics`
