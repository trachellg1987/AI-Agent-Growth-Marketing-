# 02 - Context engineering: persona messaging from a context file

A prompt is only as good as the facts it can see. This agent attaches
[`.agents/product-marketing-context.md`](../.agents/product-marketing-context.md) to the
prompt, so messaging is grounded in your portfolio, personas and approved proof instead of
the model's general knowledge.

## How to use

1. Fill in the `[FILL IN]` fields of the context file.
2. Paste [prompt.md](prompt.md) into your model and attach the context file.
3. Name one product and one client type.

## What it teaches

- Separating stable context (a file you maintain) from the task (a short prompt).
- Telling the model what to do when the context is incomplete.
- Keeping proof points honest: if a claim is not in the context file, it is not in the copy.

Related skill: [persona-messaging](../skills/persona-messaging/SKILL.md).
