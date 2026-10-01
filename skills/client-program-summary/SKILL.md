---
name: client-program-summary
description: Count live and inactive client programs per VAS product from a CSV export and share only column names and aggregates with a model, never client rows.
---

# Client program summary

## When to use

You have a client-program export and want a model's view on where account managers should
focus, without sending client-level data to the model.

## Inputs

CSV with `client_id, client_type, vas_product, status, start_date, source`.
`status` is `active` or `inactive`; `source` is `account_manager`, `webinar`, `email`, or `workshop`.

## Steps

1. Load and validate with `skills/client-program-summary/scripts/program_summary.py`.
2. Aggregate: active/inactive per product, active by client type, active by source.
3. Send the model the column names and the aggregates only.

## Output

A product table plus active counts by client type and by source.

## Guardrails

- Never paste client rows into a prompt. Aggregates only.
- Keep real exports out of git (`data/` and `*.local.csv` are git-ignored).

## Used by

`04-tool-use-python`
