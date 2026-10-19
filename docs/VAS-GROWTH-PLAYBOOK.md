# VAS growth playbook: how this repo drives more conversions

ILLUSTRATIVE: this playbook uses fictional products, clients, pages and rates. Every number in a
computed block is real output of the command shown, re-checked by `make test`; every rate that goes
into those commands is an assumption to replace with real data. It describes an approach, not
results.

**The thesis in three sentences.** B2B Value Added Services (VAS) are bought over weeks or months,
by several people, through several channels, so conversion is not one moment but a chain of them.
Small, measured improvements at each link multiply. This repo gives a growth marketer one tested
tool per link, with the rule that **code does the math, AI drafts, and a human approves**.

## 1. How a VAS client buys

VAS clients are businesses: issuers (banks and credit unions), acquirers, merchants and fintechs.
The buyers are roles such as head of fraud/risk, head of cards/product, head of payments, and
procurement. A typical path, with the conversion that matters at each step:

| Stage | What the buyer does | The conversion | Where it leaks |
| --- | --- | --- | --- |
| 1. Discover | Searches Google or asks an AI assistant a problem question ("how do issuers reduce card-not-present fraud?") | Your page shows up and is cited | No page answers the question; AI answers name the problem but cite someone else |
| 2. Research | Reads product, use-case and comparison pages | Visitor clicks through and stays | Page is generic, slow, or answers a different question than the one asked |
| 3. Raise a hand | Requests a demo, workshop or assessment | Form submitted | The offer doesn't fit the client type; the form asks too much too soon |
| 4. Engage | Meets the account team, attends a webinar or workshop | A real conversation starts | Slow or generic follow-up; account manager lacks context |
| 5. Pilot | Tests the service with defined success criteria | Pilot starts | Success criteria are vague, so nobody knows what "worked" means |
| 6. Sign | Procurement, security and legal review | Contract signed | Long reviews with no proof pack ready |
| 7. Go live and expand | Turns the service on, adds products | Live client program; more programs per client | Signed but never activated; programs go inactive |

The repo's planning agent models stages 1 to 6 as a funnel (`reached -> engaged -> pilot -> signed`),
and the analysis agents cover stage 7 (live and inactive programs, attrition).

## 2. Why small lifts matter: the conversion math

