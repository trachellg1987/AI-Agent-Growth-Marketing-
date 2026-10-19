# 11 - Search visibility agent: SEO + GEO/AEO

A weekly or monthly search-visibility review for VAS products. Code checks the **topical map**
(SEO structure and click-through) and measures **AI answer visibility** (GEO/AEO: how often AI
answer engines name your product and cite your page for real buyer questions). Then it ranks
which pages to create or improve. The model drafts the page outlines and edits; a content owner
and legal/compliance approve them.

All counts and rates come from
[`skills/search-visibility/scripts/search_visibility.py`](../skills/search-visibility/scripts/search_visibility.py).
The model never recomputes them.

## Run

```bash
python 11-search-visibility-agent/agent.py --stats-only
python 11-search-visibility-agent/agent.py --dry-run
make run AGENT=11-search-visibility-agent ARGS="--top 2"
```

## Inputs

Both sample files are fictional.

[sample-pages.csv](sample-pages.csv), the topical map for two topics:

| Column | Meaning |
| --- | --- |
| `url` | Page path |
| `topic` | The topic the page belongs to (for example "card-not-present fraud") |
| `role` | `pillar` (the topic overview) or `cluster` (one buyer question) |
| `target_question` | The one buyer question the page answers |
| `links_to` | Internal links on the page, separated by `;` |
| `impressions`, `clicks` | From Google Search Console or Bing Webmaster Tools |

[sample-answers.csv](sample-answers.csv), six buyer questions asked to three AI answer engines
on two dates (36 checks):

| Column | Meaning |
| --- | --- |
| `checked_on` | Date of the check |
| `question`, `persona` | The buyer question and who would ask it |
| `engine` | `chatgpt`, `perplexity`, `google_ai_overview` |
| `brand_mentioned` | `yes` if the answer named your product |
| `our_url_cited` | Your page the answer cited, or blank |
| `competitor_mentions` | How many other vendors the answer named |

## What the sample shows

- **Structure:** two orphan pages, missing links between pillars and clusters, and two pages
  answering the same question (they compete with each other).
- **SEO quick wins:** two pages get plenty of impressions but less than half the site's
  click-through rate: candidates for a title and description test.
- **GEO/AEO:** the product is named in 42% of answers but its pages are cited in only 22%.
  Fraud leaders see it most; the head-of-cards question about fintech card programs has no
  page at all, so it ranks first as `CREATE PAGE`.

Related skill: [search-visibility](../skills/search-visibility/SKILL.md). How this fits a
working week: [docs/DAY-IN-THE-LIFE.md](../docs/DAY-IN-THE-LIFE.md).
