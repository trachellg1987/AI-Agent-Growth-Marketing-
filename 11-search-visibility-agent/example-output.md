# Example output: search-visibility review

> ILLUSTRATIVE: fictional pages, Search Console numbers and AI answer checks. The computed
> block is real output of the command shown; the drafts are a hand-written sample of the
> expected shape.

## Computed by code

<!-- computed: python 11-search-visibility-agent/agent.py --stats-only -->
````text
SEO: topical map
  card-not-present fraud: pillar /risk/card-not-present-fraud, 4 cluster page(s)
  disputes and chargebacks: pillar /acceptance/dispute-management, 1 cluster page(s)
  Structure issues (9):
    - /risk/fraud-tool-roi does not link up to its pillar /risk/card-not-present-fraud
    - pillar /risk/card-not-present-fraud does not link down to /risk/fraud-tool-roi
    - /risk/fraud-tool-roi is an orphan page (no internal links point to it)
    - /insights/what-is-risk-scoring does not link up to its pillar /risk/card-not-present-fraud
    - pillar /risk/card-not-present-fraud does not link down to /insights/what-is-risk-scoring
    - /insights/what-is-risk-scoring is an orphan page (no internal links point to it)
    - pillar /acceptance/dispute-management does not link down to /acceptance/chargeback-reason-codes
    - /acceptance/chargeback-reason-codes is an orphan page (no internal links point to it)
    - /risk/real-time-risk-scoring and /insights/what-is-risk-scoring target the same question and compete with each other
  Site click-through rate from search: 2.7%
  High impressions, low click-through (test a new title and description):
    - /acceptance/chargeback-reason-codes: 3,100 impressions, 34 clicks, 1.1% CTR
    - /risk/false-declines: 2,600 impressions, 31 clicks, 1.2% CTR

GEO/AEO: AI answer visibility (2026-10-05 to 2026-10-12)
  36 answer checks | brand named in 42% | our page cited in 22% | share of voice 17%
  By engine:
    chatgpt             checks  12  named  58%  cited  33%
    google_ai_overview  checks  12  named  25%  cited  17%
    perplexity          checks  12  named  42%  cited  17%
  By persona:
    head_of_cards     checks   6  named   0%  cited   0%
    head_of_fraud     checks  12  named  75%  cited  50%
    head_of_payments  checks  12  named  42%  cited  17%
    procurement       checks   6  named  17%  cited   0%

Actions by buyer question (cited threshold 50%; under 5 checks = directional only):
  1. CREATE PAGE: "Which fraud tools fit fintechs launching card programs?"
     persona head_of_cards | page [none] | named 0/6, cited 0/6
  2. IMPROVE PAGE: "How do you measure the ROI of a fraud tool?"
     persona procurement | page /risk/fraud-tool-roi | named 1/6, cited 0/6
  3. IMPROVE PAGE: "How can acquirers reduce the cost of handling chargebacks?"
     persona head_of_payments | page /acceptance/dispute-management | named 2/6, cited 1/6
  4. IMPROVE PAGE: "How can issuers cut false declines without raising fraud losses?"
     persona head_of_payments | page /risk/false-declines | named 3/6, cited 1/6
  5. IMPROVE PAGE: "What is real-time transaction risk scoring?"
     persona head_of_fraud | page /risk/real-time-risk-scoring | named 4/6, cited 2/6
  6. MAINTAIN: "How do issuers reduce card-not-present fraud?"
     persona head_of_fraud | page /risk/card-not-present-fraud | named 5/6, cited 4/6

Note: AI answers change from day to day and by account. Treat rates as trends to track over weeks, not as fixed scores.
````

## Sample model drafts

1. **Summary for my manager.**
   - Biggest gap: the head-of-cards question about fintech card programs has no page, and AI
     answers never name us for it (0 of 6 checks).
   - Biggest quick win: fix the internal links and the two competing risk-scoring pages. It is
     a few hours of work and helps both search ranking and AI citation.
   - Track next: citation rate for the five `IMPROVE PAGE` questions, weekly, by engine.

2. **CREATE PAGE: "Which fraud tools fit fintechs launching card programs?"**
   - H1: Which fraud tools fit fintechs launching card programs?
   - Answer at the top (draft): "Fintechs launching card programs usually need fraud tools that
     connect through an API, score transactions in real time, and scale with volume.
     [UNKNOWN: which of our Risk Scoring Service features support fintech issuing programs]"
   - Subheadings: What fraud risks do new card programs face? / What should a fintech look for
     in a fraud tool? / How does real-time risk scoring work for a new program? / How long does
     setup take? [UNKNOWN] / What data does the tool need?
   - Link up to the pillar: `/risk/card-not-present-fraud`.
   - FAQ: Do we need a fraud team to use it? / Does it work with our processor? / How is it priced? [UNKNOWN]

3. **IMPROVE PAGE: `/risk/fraud-tool-roi` (procurement)**
   - Add a direct answer at the top: the inputs to an ROI estimate (fraud losses, false-decline
     revenue, review costs) and how they combine. No ROI figures: [CLAIM NEEDS SUBSTANTIATION].
   - Link up to the pillar and ask the pillar owner to link down (the page is an orphan today).
   - Add a "last updated" date and named sources for any industry figure.

4. **IMPROVE PAGE: `/acceptance/dispute-management` (head of payments)**
   - Put a two-sentence answer about chargeback handling costs at the top.
   - Link down to `/acceptance/chargeback-reason-codes`, which is an orphan today.

5. **Title and description tests.**
   - `/acceptance/chargeback-reason-codes`: "Chargeback reason codes explained for merchants" vs
     "What each chargeback reason code means, and what to do next".
   - `/risk/false-declines`: "How issuers cut false declines without raising fraud" vs
     "False declines: a guide for card issuers".

6. **Needs a human.** Product facts marked [UNKNOWN]; any figure or outcome claim needs
   legal/compliance approval; content owners must approve each page before publishing.
