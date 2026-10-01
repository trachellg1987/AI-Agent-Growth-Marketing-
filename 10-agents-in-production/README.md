# 10 - Agents in production: review an agent prompt before launch

Before an agent drafts or sends anything client-facing, review its prompt.

1. **Static checks (code):** ten repeatable regex checks, each PASS or FLAG.
2. **Model review:** a deeper review for risks regex cannot see. It uses the static
   results as evidence and returns a risk table plus a rewritten prompt.

## Run

```bash
python 10-agents-in-production/agent.py --static-only                   # code checks only
python 10-agents-in-production/agent.py --dry-run                       # show the review prompt
python 10-agents-in-production/agent.py --prompt-file path/to/prompt.md # live review
```

## The sample prompt

[sample-agent-prompt.md](sample-agent-prompt.md) is deliberately weak. It promises a
specific fraud-reduction percentage, disparages competitors, pulls contact lists and
incident notes from a CRM, sends to everyone, and has no approval step. It passes 1 of 10
static checks.

## Static checks

| Check | Flags when |
| --- | --- |
| Human approval step | No human review or approval before sending |
| No hard-coded performance claims | The prompt promises a specific result (for example "cut fraud losses by 40%") |
| No competitor disparagement | The prompt attacks competitors |
| No sensitive client data pulled | Incident or fraud-case notes, or full CRM exports |
| Confidentiality / client-data rule | The prompt never mentions client confidentiality or data handling |
| Claims need substantiation/approval | The prompt never requires claims to be substantiated or approved |
| Recipient scope and marketing consent | Sends to everyone, or no consent/opt-out rule |
| No secrets in prompt | API keys or passwords in the text |
| Unknowns are labeled | No instruction for missing information |
| Output format defined | No defined output format |

Related skill: [agent-prompt-review](../skills/agent-prompt-review/SKILL.md).
