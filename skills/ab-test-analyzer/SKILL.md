---
name: ab-test-analyzer
description: Analyze an A/B offer test by client segment with a two-proportion z-test, Holm-adjusted segment p-values, and a segment-disagreement warning. Use when someone asks whether one offer beat another.
---

# A/B test analyzer

## When to use

An offer or message was tested on client contacts (for example "ROI assessment offer" vs
"free pilot offer") and someone asks which one won, overall or by client segment.

## Inputs

A CSV with `segment,variant,visitors,conversions`. `visitors` means contacts exposed to the
offer; `conversions` is the metric (for example demo requests). Variants are `A` and `B`.

## Steps

1. Run the script. Never compute statistics by hand or in the model:

   ```bash
   python skills/ab-test-analyzer/scripts/ab_stats.py --csv 08-ab-test-analyzer/sample-ab-results.csv
   ```

2. Read the verdict per segment. Segment p-values are Holm-adjusted, because testing
   several segments raises the chance of a false win.
3. If the script warns that segments disagree, do not decide on the pooled row.
4. Ask the model to explain the result and to label every explanation `HYPOTHESIS (untested)`.

## Output

A per-segment table (rates, difference in points, 95% CI, p, Holm p, verdict), a pooled row,
and a disagreement warning when it applies.

## Guardrails

- Small B2B samples: a "no evidence" verdict is not proof of no effect. Use
  `sample_size_per_variant()` to size the next test.
- Do not turn a test result into a client-facing performance claim without legal/compliance approval.

## Used by

`08-ab-test-analyzer`, `case-studies/01-offer-test-by-client-segment.md`
