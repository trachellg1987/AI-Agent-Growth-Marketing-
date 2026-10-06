# Implementation guide: agent-ready in 3 weeks

A step-by-step plan for a marketing agency, SaaS vendor, consultancy or freelancer.

**What "3 weeks" covers:** weeks 1 and 3 (discovery and lead capture) are fully in your control.
Taking agent payments (week 2) also depends on your payment processor's onboarding, which can take
longer. Launch lead capture first; switch on payments when your processor is ready.

> Simplified examples throughout. WebMCP is a draft standard and Visa Intelligent Commerce details change,
> so check the official docs linked at the end before you ship.

## Week 1: register WebMCP tools on your website

### What is `document.modelContext`?

It's the browser API WebMCP adds. Your page calls `document.modelContext.registerTool(...)` to tell
agents "here is something you can do on this page". Early drafts used `navigator.modelContext`; the
spec moved it to `document` in 2026. Always feature-detect. Background: [docs/WEBMCP-EXPLAINED.md](docs/WEBMCP-EXPLAINED.md).

### Day 1-2: decide your tools

Start with the two-tool pattern used by visapaymentsfrontier.io: one tool to **answer questions** and
one to **capture intent**. Then add discovery and pricing.

| Business | Read-only tools | Action tool |
| --- | --- | --- |
| Marketing agency | `discover_seo_services`, `discover_ppc_services`, `get_case_studies`, `get_pricing` | `submit_agency_inquiry` |
| SaaS marketing tool | `discover_marketing_services`, `get_pricing`, `compare_pricing` | `start_checkout` (week 3) |
| Consultant or freelancer | `ask_site`, `get_availability` | `submit_contact_lead` |

Copy from [examples/marketing-agency-webmcp-tools.json](examples/marketing-agency-webmcp-tools.json)
and [webmcp-skills/](webmcp-skills/).

### Day 3-4: register them

```javascript
// tools.js — simplified example. Load on every page where agents should find the tools.
import definitions from "./marketing-agency-webmcp-tools.json" with { type: "json" };

const handlers = {
  discover_seo_services: (input) => api("/api/services/seo", input),
  discover_ppc_services: (input) => api("/api/services/ppc", input),
  get_case_studies: (input) => api("/api/case-studies", input),
  get_pricing: (input) => api("/api/pricing", input),
  submit_agency_inquiry: (input) => api("/api/inquiries", input, "POST"),
};

async function api(path, input, method = "GET") {
  const url = method === "GET" ? `${path}?${new URLSearchParams(input)}` : path;
  const res = await fetch(url, method === "GET" ? {} : {
    method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(input),
  });
  const text = res.ok ? JSON.stringify(await res.json()) : `Request failed (${res.status}). Please try again later.`;
  return { content: [{ type: "text", text }] };
}

// Remove documentation-only keys ($comment, x-...) before registering.
function clean(value) {
  if (Array.isArray(value)) return value.map(clean);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value)
      .filter(([k]) => k !== "$comment" && !k.startsWith("x-"))
      .map(([k, v]) => [k, clean(v)]));
  }
  return value;
}

if ("modelContext" in document) {
  for (const def of definitions.tools) {
    const { name, title, description, inputSchema, annotations } = clean(def);
    document.modelContext.registerTool({ name, title, description, inputSchema, annotations, execute: handlers[name] });
  }
}
```

Your server endpoints must validate input again. Never trust that the agent followed the schema.

### Day 5: test discovery in a browser