Take a fictional goal: **20 new signed clients in 12 weeks** from **600 eligible clients** (for
example, regional issuers that don't yet use a product). With assumed stage rates, the plan
falls short:

<!-- computed: python 07-planning-agent/agent.py --target 20 --eligible 600 --funnel reached:0.70,engaged:0.25,pilot:0.60,signed:0.30 --budget 120000 --weeks 12 --stats-only -->
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

Now lift **one** stage, engaged, from 25% to 30% (better follow-up after first contact), and keep
everything else the same:

<!-- computed: python 07-planning-agent/agent.py --target 20 --eligible 600 --funnel reached:0.70,engaged:0.30,pilot:0.60,signed:0.30 --budget 120000 --weeks 12 --stats-only -->
````text
Target: 20 new signed clients in 12 weeks | eligible base: 600 | budget: $120,000
Funnel: reached 70% -> engaged 30% -> pilot 60% -> signed 30% | overall eligible-to-signed: 3.78%

stage         needed (backward)  supported (forward)  per week
eligible                    535                  600         -
reached                     374                  420      31.2
engaged                     112                  126       9.3
pilot                        67                   75       5.6
signed                       20                   22       1.7

Budget per signed client: $6,000
Budget per client at first stage (reached): $320.86

FEASIBLE: the eligible base supports 22 signed clients (target 20).
````

Same clients, same budget: the plan goes from **18 to 22 signed clients**. Running the same
command with other single changes, and then with all four at once:

| Scenario (other rates unchanged) | Overall eligible-to-signed | Signed clients the base supports |
| --- | --- | --- |
| Baseline | 3.15% | 18 |
| Reached 70% to 80% (found in search and AI answers) | 3.60% | 21 |
| Engaged 25% to 30% (faster, persona-matched follow-up) | 3.78% | 22 |
| Pilot 60% to 70% (better offer for each segment) | 3.67% | 21 |
| Signed 30% to 35% (pilots with agreed success criteria) | 3.67% | 22 |
| All four together | 5.88% | 35 |

The lesson is the last row. **Four modest lifts compound to nearly double the result**, because
each stage multiplies the next. That is why the approach below works stage by stage instead of
chasing one big campaign. The rates are assumptions; the point is the shape of the math, and the
agent recomputes it the moment real rates replace them.

## 3. Six growth levers, one per weak link

Each lever names the stage it moves, what I would do, the repo piece that does the heavy lifting,
why it raises conversion, and what I would measure.

### Lever 1: Be found where buyers research (stage 1, "reached")

**What I'd do.** Build a topical map for each priority product: one pillar page per topic and one
cluster page per real buyer question, all linked together. Log a set of buyer questions in AI
answer engines every week and track whether the product is named and its page cited.

**Repo piece.** [Agent 11](../11-search-visibility-agent/) and the
[search-visibility skill](../skills/search-visibility/SKILL.md):

```bash
python 11-search-visibility-agent/agent.py --stats-only
```

In the fictional sample, the product is named in 42% of AI answers but its pages are cited in only
22%, the head-of-cards question about fintech card programs has no page at all, two pages compete
for the same question, and two high-impression pages get less than half the site's click-through
rate. The agent ranks those into `CREATE PAGE` and `IMPROVE PAGE` actions and drafts outlines.
See the full output in [11-search-visibility-agent/example-output.md](../11-search-visibility-agent/example-output.md).

**Why it lifts conversion.** More of the research now starts in AI answers. A buyer who sees the
product cited as the source arrives already trusting it. Fixing structure helps search ranking
and AI citation at once, and a better title on a page that already gets impressions turns
existing visibility into visits without new spend.

**Measure.** Citation rate and share of voice by persona and engine (weekly), impressions and
click-through rate per page (Search Console), visits to demo-request pages from organic and AI
referrals.

### Lever 2: Make the page convert, by segment (stage 3, "raise a hand")

**What I'd do.** Test one offer against another on a product page, and read the result **by client
segment**, not just overall. Match each segment to the offer and message that wins for it.

**Repo piece.** [Agent 08](../08-ab-test-analyzer/) for the statistics, with
[persona-messaging](../skills/persona-messaging/SKILL.md) (agent 02) for the variants:

<!-- computed: python 08-ab-test-analyzer/agent.py --csv 08-ab-test-analyzer/sample-ab-results.csv --stats-only -->
````text
Metric: demo requests | A = ROI assessment offer | B = free pilot offer | alpha = 0.05
Per-segment p-values are Holm-adjusted across segments.

segment                       A rate          B rate  B-A (pts)      95% CI (pts)       p  p_holm  verdict
fintech_acquirers       20/400 5.00%   44/400 11.00%      +6.00    [+2.26, +9.74]  0.0018  0.0053  B better
regional_issuers        30/500 6.00%    33/500 6.60%      +0.60    [-2.41, +3.61]  0.6962  0.6962  no evidence of a difference
large_issuers          30/300 10.00%    12/300 4.00%      -6.00   [-10.05, -1.95]  0.0040  0.0080  A better
ALL (pooled)           80/1200 6.67%   89/1200 7.42%      +0.75    [-1.30, +2.80]  0.4727       -  no evidence of a difference

WARNING: segments disagree (B wins in at least one segment and loses in another). Do not roll out on the pooled result alone.
````

**Why it lifts conversion.** Overall, the test says "no difference," and a team reading only that
line would keep whichever offer it started with. By segment, the free pilot more than doubles demo
requests from fintechs and acquirers (5% to 11%), while large issuers prefer the ROI assessment (10% vs 4%).
Showing each segment its winning offer gets more demo requests from the **same traffic**.

**Measure.** Demo-request rate per page and segment; test velocity (tests completed per month);
the share of tests read by segment.

### Lever 3: Keep interested buyers moving (stage 4, "engaged")

**What I'd do.** Follow up within days, not weeks, after any signal: a webinar, a demo request, a
content download. Give each persona one idea and one next step per email, and give account managers
talking points from the same source so the handoff is warm.

**Repo piece.** [Agent 06](../06-content-repurposing/) turns one webinar into account-manager
talking points, a nurture email and a recap; [email-nurture](../skills/email-nurture/SKILL.md) drafts
the sequence; [consent-check](../skills/consent-check/SKILL.md) confirms who may be emailed in each
region before anything is sent.

**Why it lifts conversion.** In long B2B cycles, interest fades if nothing happens. Fast,
relevant follow-up is the cheapest way to raise the engaged rate, which section 2 shows is enough
on its own to turn a short plan into a feasible one. Automating the first draft is what makes "within
days" realistic across many products and regions.

**Measure.** Time from signal to first follow-up, reply and meeting rates by persona, share of
webinar attendees who reach a meeting within 30 days.

### Lever 4: Arm the account teams (stages 5 and 6, "pilot" and "signed")

**What I'd do.** Most VAS growth runs through existing relationships, so marketing's job here is to
make every client conversation better prepared. Before a meeting, a one-page brief; for a pilot, a
written proposal with success criteria the client agrees to up front.

**Repo piece.** [account-brief](../skills/account-brief/SKILL.md) (agent 01),
[pilot-proposal](../skills/pilot-proposal/SKILL.md), [campaign-brief](../skills/campaign-brief/SKILL.md)
(agent 03), and [agent 05](../05-multi-agent-workflow/), where a Planner, Writer and Critic chain drafts
outreach for a segment and the Critic removes unsupported claims.

**Why it lifts conversion.** A pilot with agreed success criteria has a built-in decision rule: if
the criteria are met, the next step is the contract, not another debate. Prepared account managers
also shorten the time between stages, which matters as much as the rates themselves.

**Measure.** Pilot-to-signed rate, days from pilot start to signature, share of pilots with written
success criteria.

### Lever 5: Grow inside existing clients (stage 7, "go live and expand")

**What I'd do.** Treat signed-but-inactive programs as the first growth target, before buying new
reach. Plan net growth after attrition, and fill it from the cheapest channels first.

**Repo piece.** [Agent 04](../04-tool-use-python/) summarizes live and inactive programs per product
(the model sees only counts, never client rows):

<!-- computed: python 04-tool-use-python/agent.py --stats-only -->
````text
Client programs: 12 rows across 12 clients | active 8 | inactive 4

vas_product                active inactive  total  active %
Analytics Dashboard             2        1      3       67%
Card Controls API               1        1      2       50%
Dispute Management Tool         2        1      3       67%
Risk Scoring Service            3        1      4       75%

Active programs by client type: acquirer 1, fintech 1, large_issuer 2, merchant 1, regional_issuer 3
Active programs by source: account_manager 4, email 1, webinar 1, workshop 2
````

[Agent 09](../09-vas-planning-agent/) then plans how many new programs a net-growth goal needs per
month and which channel is the costly marginal one.

**Why it lifts conversion.** A client who already signed has cleared procurement, security and
legal. Reactivating one inactive program is usually far cheaper than winning a new client, and every
reactivated program counts toward the same growth goal.

**Measure.** Active share per product, programs per client, monthly attrition, cost per new live
program by channel.

### Lever 6: Open the agent channel early (all stages)

**What I'd do.** Make product pages usable by AI agents doing research for buyers: a tool that
answers questions and a tool that submits a contact request, the pattern
[visapaymentsfrontier.io](https://webmcp.com/sites/visapaymentsfrontier.io) uses. Tag those leads
separately so their quality can be compared with human leads.

**Repo piece.** The agent-ready kit: [WEBMCP-EXPLAINED.md](WEBMCP-EXPLAINED.md),
[webmcp-skills/](../webmcp-skills/), [IMPLEMENTATION-GUIDE.md](../IMPLEMENTATION-GUIDE.md).

**Why it lifts conversion.** When an agent can read a structured answer and submit a lead in one
step, a whole research-and-form path collapses into one action. It is early, so I would run it as a
small, measured pilot rather than a bet.

**Measure.** Agent-sourced leads, their meeting and pilot rates against human leads.

## 4. Guardrails that make this safe at a payments company

Growth only counts if it is trusted. The repo builds these in:

- **Code does the math.** Rates, tests and plans are computed in Python and passed to the model in a
  `COMPUTED` block; the model never recomputes them.
- **No client data in models.** Agent 04 shares column names and counts only.
- **Claims are checked.** [claims-review](../skills/claims-review/SKILL.md) maps every number and
  promise to proof; missing proof becomes `[CLAIM NEEDS SUBSTANTIATION]`.
- **Consent by region.** [consent-check](../skills/consent-check/SKILL.md) runs before any send,
  which is what lets one approach scale across regional markets.
- **Agents are reviewed before launch.** [Agent 10](../10-agents-in-production/) runs ten static checks
  on any agent prompt, then a model review.
- **A human approves anything client-facing**, and legal/compliance approves any claim.

## 5. Measurement framework

One north-star metric, with stage metrics underneath it:

| Level | Metric | Cadence | Repo source |
| --- | --- | --- | --- |
| North star | New live client programs, net of attrition | Monthly | Agent 09, agent 04 |
| Discover | AI citation rate, share of voice, organic impressions and CTR | Weekly | Agent 11 |
| Raise a hand | Demo-request rate by page and segment | Per test | Agent 08 |
| Engage | Signal-to-follow-up time, meeting rate by persona | Weekly | Email and CRM reports |
| Pilot and sign | Pilot-to-signed rate, days to signature | Monthly | Agent 07 (re-plan with real rates) |
| Expand | Active share per product, programs per client | Monthly | Agent 04 |

Every month, the real stage rates go back into agent 07. That turns the plan from an assumption
into a forecast and shows which stage is now the weakest link.

## 6. A working week

| Day | Work | Repo piece | Stage it moves |
| --- | --- | --- | --- |
| Monday | Search and AI answer review; pick the week's page work | Agent 11 | Discover |
| Tuesday | Read the current page test by segment; set the next test | Agent 08, persona-messaging | Raise a hand |
| Wednesday | Launch content for one product, with claims and consent checks | Agents 02, 03, 05; claims-review; consent-check | Engage |
| Thursday | Turn the week's webinar into follow-ups; log new buyer questions for Monday | Agent 06, email-nurture | Engage, Discover |
| Friday | Update the plan with real rates; one-page report to leadership | Agents 07, 09, 04 | All |

## 7. First 90 days with this approach

- **Days 1 to 30, learn.** Map the real funnel for two priority products, get the actual stage
  rates, and put them into agent 07 to find the weakest link.
- **Days 31 to 60, test.** One lever per weak link: a topical map and answer log for one product
  (lever 1) and one segment-level page test (lever 2). Pilot one AI workflow with human approval.
- **Days 61 to 90, scale.** Keep what moved a stage rate, stop what didn't, re-run the plan, and set
  next quarter's test roadmap.

## 8. What this playbook does not claim

- It uses no real Visa data, products or results. The VAS portfolio names come only from public
  filings, as cited in [AGENT-LIBRARY.md](AGENT-LIBRARY.md).
- The stage rates are assumptions. Real lifts must come from real, measured tests.
- AI answer visibility changes from day to day; it is tracked as a trend, not a score.
