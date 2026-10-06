<p align="center">
  <img src="images/banner.svg" alt="AI Growth Agents for marketers" width="100%">
</p>

# AI-Native Growth: WebMCP + Visa Intelligent Commerce for Marketing Services

[![validate](https://github.com/trachellg1987/AI-Agent-Growth-Marketing-/actions/workflows/validate.yml/badge.svg)](https://github.com/trachellg1987/AI-Agent-Growth-Marketing-/actions/workflows/validate.yml)

**Sites like visapaymentsfrontier.io are already live with WebMCP tools. AI agents can discover
services, ask questions, and submit leads without scraping a single button. And Visa and its partners
have already completed real agent-initiated payments. Are your marketing services ready?**

This repo is a playbook and starter kit for marketing agencies, SaaS vendors, consultancies and
freelancers who want to be **discoverable by AI agents** (WebMCP) and **payable by AI agents**
(Visa Intelligent Commerce).

> **Independent project.** Not affiliated with, endorsed by, or built with any confidential information
> from Visa, Anthropic, OpenAI or any other company. Visa is referenced only through public sources,
> which are linked. Fictional companies and all illustrative numbers are labeled as such.

## The problem

AI agents increasingly do the first round of vendor research for people. But a marketing agency's
website was built for human eyes:

- **Agents have to guess.** To find out whether an agency does SEO for e-commerce brands under
  $5,000 a month, an agent must read pages, click menus and fill forms meant for people. That is
  slow and it breaks when the page changes.
- **There's no standard menu of capabilities.** Every site describes its services differently, so
  agents can't compare agencies reliably.
- **There's no trusted way to pay.** Even when an agent finds the right service, handing it a raw card
  number is a security problem, and merchants can't tell a trusted agent from a malicious bot.

## The solution

Two open building blocks, used together:

| Layer | What it does | In one sentence |
| --- | --- | --- |
| **[WebMCP](docs/WEBMCP-EXPLAINED.md)** | Discovery and actions | Your website hands agents a menu of tools (`discover_seo_services`, `submit_agency_inquiry`) instead of making them guess at buttons. |
| **[Visa Intelligent Commerce](docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md)** | Trusted payment | Agents pay with agent-specific tokenized credentials that the cardholder authorized with a passkey, and merchants can verify the agent. |

**Discovery + trusted payment = an agent-ready marketing service.**

## The opportunity

- Gartner predicts that by 2028 **one-third of interactions with generative AI services** will use
  action models and autonomous agents to complete tasks
  ([Gartner, March 2024](https://www.gartner.com/en/newsroom/press-releases/2024-03-11-gartner-predicts-one-third-of-interactions-with-genai-services-will-use-action-models-and-autonomous-agents-for-task-completion-by-2028)).
- Gartner also expects AI agents to intermediate **more than $15 trillion of B2B purchases by 2028**
  ([Digital Commerce 360, November 2025](https://www.digitalcommerce360.com/2025/11/28/gartner-ai-agents-15-trillion-in-b2b-purchases-by-2028/)).
  Marketing services are a B2B purchase.
- Visa reports **more than 100 partners** working on agentic commerce, **over 30 building in the
  Visa Intelligent Commerce sandbox**, and **over 20 agents and agent enablers** integrating directly
  ([Visa, December 2025](https://investor.visa.com/news/news-details/2025/Visa-and-Partners-Complete-Secure-AI-Transactions-Setting-the-Stage-for-Mainstream-Adoption-in-2026/default.aspx)).

The gap: agents and payment rails are arriving faster than **services that agents can actually find and
buy**. [GROWTH-STRATEGY.md](docs/GROWTH-STRATEGY.md) explains why closing that gap is a growth lever.

## Real example: visapaymentsfrontier.io

[visapaymentsfrontier.io](https://visapaymentsfrontier.io) is listed in the public
[WebMCP directory](https://webmcp.com/) as a live site exposing **two WebMCP tools**. As described in this
repo's brief, they are `ask_site` (an agent asks about the site's services and case studies) and
`submit_contact_lead` (an agent submits a lead on a person's behalf).

That pair is the pattern this repo teaches: **one tool to answer questions, one tool to capture
intent.** See [CASE-STUDIES.md](CASE-STUDIES.md#case-study-1-visapaymentsfrontierio) for what it shows
and what it doesn't (no results have been published).

## Quick start: get your service agent-ready in 3 weeks

| Week | You do | Start from |
| --- | --- | --- |
| 1 | Register WebMCP tools: services, case studies, pricing, inquiry | [examples/marketing-agency-webmcp-tools.json](examples/marketing-agency-webmcp-tools.json) |
| 2 | Set up payment acceptance through your acquirer or processor, in the sandbox | [examples/marketing-agency-visa-ic-integration.ts](examples/marketing-agency-visa-ic-integration.ts) |
| 3 | Connect both, test end to end with an agent, go live | [IMPLEMENTATION-GUIDE.md](IMPLEMENTATION-GUIDE.md) |

Three weeks assumes a lead-capture launch (discovery plus inquiries). Taking agent payments also depends
on your processor's onboarding timeline, which this repo can't shorten.

## Table of contents

| Document | For | What you get |
| --- | --- | --- |
| [docs/GROWTH-STRATEGY.md](docs/GROWTH-STRATEGY.md) | Growth, partnerships, leadership | Why partner readiness is the lever, the flywheel, GTM tactics, metrics |
| [docs/WEBMCP-EXPLAINED.md](docs/WEBMCP-EXPLAINED.md) | Everyone | WebMCP in plain English, vs MCP vs browser automation, code |
| [docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md](docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md) | Everyone | How agents pay safely: tokens, passkeys, agent verification |
| [IMPLEMENTATION-GUIDE.md](IMPLEMENTATION-GUIDE.md) | Developers | Week-by-week integration plan and go-live checklist |
| [CASE-STUDIES.md](CASE-STUDIES.md) | Everyone | visapaymentsfrontier.io plus two illustrative partner scenarios |
| [examples/](examples/) | Developers | Tool definitions, payment integration, ChatGPT and Claude walkthroughs |
| [webmcp-skills/](webmcp-skills/) | Developers | Ready-to-adapt WebMCP tool definitions |
| [visa-ic-skills/](visa-ic-skills/) | Developers | Payment function templates (merchant side and agent side) |
| [docs/README-STRUCTURE.md](docs/README-STRUCTURE.md) | Everyone | Repo map and "start here" paths |

## Also in this repo: the B2B VAS marketing agent library

Ten tested agent workflows for a B2B Value Added Services marketing team (client briefs, offer-test
analysis, backward planning, a pre-launch prompt review), built on one rule: **code does the math, the
model explains, a human approves.** See [docs/AGENT-LIBRARY.md](docs/AGENT-LIBRARY.md).

```bash
make test   # validate, unit tests, reference check, example check, smoke test (no API key needed)
```

## Key sources

- WebMCP draft specification: [webmachinelearning.github.io/webmcp](https://webmachinelearning.github.io/webmcp/)
  and [github.com/webmachinelearning/webmcp](https://github.com/webmachinelearning/webmcp)
- Visa Intelligent Commerce: [developer.visa.com](https://developer.visa.com/capabilities/visa-intelligent-commerce)
  and Visa's open-source toolkit [github.com/visa/ai](https://github.com/visa/ai)
- Model Context Protocol: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Anthropic, a Visa Intelligent Commerce launch partner:
  [Visa press release, April 2025](https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21361.html)

## Credits and author

The numbered, folder-per-agent course format of the agent library is inspired by
[thaolst/ai-growth-agents-for-marketers](https://github.com/thaolst/ai-growth-agents-for-marketers)
(MIT License).

Trachell Trice ([LinkedIn](https://www.linkedin.com/in/trachell1234/)). No license is granted; all rights reserved.