1. Use a browser build with WebMCP enabled (check the [spec repo](https://github.com/webmachinelearning/webmcp)
   for current browser support and flags).
2. Open your page and confirm each tool is listed with its name, description and schema.
3. Call each read-only tool with good and bad inputs. Bad input must return a readable error, not a crash.
4. Call `submit_agency_inquiry`: it must ask the person to confirm before sending.

## Week 2: set up Visa Intelligent Commerce

As a merchant, you **accept** agent payments; you don't issue agent tokens. Agent platforms do that
(see [docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md](docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md)).

### Day 1: merchant account

Talk to your acquirer or payment processor about accepting agent-initiated, tokenized payments. If you
use Visa Acceptance or Cybersource, start with the
[Intelligent Commerce developer guide](https://developer.visaacceptance.com/docs/vas/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce.html).
Ask about sandbox access, agent verification (Trusted Agent Protocol), and timelines.

### Day 2: token handling

You never store card data. Your processor handles tokenized credentials. Your job:

- pass credentials straight from the request to the processor; never log them
- use idempotency keys so agent retries never charge twice
- keep the agent's id on the order for disputes and reporting

### Day 3-4: configure payment flows

Decide what agents may buy without a human sales conversation. A good rule: **fixed price, fixed scope,
cancel anytime.** Mark those offers `purchasable_by_agent: true` in `get_pricing`. Everything else goes to
`submit_agency_inquiry`.

Wire up `initiateAgentPayment()` from
[examples/marketing-agency-visa-ic-integration.ts](examples/marketing-agency-visa-ic-integration.ts):
verify the agent, check approval, price from your catalog, charge, provision.

### Day 5: sandbox testing

| Test | Expected |
| --- | --- |
| Valid agent, approved, correct price | Paid, service provisioned, receipt returned |
| Same request sent twice | Charged once, same receipt |
| Unsigned agent | `AGENT_NOT_VERIFIED`, no charge |
| Stale price | `PRICE_MISMATCH`, no charge |
| Custom-scope package | `OFFER_NOT_AGENT_PURCHASABLE`, routed to inquiry |
| Declined credentials | `PAYMENT_DECLINED`, order marked failed |

## Week 3: integrate both

1. **Agents discover your WebMCP tools.** Re-run week 1's browser test on production.
2. **Agents submit leads (no payment yet).** Turn on `submit_agency_inquiry` in production. Route leads
   to your CRM tagged `source=agent` and the agent's name, so you can measure the channel.
3. **Agents purchase premium services.** Expose a payment tool (for example `purchase_package`) only
   for `purchasable_by_agent` offers. It calls `initiateAgentPayment()` and asks the person to confirm the
   price before paying.
4. **Real transactions go live.** Start with one low-price package, watch the first transactions by hand,
   then widen.

Also exposing the same tools to chat assistants? Reuse the definitions on a remote MCP server:
[examples/claude-agent-integration.md](examples/claude-agent-integration.md) and
[examples/chatgpt-plugin-integration.md](examples/chatgpt-plugin-integration.md).

## Before you go live

- [ ] Every tool description says what it does and what it does not do
- [ ] Read-only tools are marked `readOnlyHint: true`; action tools are not
- [ ] Action tools ask the person to confirm before acting
- [ ] Server-side validation on every endpoint (the schema is not a security boundary)
- [ ] Inquiries require explicit consent to contact; regional marketing-consent rules checked
- [ ] Case studies return only client-approved material and legal-approved claims
- [ ] Prices returned by tools match your website and invoices
- [ ] Agent payments: agent verification on, idempotency keys enforced, credentials never logged
- [ ] Refund, cancellation and support paths documented and returned in receipts
- [ ] Monitoring: agent leads and agent payments tracked as their own channel
- [ ] A named person owns the tools and reviews agent activity weekly

## Support and references

- WebMCP spec: [webmachinelearning.github.io/webmcp](https://webmachinelearning.github.io/webmcp/)
  and [github.com/webmachinelearning/webmcp](https://github.com/webmachinelearning/webmcp)
- Visa Intelligent Commerce: [developer.visa.com](https://developer.visa.com/capabilities/visa-intelligent-commerce)
- Visa's open-source toolkit: [github.com/visa/ai](https://github.com/visa/ai)
- Model Context Protocol: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Questions about this repo: open a GitHub Discussion or issue
