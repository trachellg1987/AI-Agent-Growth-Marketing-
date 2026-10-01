# 09 - VAS planning agent: grow live client programs net of attrition

A live client program is one client live on one VAS product. To grow live programs by a
net amount, you must also replace programs lost to attrition (clients that deactivate or do
not renew). This agent works out the new programs needed each month, then fills that need
from channels in order of cost per signed client, cheapest first.

## Run

```bash
python 09-vas-planning-agent/agent.py --current-active 300 --target-net 100 --months 6 \
  --monthly-churn 0.01 \
  --channels "email_nurture:3000:0.001:0.5,account_manager:120:0.08:150,webinar:600:0.01:20,workshop:25:0.2:2000" \
  --stats-only
```

## Inputs

| Argument | Meaning |
| --- | --- |
| `--current-active` | Live client programs today |
| `--target-net` | Net new live client programs wanted by the end of the horizon |
| `--months` | Horizon in months |
| `--monthly-churn` | Monthly attrition: share of live programs that deactivate or do not renew each month |
| `--channels` | `name:monthly_contacts:conversion_to_signed:cost_per_contact`, comma-separated |

For account managers, `cost_per_contact` is the loaded cost of one client conversation
(salary, overhead, travel). The sample uses $150; it is an assumption you replace.

## Reading the result

The **marginal channel** is the most expensive channel still needed. In the example,
email nurture, account managers and webinars run at full capacity, and the last
1.49 programs per month come from workshops at $10,000 per client. That is the first place
to look for efficiency: every program shifted from workshops to a cheaper channel saves the
most. See [example-output.md](example-output.md).

Related skill: [vas-capacity-planner](../skills/vas-capacity-planner/SKILL.md). Case study:
[02-backward-plan-live-client-programs](../case-studies/02-backward-plan-live-client-programs.md).
