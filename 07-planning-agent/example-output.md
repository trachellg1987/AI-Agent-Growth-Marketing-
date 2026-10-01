# Example output: backward plan for new signed clients

> ILLUSTRATIVE: fictional target, base, rates and budget. The computed block is real
> output of the command shown; the explanation is a hand-written sample.

## Computed by code

<!-- computed: python 07-planning-agent/agent.py --target 20 --eligible 600 --funnel "reached:0.70,engaged:0.25,pilot:0.60,signed:0.30" --budget 120000 --weeks 12 --stats-only -->
````text
Target: 20 new signed clients in 12 weeks | eligible base: 600 | budget: $120,000
Funnel: reached 70% -> engaged 25% -> pilot 60% -> signed 30% | overall eligible-to-signed: 3.15%

stage         needed (backward)  supported (forward)  per week
eligible                    640                  600         -
reached                     448                  420      37.3
engaged                     112                  105       9.3
pilot                        67                   63       5.6
signed                       20                   18       1.7

Budget per signed client: $6,000
Budget per client at first stage (reached): $267.86

INFEASIBLE: the target needs 640 eligible clients but the base is 600; at these rates the base supports about 18 signed clients, not 20.
Options: lower the target to 18, widen the eligible base to 640, or lift the signed rate from 30% to 31.7% (other rates unchanged).
````

## Why this example is infeasible on purpose

Twenty signed clients need 640 eligible clients at these rates. The base is 600, which
supports about 18 (working forward and rounding down at each stage: 420 reached, 105
engaged, 63 pilots, 18 signed). The flag is the point of the demo: a planning agent should
say a target is not reachable before anyone commits to it.

## Sample model explanation

1. **Feasibility.** Infeasible as set. With 600 eligible clients and these rates, expect
   about 18 signed clients, not 20.
2. **Weekly activity.** About 37 clients reached, 9 engaged and 6 pilots started per week
   to stay on pace for the target.
3. **Options.**
   - Lower the target to 18: no new evidence needed.
   - Widen the base to 640: needs a defined, eligible extra segment.
   - Lift the signed rate from 30% to 31.7%: needs evidence from recent pilots that
     conversion can improve, for example a better pilot success-criteria template.
4. **Unknowns.** [UNKNOWN: whether the 30% pilot-to-signed rate holds for regional issuers]
   [UNKNOWN: account-manager capacity for 6 new pilots a week]
