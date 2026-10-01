# Example output: Planner, Writer, Critic

> ILLUSTRATIVE: fictional product and segment, hand-written sample output showing the
> expected shape of a live run. No numbers are computed in this agent; see
> [prompt.md](prompt.md) for the real prompts.

Question: How should we raise adoption of the Risk Scoring Service among regional issuers next quarter?

## Plan (Planner)

- Goal: more regional issuers agree a pilot of the Risk Scoring Service. Target: [UNKNOWN: no target in context].
- Segment: regional issuers without the product.
- Personas: head of fraud/risk (primary), head of cards/product, procurement.
- Channels: account-manager conversations, then a client webinar, then email nurture to attendees with consent, then scoping workshops.
- Offer: a pilot with success criteria agreed with each client.
- Measures: pilots agreed, pilots converted to contracts.

## Draft (Writer)

Email, head of fraud/risk:

> Subject: Scoring risk without rebuilding your fraud stack
>
> Regional issuers tell us fraud screening and approving good transactions pull in opposite
> directions. The Risk Scoring Service adds a risk score to authorization decisions, and it
> reduces fraud losses by 30%. Unlike other vendors, it is easy to set up. Reply to book a
> 30-minute scoping call with your account manager.

## Critic review

| Check | Result | Line |
| --- | --- | --- |
| Unsupported performance claims | FIX | "reduces fraud losses by 30%" is not in the context file |
| Client confidentiality | PASS | No client named or implied |
| Regional marketing-consent rules | FIX | Audience must be limited to contacts with consent or a contract basis |
| Claims needing legal/compliance approval | FIX | "easy to set up" needs substantiation |
| Competitor disparagement | FIX | "Unlike other vendors" |

Revised draft:

> Subject: Scoring risk without rebuilding your fraud stack
>
> Regional issuers tell us fraud screening and approving good transactions pull in opposite
> directions. The Risk Scoring Service adds a risk score to authorization decisions.
> [CLAIM NEEDS SUBSTANTIATION] A pilot lets you measure results on your own data against
> criteria you set. Reply to book a 30-minute scoping call with your account manager.

Requires human and legal/compliance approval before use.
