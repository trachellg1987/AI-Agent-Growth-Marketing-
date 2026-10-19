# A week in the life: AI-native growth marketing for B2B VAS

ILLUSTRATIVE: a sample week showing how this repo's agents and skills fit the everyday work of
a growth marketer on a B2B Value Added Services team. The products, pages, numbers and team
names are fictional. Real tools, processes and approvals would follow the employer's own rules.

The idea in one line: **agents do the counting and the first drafts, so the marketer spends the
week on judgment, partners and tests.** Every client-facing draft still goes to a human, and any
claim goes to legal/compliance.

## How VAS buyers are reached, and where the repo helps

| Channel | Who it reaches | Repo support |
| --- | --- | --- |
| Account teams (account-based marketing) | Existing clients: issuers, acquirers, merchants, fintechs | [account-brief](../skills/account-brief/SKILL.md), [persona-messaging](../skills/persona-messaging/SKILL.md), [pilot-proposal](../skills/pilot-proposal/SKILL.md) |
| Website: SEO, GEO/AEO, landing pages | Buyers researching on search engines and AI answer engines | [search-visibility](../skills/search-visibility/SKILL.md) (agent 11), [ab-test-analyzer](../skills/ab-test-analyzer/SKILL.md) (agent 08), the WebMCP kit |
| Email nurture (a marketing automation platform) | Contacts with marketing consent | [email-nurture](../skills/email-nurture/SKILL.md), [consent-check](../skills/consent-check/SKILL.md) |
| Webinars, events, thought leadership | Payments and fraud leaders | [webinar-follow-up](../skills/webinar-follow-up/SKILL.md), agent 06 |
| Planning and reporting | Leadership | [funnel-planner](../skills/funnel-planner/SKILL.md) (agent 07), [vas-capacity-planner](../skills/vas-capacity-planner/SKILL.md) (agent 09) |
| Guardrails for all of the above | Legal, compliance, brand | [claims-review](../skills/claims-review/SKILL.md), [agent-prompt-review](../skills/agent-prompt-review/SKILL.md) (agent 10) |

## Monday: search visibility review (SEO + GEO/AEO)

**Goal:** know where buyers can't find the product, and pick this week's page work.

1. Export last week's page impressions and clicks from Search Console into the topical map,
   and add last week's AI answer checks to the answer log.
2. Run the review:

   ```bash
   python 11-search-visibility-agent/agent.py --stats-only
   ```

3. Read it like this (sample numbers):
   - The product is **named in 42%** of AI answers but **cited in only 22%**: answer engines know
     the brand but don't treat its pages as the source. That points to page structure, not awareness.
   - The head-of-cards question about fintech card programs has **no page**: first `CREATE PAGE`.
   - Two pages answer the same risk-scoring question: merge them or point one to the other.
   - Two pages get high impressions but **low click-through**: set up a title and description test.
4. Run the agent without `--stats-only` to get draft outlines for the top three actions, then
   send them to the content owner.

**What this shows in the job:** search-everywhere optimization at scale, measurement that turns
into a ranked action list, and AI for the first draft with a human approving.

## Tuesday: landing page test readout

**Goal:** decide which offer to keep on a product landing page.

```bash
python 08-ab-test-analyzer/agent.py --csv 08-ab-test-analyzer/sample-ab-results.csv --stats-only
```

The sample shows the free pilot offer winning with fintechs and acquirers, losing with large
issuers, and no difference overall. **Deciding on the overall number would hide both effects.**
Next step: show each segment the offer that won for it, and size the next test properly.

**What this shows:** CRO and experimentation with real statistics, not gut feel.

## Wednesday: content for one launch, many channels

**Goal:** support the account teams and the nurture program for one product.

1. [persona-messaging](../skills/persona-messaging/SKILL.md): value propositions for the head of
   fraud, head of payments, head of cards and procurement (agent 02).
2. [campaign-brief](../skills/campaign-brief/SKILL.md): the brief, with its claims-approval checklist (agent 03).
3. [email-nurture](../skills/email-nurture/SKILL.md): a short sequence for consented contacts.
4. Before anything ships: [claims-review](../skills/claims-review/SKILL.md) maps every number and
   promise to proof, and [consent-check](../skills/consent-check/SKILL.md) confirms who may be emailed.
5. The new fintech page drafted on Monday becomes the nurture email's destination.

**What this shows:** content at scale, partnering with product marketing and regional teams, and
working within a regulated company's rules.

## Thursday: after a client webinar

**Goal:** turn one webinar into follow-ups by audience.

[Agent 06](../06-content-repurposing/) turns the webinar summary into account-manager talking
points, a nurture email and an internal recap. The questions attendees asked are logged as new
buyer questions for Monday's answer log, so next week's review checks whether the site answers them.

**What this shows:** a closed loop between events, content and search.

## Friday: plan and report

**Goal:** a one-page update for leadership and next week's priorities.

```bash
python 09-vas-planning-agent/agent.py --current-active 300 --target-net 100 --months 6 --monthly-churn 0.01 --channels "email_nurture:3000:0.001:0.5,account_manager:120:0.08:150,webinar:600:0.01:20,workshop:25:0.2:2000" --stats-only
```

The planning agent shows how many new client programs a growth goal needs each month and which
channel is the most expensive one still in use. That is where efficiency work pays off first. The
update pairs it with the week's search and test results.

**What this shows:** measurement frameworks and dashboards that turn into business recommendations,
and prioritizing a portfolio of growth initiatives.

## The weekly loop

```text
Monday     measure search and AI answer visibility   -> pick page work
Tuesday    read test results by segment               -> keep, change, or retest
Wednesday  draft content for one launch               -> claims and consent checks
Thursday   turn events into follow-ups                -> new buyer questions for Monday
Friday     plan and report                            -> next week's priorities
```

## Ground rules that carry over to any team

- **Code does the math, the model explains, a human approves.**
- AI answer visibility moves week to week; track trends, not single checks.
- No performance claim without substantiation and legal/compliance approval.
- Use only fictional or approved data in prompts; never paste client data into a model.
