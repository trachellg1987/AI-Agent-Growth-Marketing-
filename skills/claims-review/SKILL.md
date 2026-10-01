---
name: claims-review
description: Find every claim in a draft (numbers, comparisons, promises), map each to its substantiation, and mark which need legal/compliance approval before use.
---

# Claims review

## When to use

Any client-facing draft before it goes to legal/compliance.

## Inputs

The draft, plus the "Proof you can honestly show" list from the context file.

## Steps

1. List every sentence that states or implies a result, comparison, or guarantee.
2. For each: substantiation source, or `[CLAIM NEEDS SUBSTANTIATION]`.
3. Flag comparisons that disparage competitors and anything that implies a real client.

## Output

A table: claim, type (figure / comparison / promise), source, action (keep / soften / remove / approve).

## Guardrails

- The reviewer never supplies a missing number. Missing proof means the claim comes out.

## Used by

`05-multi-agent-workflow` (Critic role)
