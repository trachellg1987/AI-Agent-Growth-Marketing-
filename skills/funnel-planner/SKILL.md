---
name: funnel-planner
description: Work backward from a target of new signed clients through reached, engaged, pilot and signed stages, check it against the eligible client base, and flag infeasible targets.
---

# Funnel planner

## When to use

Someone sets a target such as "20 new signed clients this quarter" and needs the weekly
activity it implies, or wants to know whether the target is realistic.

## Inputs

- Target (new signed clients), eligible client base, budget, weeks
- Funnel as ordered `name:rate` pairs, each rate a share of the previous stage

## Steps

1. Compute with `skills/funnel-planner/scripts/funnel.py` (via agent 07 or directly).
2. Backward pass rounds up (you cannot pilot 0.7 of a bank); forward pass rounds down.
3. Read the FEASIBLE / INFEASIBLE line before anything else.
4. If infeasible, compare the three levers the script prints: lower the target, widen the
   base, or lift the last-stage rate. Each needs evidence; none is free.

## Output

Stage table (needed vs supported, per week), budget per signed client, feasibility line, options.

## Guardrails

- Rates must come from your pipeline history (`.agents/growth-metrics-context.md`), not guesses.
- The model may explain options; it must not invent new rates.

## Used by

`07-planning-agent`
