# Example output: offer test by client segment

> ILLUSTRATIVE: fictional segments and counts. The computed block is real output of the
> command shown; the explanation is a hand-written sample of the expected shape.

## Computed by code

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

## Sample model explanation

1. **Per segment.**
   - fintech_acquirers: B better. The free pilot offer drew more demo requests.
   - regional_issuers: no evidence of a difference.
   - large_issuers: A better. The ROI assessment offer drew more demo requests.
2. **Pooled result.** "No evidence of a difference" overall, because the two significant
   effects point in opposite directions and cancel out. It is not a safe basis for a decision.
3. **Possible explanations.**
   - HYPOTHESIS (untested): fintechs and acquirers decide quickly and can start a pilot with
     little internal process, so a free pilot lowers the barrier. Test: time from demo request
     to pilot start by segment.
   - HYPOTHESIS (untested): at large issuers, a "free pilot" still triggers procurement and
     security review, so it reads as more work than an ROI assessment. Test: ask account
     managers how many B-variant demo requests stalled in procurement.
   - HYPOTHESIS (untested): regional issuers may respond to both offers equally, or the sample
     is too small to see a difference. Test: size the next test with `sample_size_per_variant()`.
4. **Next steps (each needs human sign-off).**
   - fintech_acquirers: lead with the free pilot offer.
   - large_issuers: keep the ROI assessment offer.
   - regional_issuers: keep testing with a larger sample.
