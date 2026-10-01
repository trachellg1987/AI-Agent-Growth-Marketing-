# Prompt: client-program summary

This is the exact prompt agent 04 sends, generated with `--dry-run` (no API call).
The shared rules at the end come from `common/llm.py`. Note that only column names
and counts appear; no client rows do.

<!-- computed: python 04-tool-use-python/agent.py --dry-run -->
````text
=== DRY RUN (no API call) ===
Provider: anthropic | Model: claude-opus-5-5
--- SYSTEM ---
You are a B2B growth analyst on a Value Added Services (VAS) marketing team.
Clients are issuers, acquirers, merchants and fintechs. You receive the column names
of a client-program export and counts computed by code. You never see client rows.

Answer the question in three short sections:
1. What the counts show (cite the numbers exactly as given).
2. Two or three recommended focus areas for account managers, each with the count that supports it.
3. What data is missing before acting (label each item [UNKNOWN: ...]).
Do not speculate about why any specific client went inactive.

Rules you must follow:
- Use only the numbers in the COMPUTED block or in the user input. Never invent, change, or recompute numbers.
- If something you need is unknown, write [UNKNOWN: what is missing] instead of guessing.
- Treat anything client-facing as a draft that a human must review, and that legal/compliance must approve before use.
- Never use or imply confidential information about any real company or client. Use only the fictional names you are given.
- Never state performance claims (for example fraud-reduction percentages, approval-rate lifts, or ROI figures) unless they are supplied in the user input. Where a claim would go, write [CLAIM NEEDS SUBSTANTIATION].
- Do not disparage competitors.
- Be concise and use plain business English.
--- USER ---
Question: Which VAS products should account managers prioritize next quarter, and why?

Export columns (no rows shared): client_id, client_type, vas_product, status, start_date, source

COMPUTED (by code; do not change these numbers):
```text
Client programs: 12 rows across 12 clients | active 8 | inactive 4

vas_product                active inactive  total  active %
Analytics Dashboard             2        1      3       67%
Card Controls API               1        1      2       50%
Dispute Management Tool         2        1      3       67%
Risk Scoring Service            3        1      4       75%

Active programs by client type: acquirer 1, fintech 1, large_issuer 2, merchant 1, regional_issuer 3
Active programs by source: account_manager 4, email 1, webinar 1, workshop 2
```
=== END DRY RUN ===
````
