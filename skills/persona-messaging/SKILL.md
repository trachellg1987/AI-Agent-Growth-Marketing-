---
name: persona-messaging
description: Write value propositions for one VAS product per buyer persona (head of fraud/risk, head of cards/product, head of payments, procurement) and client type, grounded in the product-marketing context file.
---

# Persona messaging

## When to use

You need different messages for different buyers of the same product.

## Inputs

`.agents/product-marketing-context.md` (filled in), product name, client type, personas.

## Steps

1. Use `02-context-engineering/prompt.md` with the context file attached.
2. One message per persona: their problem, what changes for them, proof you can honestly show.
3. Where proof is missing, write `[CLAIM NEEDS SUBSTANTIATION]`.

## Output

A table: persona, pain point, value proposition, proof point, call to action.

## Guardrails

- Only claims listed under "Proof you can honestly show" in the context file.

## Used by

`02-context-engineering`
