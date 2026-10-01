# Example output: grow live client programs net of attrition

> ILLUSTRATIVE: fictional programs, attrition and channel assumptions. The computed block
> is real output of the command shown; the explanation is a hand-written sample.

## Computed by code

<!-- computed: python 09-vas-planning-agent/agent.py --current-active 300 --target-net 100 --months 6 --monthly-churn 0.01 --channels "email_nurture:3000:0.001:0.5,account_manager:120:0.08:150,webinar:600:0.01:20,workshop:25:0.2:2000" --stats-only -->
````text
Live client programs: 300 now -> 400 goal (+100 net) in 6 months
Monthly attrition (deactivate or do not renew): 1.0%

New signed client programs needed per month: 20.09
Total new programs over 6 months: 120.5 (of which 20.5 replace programs lost to attrition)

month  lost  live at month end
    1   3.0              317.1
    2   3.2              334.0
    3   3.3              350.8
    4   3.5              367.3
    5   3.7              383.7
    6   3.8              400.0

Channels, cheapest cost per signed client first:
channel           cost/client  capacity/mo  planned/mo  contacts/mo    cost/mo   used
email_nurture            $500          3.0        3.00         3000     $1,500   100%
account_manager        $1,875          9.6        9.60          120    $18,000   100%
webinar                $2,000          6.0        6.00          600    $12,000   100%
workshop              $10,000          5.0        1.49            7    $14,882    30%

Total channel capacity: 23.6 programs/month vs 20.09 needed
Planned cost: $46,382/month, $278,293 over 6 months, blended $2,309 per new program
Marginal (most costly) channel in use: workshop at $10,000 per client, 1.49 programs/month
FEASIBLE within current channel capacity.
````

## Sample model explanation

1. **Headline.** About 20 new client programs a month for 6 months. Roughly 100 of the
   120.5 total are net growth; about 20.5 replace programs lost to 1% monthly attrition.
2. **Channel plan.** Email nurture, account managers and webinars run at full capacity.
   Workshops are the costly marginal channel at $10,000 per client and cover the last
   1.49 programs a month, about $14,882 of the $46,382 monthly cost. Raising webinar
   conversion or account-manager capacity would cut workshop use first.
3. **Assumptions to replace.** [UNKNOWN: real loaded cost of an account-manager conversation]
   [UNKNOWN: measured conversion to signed client per channel]
   [UNKNOWN: attrition by product; 1% is one blended rate]
