# WebMCP explained

## What is WebMCP?

**It's like a menu your website gives to AI agents instead of making them guess at buttons.**

When an AI agent visits a normal website, it sees what you see: text, images, buttons, forms. To do
anything, it has to work out which button means "get a quote" and which form field means "budget".
WebMCP lets the page say, in a structured way: "Here are the things you can do here. Here's what each one
needs. Call them directly."

Technically, WebMCP is a proposed web standard, a draft from the W3C Web Machine Learning Community Group,
with Google and Microsoft involved. A page registers **tools** in JavaScript. Each tool has a name, a
plain-language description, a JSON Schema for its inputs, and a function that runs when an agent calls it.

- Spec: [webmachinelearning.github.io/webmcp](https://webmachinelearning.github.io/webmcp/)
- Repo and explainer: [github.com/webmachinelearning/webmcp](https://github.com/webmachinelearning/webmcp)
- Chrome demo explainer: [googlechromelabs.github.io/webmcp-tools](https://googlechromelabs.github.io/webmcp-tools/demos/explainer/)

> **Status check.** WebMCP is a draft and still changing. The API entry point moved from
> `navigator.modelContext` to `document.modelContext` in 2026, so check the current spec before you ship.

## Why it matters

| Browser automation (agent clicks around) | WebMCP (agent calls tools) |
| --- | --- |
| Slow: read the page, find the button, click, wait, re-read | Fast: one structured call |
| Fragile: breaks when you redesign the page | Stable: tools are a contract you version |
| Guesswork: "is this field the budget or the deposit?" | Typed: the schema says `budget_usd`, a number |
| The site can't tell the agent what's allowed | The site decides exactly which actions exist |

For a marketing agency, that difference decides whether an agent recommends you. An agent comparing
five agencies will favor the ones it can query reliably.

## WebMCP vs MCP vs browser automation

| | WebMCP | MCP (Model Context Protocol) | Browser automation |
| --- | --- | --- | --- |
| Where tools live | In your web page (JavaScript) | On a server you run | Nowhere: the agent improvises |
| Who calls them | An agent working inside a browser tab | An AI app connected to your server (Claude, ChatGPT and others) | An agent driving a browser |
| User's session | Shares the user's logged-in browser session | Separate; uses its own auth | Shares the browser session |
| Setup | Add a script to your site | Build and host an MCP server | None, but unreliable |
| Best for | Actions on your existing website | Headless integrations and chat apps | Sites with no tools at all |

**They're complementary.** Define each tool once (the JSON in [webmcp-skills/](../webmcp-skills/)) and
expose it two ways: WebMCP for agents browsing your site, and a remote MCP server for chat assistants.
See [examples/claude-agent-integration.md](../examples/claude-agent-integration.md) and
[examples/chatgpt-plugin-integration.md](../examples/chatgpt-plugin-integration.md).

## Example: visapaymentsfrontier.io

[visapaymentsfrontier.io](https://visapaymentsfrontier.io) is listed in the public
[WebMCP directory](https://webmcp.com/) as a live site with two tools. As described in this repo's brief:

| Tool | What an agent does with it |
| --- | --- |
| `ask_site` | Asks a question about the site's services and case studies, and gets an answer |
| `submit_contact_lead` | Submits a contact request on behalf of a person |

**How agents discover them:** when an agent loads the page in a WebMCP-capable browser, the page's script
registers its tools. The browser lists those tools (name, description, input schema) to the agent.

**How agents call them:** the agent picks a tool, fills in the inputs according to the schema, and the
browser runs the page's handler. The handler returns a structured result the agent can read.

> Verify the tool names yourself before citing them. Open the site in a browser with WebMCP enabled and
> inspect the registered tools; the public directory listing only confirms that there are two.

## Code: register a tool (simplified example)

```javascript
// Simplified example. Feature-detect: WebMCP is a draft and not in every browser.
if ("modelContext" in document) {
  document.modelContext.registerTool({
    name: "discover_seo_services",
    description:
      "List this agency's SEO service packages that fit a budget, industry and timeframe. " +
      "Read-only: does not contact anyone or create a lead.",
    inputSchema: {
      type: "object",
      properties: {
        industry: { type: "string", description: "Client industry, e.g. 'ecommerce' or 'b2b saas'" },
        monthly_budget_usd: { type: "number", minimum: 0, description: "Monthly budget in US dollars" },
        timeframe_months: { type: "integer", minimum: 1, maximum: 36 }
      },
      required: ["industry", "monthly_budget_usd"]
    },
    annotations: { readOnlyHint: true }, // tells the agent this tool changes nothing
    async execute({ industry, monthly_budget_usd, timeframe_months = 6 }) {
      const res = await fetch("/api/services/seo?" + new URLSearchParams({
        industry, budget: String(monthly_budget_usd), months: String(timeframe_months)
      }));
      if (!res.ok) {
        return { content: [{ type: "text", text: "Service catalog unavailable. Please try again later." }] };
      }
      const packages = await res.json();
      return { content: [{ type: "text", text: JSON.stringify(packages) }] };
    }
  });
}
```

What makes a tool agent-friendly:

- **The description says what the tool does and doesn't do** ("read-only: does not create a lead").
- **Inputs are typed, with units in the names** (`monthly_budget_usd`, not `budget`).
- **Failures return a readable message**, so the agent can recover instead of giving up.
- **Anything with side effects** (submitting a lead, paying) is a separate tool that confirms with the
  person first. The draft spec includes ways to request user interaction; check the current version.

Full, adaptable definitions: [examples/marketing-agency-webmcp-tools.json](../examples/marketing-agency-webmcp-tools.json)
and [webmcp-skills/](../webmcp-skills/).
