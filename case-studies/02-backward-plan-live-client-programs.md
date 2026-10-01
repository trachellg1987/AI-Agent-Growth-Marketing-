# Case study 02: backward plan for live client programs

> ILLUSTRATIVE: fictional program counts, attrition and channel assumptions. The computed
> block is real output of agent 09. Not a real result.

## The question

"We have 300 live client programs. Leadership wants 400 in six months. What does that take,
and where will the money go?"

## Data (fictional)

- 300 live client programs today; goal +100 net in 6 months
- 1% monthly attrition (clients that deactivate or do not renew)
- Four channels with assumed monthly reach, conversion to signed client, and loaded cost per
  contact. Account managers at $150, the assumed loaded cost of one client conversation.

## What the code computed

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

## What the model explained

- +100 net means about 120 new programs, because about 20 replace programs lost to attrition.
- Email nurture, account managers and webinars run at full capacity. Workshops are the
  costly marginal channel: $10,000 per new program, against a blended $2,309.
- The cheapest way to cut cost is not a new channel. It is moving the last 1.49 programs a
  month out of workshops, by lifting webinar conversion or adding account-manager capacity.
- Every channel number is an assumption until replaced with measured data.

## Decision and human sign-off

- The plan was accepted as a planning range, not a commitment.
- Before budgeting, the team agreed to measure real account-manager conversation cost and
  per-channel conversion for one quarter.

## What we would do differently

- Use attrition per product instead of one blended rate.
- Model account-manager capacity in hours, not contacts.
