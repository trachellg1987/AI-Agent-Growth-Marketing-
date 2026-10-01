# Example output: client-program summary

> ILLUSTRATIVE: fictional clients and products. The computed block is real output of
> the command shown; the explanation is a hand-written sample of the expected shape.

## Computed by code

<!-- computed: python 04-tool-use-python/agent.py --stats-only -->
````text
Client programs: 12 rows across 12 clients | active 8 | inactive 4

vas_product                active inactive  total  active %
Analytics Dashboard             2        1      3       67%
Card Controls API               1        1      2       50%
Dispute Management Tool         2        1      3       67%
Risk Scoring Service            3        1      4       75%

Active programs by client type: acquirer 1, fintech 1, large_issuer 2, merchant 1, regional_issuer 3
Active programs by source: account_manager 4, email 1, webinar 1, workshop 2
````

## Sample model explanation

1. **What the counts show.** 8 of 12 programs are active. Risk Scoring Service has the most
   active programs (3 of 4, 75%). Card Controls API is at 1 of 2 (50%). Regional issuers hold
   the most active programs (3). Account-manager-sourced programs are the largest group (4).
2. **Focus areas.**
   - Risk Scoring Service with regional issuers: the strongest base (3 active), worth
     expanding with similar clients.
   - Card Controls API: the lowest active share (50%); find out why one program went inactive
     before investing in acquisition.
   - Account-manager and workshop sources account for 6 of 8 active programs; prioritize those
     motions over email (1) and webinar (1).
3. **Missing before acting.**
   - [UNKNOWN: how many eligible clients do not have each product yet]
   - [UNKNOWN: reasons programs went inactive]
   - [UNKNOWN: program value; counts treat every program as equal]
