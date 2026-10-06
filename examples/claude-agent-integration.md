# Claude agent integration

How Claude can discover and use a marketing agency's tools, and how that connects to Visa Intelligent
Commerce.

**Context:** Anthropic was named among Visa's AI partners when Visa Intelligent Commerce launched in
April 2025 ([Visa press release](https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21361.html)).
Visa's open-source toolkit also ships Claude Code skills ([github.com/visa/ai](https://github.com/visa/ai)).
This repo is independent of both companies.

## Two ways Claude reaches your tools

| | WebMCP | Remote MCP server |
| --- | --- | --- |
| Where the tools run | In your web page | On your server |
| How Claude connects | Through a WebMCP-capable browser the agent is working in | As a connector (claude.ai) or via the Messages API MCP connector |
| Best for | Agents browsing your site with the person's session | Chat and API agents that never open your site |

Both can use **the same tool definitions**. Keep them in one place
([webmcp-skills/](../webmcp-skills/), [marketing-agency-webmcp-tools.json](marketing-agency-webmcp-tools.json))
and expose them both ways. Check current WebMCP support in the browser your agent uses; the remote MCP
path works today.

## Option A: expose your tools as a remote MCP server

A minimal server using the official MCP Python SDK (simplified example; see the
[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) for current APIs and auth):

```python
# agency_mcp_server.py — simplified example
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("northwind-growth")  # fictional agency


@mcp.tool()
def discover_marketing_services(service_type: str, budget: float, industry: str = "other") -> dict:
    """Find this agency's packages for a service type and monthly budget (USD). Read-only."""
    return catalog_search(service_type, budget, industry)  # your existing catalog lookup


@mcp.tool()
def submit_agency_inquiry(contact_name: str, contact_email: str, service_needed: str,
                          message: str, consent_to_contact: bool) -> dict:
    """Send an inquiry on the person's behalf. Requires consent_to_contact=true. No payment."""
    if consent_to_contact is not True:
        return {"status": "rejected", "next_step": "Ask the person for consent to be contacted."}
    return create_lead(contact_name, contact_email, service_needed, message, source="claude")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

Then either:

- **In Claude apps:** add the server's URL as a custom connector (Settings → Connectors). Menu names
  change; see Anthropic's help center.
- **From your own agent code:** use the Messages API MCP connector (beta), which needs both halves:

```python
import anthropic

client = anthropic.Anthropic()
response = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[{"type": "url", "url": "https://northwind.example/mcp", "name": "northwind"}],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "northwind"}],
    messages=[{"role": "user", "content": "Find an SEO package under $4,000/month for my online store."}],
)
```

## Option B: a Claude agent script that evaluates three agencies

[claude_agency_scout.py](claude_agency_scout.py) is a runnable example: Claude calls each agency's
discovery and case-study tools, compares them, recommends one, and drafts an inquiry. The inquiry is
only sent if the person types `yes`.

```bash
python examples/claude_agency_scout.py --dry-run     # show tools and prompt, no API call
python examples/claude_agency_scout.py --mock        # fictional agencies, needs ANTHROPIC_API_KEY
```

How it works:

1. **Tool definitions come from this repo's JSON.** The script loads
   `webmcp-skills/marketing-discovery.json` and two tools from `marketing-agency-webmcp-tools.json`,
   adds an `agency_id` parameter, and strips documentation-only keys.
2. **Claude decides which tools to call.** It typically calls discovery for all three agencies at once;
   the script returns every result in a single message.
3. **Code enforces the guardrails, not the prompt:** an unknown `agency_id` is rejected, and
   `submit_agency_inquiry` requires typed confirmation.
4. **Failures are reported to the model** (`is_error: true`) instead of crashing, so it can adapt.

What a run looks like (illustrative, abbreviated):

```text
| Agency     | Package               | $/month | Min. term |
| Northwind  | E-commerce SEO Growth | 3,500   | 3 months  |
| Harbor     | SEO Core              | 2,800   | 6 months  |
| Summit     | no match (over budget)|         |           |
Recommendation: Northwind. Within budget, shortest commitment, includes product-page work.

The agent wants to send this inquiry: {...}
Send it? Type 'yes' to confirm:
```

## Adding payment

When an agency marks a package `purchasable_by_agent`, the agent platform pays through Visa Intelligent
Commerce: the person approves a purchase instruction, the platform retrieves single-use credentials, and
the agency's `initiateAgentPayment()` charges them. See
[marketing-agency-visa-ic-integration.ts](marketing-agency-visa-ic-integration.ts) and
[docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md](../docs/VISA-INTELLIGENT-COMMERCE-EXPLAINED.md).

## Why build for Claude (alongside other assistants)

- **MCP is an open standard Anthropic created**, so one MCP server serves Claude and any other
  MCP-capable assistant. You don't build per-assistant plugins.
- **Anthropic is a named Visa Intelligent Commerce partner**, and Visa's toolkit includes Claude Code
  skills, so the payment side has a documented path.
- **Claude Code skills** let your team's developers get guided help integrating Visa APIs inside their
  editor ([github.com/visa/ai/skills](https://github.com/visa/ai/tree/main/skills)).
