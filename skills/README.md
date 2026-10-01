# Skills

A skill is a reusable, documented procedure. Agents are command-line tools that use skills.
When a skill involves math, the math lives in the skill's `scripts/` folder, in one place,
and agents load it from there. Statistics are never reimplemented elsewhere.

| Skill | What it does | Has a script | Used by |
| --- | --- | --- | --- |
| [ab-test-analyzer](ab-test-analyzer/SKILL.md) | A/B offer test by client segment | yes | 08, case study 01 |
| [account-brief](account-brief/SKILL.md) | Client meeting brief from notes | no | 01 |
| [agent-prompt-review](agent-prompt-review/SKILL.md) | Pre-launch review of an agent prompt | yes | 10 |
| [campaign-brief](campaign-brief/SKILL.md) | Campaign brief with claims-approval checklist | no | 03 |
| [claims-review](claims-review/SKILL.md) | Map claims to substantiation | no | 05 |
| [client-program-summary](client-program-summary/SKILL.md) | Live vs inactive programs per product | yes | 04 |
| [consent-check](consent-check/SKILL.md) | Regional marketing-consent check | no | 03, 05 |
| [email-nurture](email-nurture/SKILL.md) | B2B nurture sequence | no | 06 |
| [funnel-planner](funnel-planner/SKILL.md) | Backward plan for new signed clients | yes | 07 |
| [persona-messaging](persona-messaging/SKILL.md) | Value propositions per buyer persona | no | 02 |
| [pilot-proposal](pilot-proposal/SKILL.md) | Pilot outline with success criteria | no | 05 |
| [vas-capacity-planner](vas-capacity-planner/SKILL.md) | Net growth of live client programs | yes | 09, case study 02 |
| [webinar-follow-up](webinar-follow-up/SKILL.md) | Follow-ups from a client webinar | no | 06 |

New skill: copy [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md).
