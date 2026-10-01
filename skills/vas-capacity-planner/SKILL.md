---
name: vas-capacity-planner
description: Plan new VAS client programs per month to hit a net growth target after monthly attrition, and fill the need from channels cheapest-first to find the costly marginal channel.
---

# VAS capacity planner

## When to use

A team wants to grow live client programs (one client live on one product) by a net amount
over a few months and needs to know the monthly volume and channel mix it implies.

## Inputs

- Live client programs today, net growth target, months
- Monthly attrition: share of live programs that deactivate or do not renew each month
- Channels as `name:monthly_contacts:conversion_to_signed:cost_per_contact`. For account
  managers, cost per contact is the loaded cost of one client conversation.

## Steps

1. Compute with `skills/vas-capacity-planner/scripts/capacity.py` (via agent 09).
2. Check the monthly need against total channel capacity (FEASIBLE / INFEASIBLE).
3. Look at the marginal channel: the most expensive channel still in use. That is where
   efficiency work pays off first.

## Output

Monthly need, month-by-month trajectory, channel allocation with cost, blended cost per new
program, marginal channel, feasibility line.

## Guardrails

- Every channel number is an assumption until replaced with your data. Say so.
- Results are expected values (fractional programs); present them as planning ranges.

## Used by

`09-vas-planning-agent`, `case-studies/02-backward-plan-live-client-programs.md`
