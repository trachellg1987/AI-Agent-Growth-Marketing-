---
name: search-visibility
description: Check a VAS topical map for SEO structure problems, measure how often AI answer engines name and cite you for buyer questions (GEO/AEO), and rank the pages to create or improve. Use for a weekly or monthly search-visibility review.
---

# Search visibility (SEO + GEO/AEO)

## When to use

You own discoverability for VAS products and want one view of two things:

- **SEO:** is the site organized so search engines understand it, and are high-impression
  pages earning clicks?
- **GEO/AEO** (generative engine optimization, also called answer engine optimization):
  when a head of fraud, head of payments, head of cards or procurement lead asks an AI
  answer engine a buying question, does the answer name your product and cite your page?

Typical cadence: log answer checks every week, run this review every week or month.

## Inputs

- **`pages.csv`, the topical map.** One row per page:
  `url,topic,role,target_question,links_to,impressions,clicks`.
  A *topic* has one **pillar** page (the complete overview) and several **cluster** pages
  (one buyer question each). `links_to` is semicolon-separated. `impressions` and `clicks`
  come from Google Search Console or Bing Webmaster Tools.
- **`answers.csv`, the answer log.** One row per question asked to one engine on one day:
  `checked_on,question,persona,engine,brand_mentioned,our_url_cited,competitor_mentions`.
  Record checks by hand or with a tool; ask each question the way the persona would.

## Steps

1. Run the script. Never count rates by hand or in the model:

   ```bash
   python skills/search-visibility/scripts/search_visibility.py --pages 11-search-visibility-agent/sample-pages.csv --answers 11-search-visibility-agent/sample-answers.csv
   ```

2. Fix **structure issues** first. They are cheap and help both SEO and GEO: every cluster
   links up to its pillar, every pillar links down to its clusters, no orphan pages, and only
   one page per question (two pages answering the same question compete with each other).
3. For **high impressions, low click-through** pages, plan a title and description test.
4. Work the **action list** top-down: `CREATE PAGE` (no page answers the question),
   then `IMPROVE PAGE` (lowest citation rate first). `MAINTAIN` pages need only a periodic
   freshness check.
5. Have a model draft the page outline or edits (agent `11-search-visibility-agent`).
   A content owner, and legal/compliance for any claim, approves before anything is published.

## What makes a page easier for AI answers to cite

- Put a direct two- or three-sentence answer to the page's one question at the top.
- Use clear question-style headings and short sections a model can quote.
- Back facts with named sources and a visible "last updated" date.
- Add FAQ or product structured data where it truly fits the page.
- Link it into its topic (pillar and clusters) so the topic reads as complete.

## Output

A topical-map summary with structure issues, a site click-through rate with snippet-test
candidates, mention and citation rates overall and by engine and persona, share of voice,
and a ranked action per buyer question.

## Guardrails

- AI answers vary by day, account and location. Track trends over weeks; small samples
  (under 5 checks per question) are directional only.
- Share of voice counts mentions, not sentiment. Read a few answers before acting.
- Never write a performance claim on a page without substantiation and approval.
- Never write about competitors by name or disparage them.
- Question wording should come from real buyer language (sales notes, search queries,
  webinar questions), not from guesses.

## Used by

`11-search-visibility-agent`, [docs/DAY-IN-THE-LIFE.md](../../docs/DAY-IN-THE-LIFE.md)
