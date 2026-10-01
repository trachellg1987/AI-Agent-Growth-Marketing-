# Design decisions

A one-page explanation of how this repo is built and why.

## 1. Code does the math, the model explains

Language models are good at explaining, prioritizing and drafting. They are unreliable at
arithmetic and statistics, and they can produce a confident wrong number. So every number
is computed in plain Python (the skill scripts in `skills/*/scripts/`) and handed to the
model in a block labeled `COMPUTED (by code; do not change these numbers)`. The shared rules
tell the model to use only those numbers. If a figure in an output is wrong, the bug is in
code that has unit tests, not in a prompt.

Example: agent 08 never asks the model whether the free pilot offer won. `ab_stats.py`
runs the z-test, the Holm adjustment and the segment-disagreement check; the model explains
what the verdicts mean.

## 2. Unknowns are labeled instead of guessed

When information is missing, a model tends to fill the gap with something plausible. In
client-facing B2B work, a plausible but invented fact is worse than a gap. Every prompt
says: write `[UNKNOWN: what is missing]`, and for missing proof, `[CLAIM NEEDS
SUBSTANTIATION]`. The context templates keep `[FILL IN]` placeholders for the same reason:
an unfilled field is visible, not silently invented.

## 3. A human approves anything client-facing

Clients are banks, acquirers, merchants and fintechs. A wrong claim, a breach of client
confidentiality, or an email to someone without marketing consent creates real legal and
relationship risk. So the agents only draft. Agent 05's Critic and agent 10's static checks
catch common problems early, but the last step is always a person, plus legal/compliance
for any claim. No agent in this repo sends anything.

## 4. How dry-run mode works

Every Python agent has `--dry-run`. It builds the full prompt (task, shared rules, computed
block) exactly as a live run would, prints it, and stops before any network call. This lets
you inspect what would be sent, including that no client rows are in it, and it lets the
tests run without an API key. The `prompt.md` files for the Python agents are dry-run output,
so the documentation cannot drift from the code.

## 5. How the repo is tested without calling a model

- `make validate`: structure, ILLUSTRATIVE labels, skill metadata, placeholders, off-topic
  (non-B2B) terms, secrets.
- `make unit`: unit tests for the statistics, planning math, summaries and prompt checks.
- `make examples`: re-runs every command behind a computed block in the docs and fails if the
  output changed. Numbers in the docs are never hand-typed.
- `make smoke`: runs every agent offline and checks exit codes and key output, including
  that a missing API key gives a one-line message, not a traceback.
- `make test-api`: starts a local fake server that answers like the Anthropic and OpenAI
  APIs, points the official SDKs at it, and checks the contract: the model text is printed,
  the prompt includes the computed block, agent 04 sends column names but no rows, and agent
  05 makes three chained calls.
