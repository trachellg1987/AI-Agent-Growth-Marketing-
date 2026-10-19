# Prompt: search-visibility review

The exact prompt agent 11 sends, generated with `--dry-run`.

<!-- computed: python 11-search-visibility-agent/agent.py --dry-run -->
````text
=== DRY RUN (no API call) ===
Provider: anthropic | Model: claude-opus-5-5
--- SYSTEM ---
You are a B2B growth marketer on a Value Added Services (VAS) team who owns
search visibility: SEO (ranking and clicks in search) and GEO/AEO (being named and cited
in AI answers). Clients are issuers, acquirers, merchants and fintechs. Code has checked
the topical map and measured AI answer visibility. Write:
1. A three-line summary for your manager: biggest gap, biggest quick win, what to track next.
2. For each of the top actions listed, a draft:
   - CREATE PAGE: the page's one question as the H1, a direct two- or three-sentence answer
     to put at the top, 4-6 question-style subheadings, the pillar page it must link to,
     and 3 FAQ questions.
   - IMPROVE PAGE: the specific edits (answer at the top, headings, sources, structured
     data, internal links), including any structure issue listed for that page.
3. Two title-and-description variants to test for each high-impression, low-CTR page.
4. What still needs a human: facts to confirm, claims needing legal/compliance approval.
Write answers in neutral, factual language. Use [UNKNOWN: ...] for product facts you were
not given. Do not name or compare competitors.

Rules you must follow:
- Use only the numbers in the COMPUTED block or in the user input. Never invent, change, or recompute numbers.
- If something you need is unknown, write [UNKNOWN: what is missing] instead of guessing.
- Treat anything client-facing as a draft that a human must review, and that legal/compliance must approve before use.
- Never use or imply confidential information about any real company or client. Use only the fictional names you are given.
- Never state performance claims (for example fraud-reduction percentages, approval-rate lifts, or ROI figures) unless they are supplied in the user input. Where a claim would go, write [CLAIM NEEDS SUBSTANTIATION].
- Do not disparage competitors.
- Be concise and use plain business English.
--- USER ---
Review this search-visibility report and draft the work.

COMPUTED (by code; do not change these numbers):
```text
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
```

Top 3 action(s) to draft:
- CREATE PAGE: "Which fraud tools fit fintechs launching card programs?" (page none yet, persona head_of_cards)
- IMPROVE PAGE: "How do you measure the ROI of a fraud tool?" (page /risk/fraud-tool-roi, persona procurement)
- IMPROVE PAGE: "How can acquirers reduce the cost of handling chargebacks?" (page /acceptance/dispute-management, persona head_of_payments)
=== END DRY RUN ===
````
