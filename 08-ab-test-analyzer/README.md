# 08 - A/B test analyzer: offer test by client segment

An offer test across three client segments: **A = ROI assessment offer**,
**B = free pilot offer**. The metric is demo requests.

Statistics come from [`skills/ab-test-analyzer/scripts/ab_stats.py`](../skills/ab-test-analyzer/scripts/ab_stats.py),
the single source of truth. The model only explains the computed results and must label
every explanation as an untested hypothesis.

## Run

```bash
python 08-ab-test-analyzer/agent.py --csv 08-ab-test-analyzer/sample-ab-results.csv --stats-only
python 08-ab-test-analyzer/agent.py --dry-run
make run AGENT=08-ab-test-analyzer ARGS="--csv 08-ab-test-analyzer/sample-ab-results.csv --stats-only"
```

## Input

[sample-ab-results.csv](sample-ab-results.csv) (fictional):

| Column | Meaning |
| --- | --- |
| `segment` | `fintech_acquirers`, `regional_issuers`, `large_issuers` |
| `variant` | `A` (ROI assessment offer) or `B` (free pilot offer) |
| `visitors` | Client contacts exposed to the offer (not website visitors) |
| `conversions` | Demo requests |

## What the sample shows

The free pilot wins with fintechs and acquirers, loses with large issuers, and shows no
evidence of a difference with regional issuers. Pooled, the effects cancel out, so the
overall result says "no evidence of a difference". Deciding on the pooled number alone would
hide both real effects. The agent warns when segments disagree.

Related skill: [ab-test-analyzer](../skills/ab-test-analyzer/SKILL.md). Case study:
[01-offer-test-by-client-segment](../case-studies/01-offer-test-by-client-segment.md).
