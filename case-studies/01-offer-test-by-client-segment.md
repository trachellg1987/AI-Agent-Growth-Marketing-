# Case study 01: offer test by client segment

> ILLUSTRATIVE: fictional segments, offers and counts. The computed block is real output
> of agent 08 on fictional sample data. Not a real result.

## The question

"Our free pilot offer did not beat the ROI assessment offer overall. Should we drop it?"

## Data (fictional)

[08-ab-test-analyzer/sample-ab-results.csv](../08-ab-test-analyzer/sample-ab-results.csv):
contacts exposed to each offer and the demo requests they made, across three client
segments. A = ROI assessment offer, B = free pilot offer.

## What the code computed

<!-- computed: python 08-ab-test-analyzer/agent.py --csv 08-ab-test-analyzer/sample-ab-results.csv --stats-only -->
````text
Metric: demo requests | A = ROI assessment offer | B = free pilot offer | alpha = 0.05
Per-segment p-values are Holm-adjusted across segments.

segment                       A rate          B rate  B-A (pts)      95% CI (pts)       p  p_holm  verdict
fintech_acquirers       20/400 5.00%   44/400 11.00%      +6.00    [+2.26, +9.74]  0.0018  0.0053  B better
regional_issuers        30/500 6.00%    33/500 6.60%      +0.60    [-2.41, +3.61]  0.6962  0.6962  no evidence of a difference
large_issuers          30/300 10.00%    12/300 4.00%      -6.00   [-10.05, -1.95]  0.0040  0.0080  A better
ALL (pooled)           80/1200 6.67%   89/1200 7.42%      +0.75    [-1.30, +2.80]  0.4727       -  no evidence of a difference

WARNING: segments disagree (B wins in at least one segment and loses in another). Do not roll out on the pooled result alone.
````

## What the model explained

- The pooled row says "no evidence of a difference", but that hides two real, opposite effects.
- The free pilot drew more demo requests from fintechs and acquirers, and fewer from large issuers.
- HYPOTHESIS (untested): large issuers treat any pilot as a procurement and security-review
  project, so "free pilot" reads as more work, not less.
- HYPOTHESIS (untested): fintechs and acquirers can start a pilot quickly, so a free pilot
  removes their main barrier.
- Regional issuers: no evidence either way. The next test needs a larger sample.

## Decision and human sign-off

- Fintech and acquirer campaigns lead with the free pilot offer.
- Large-issuer campaigns keep the ROI assessment offer.
- Regional issuers: keep testing.
- The marketing lead approved the segment split. Any client-facing description of these
  results needs legal/compliance approval, and none of it is a performance claim.

## What we would do differently

- Agree the segments and the analysis before launch, so the split is not found after the fact.
- Track what happens after the demo request (pilot started, contract signed), not just the
  request itself.
