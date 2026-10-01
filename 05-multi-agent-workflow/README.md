# 05 - Multi-agent workflow: Planner, Writer, Critic

Three chained model calls, each with one narrow job:

1. **Planner** turns a growth question into a plan (segment, personas, channels, pilot offer, measures).
2. **Writer** drafts an email and account-manager talking points from the plan.
3. **Critic** checks the draft for B2B risks and returns a revised draft.

The Critic checks:

- unsupported performance claims
- client confidentiality
- regional marketing-consent rules
- claims that need legal/compliance approval
- competitor disparagement

Nothing is sent to a client. The output is a draft for a human and legal/compliance to approve.

## Run

```bash
python 05-multi-agent-workflow/agent.py --dry-run   # print all three prompts, no API call
python 05-multi-agent-workflow/agent.py             # live run (three model calls)
python 05-multi-agent-workflow/agent.py --question "How do we raise adoption of the Dispute Management Tool among acquirers?"
```

By default the Planner and Critic read
[`.agents/product-marketing-context.md`](../.agents/product-marketing-context.md). Fill it in first.

## Why split the work

One prompt that plans, writes and reviews tends to approve its own draft. A separate Critic
with a fixed checklist catches more, and each step can be inspected on its own.

Related skills: [claims-review](../skills/claims-review/SKILL.md),
[consent-check](../skills/consent-check/SKILL.md), [pilot-proposal](../skills/pilot-proposal/SKILL.md).
