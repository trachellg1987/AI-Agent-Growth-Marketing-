# 07 - Planning agent: backward plan for new signed clients

Start from a target ("20 new signed clients in 12 weeks") and work backward through the
pipeline (reached, engaged, pilot, signed) to the weekly activity it needs. Then work forward
from the eligible client base to check whether the target is even possible.

## Run

```bash
python 07-planning-agent/agent.py --target 20 --eligible 600 \
  --funnel "reached:0.70,engaged:0.25,pilot:0.60,signed:0.30" \
  --budget 120000 --weeks 12 --stats-only
```

Drop `--stats-only` for a live run, or use `--dry-run` to see the prompt.

## Inputs

| Argument | Meaning |
| --- | --- |
| `--target` | New signed clients wanted |
| `--eligible` | Eligible clients in scope (for example regional issuers without the product) |
| `--funnel` | Ordered `stage:rate`; each rate is a share of the previous stage, the first is a share of the eligible base |
| `--budget` | Marketing budget in dollars |
| `--weeks` | Planning horizon |

## The feasibility flag

The example deliberately asks for more than the base supports: 600 eligible clients at
these rates support about 18 signed clients, not 20. The agent says so and lists the three
levers (lower the target, widen the base, lift a rate) instead of producing a plan that
cannot work. See [example-output.md](example-output.md).

Related skill: [funnel-planner](../skills/funnel-planner/SKILL.md).
