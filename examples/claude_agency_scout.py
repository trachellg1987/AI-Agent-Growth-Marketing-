"""Claude agent that compares three agencies' WebMCP-style tools, recommends one, and drafts an inquiry.

SIMPLIFIED EXAMPLE. The three agencies are fictional (ILLUSTRATIVE).

- With --mock, tool calls are answered by a local fictional catalog, so you only need ANTHROPIC_API_KEY.
- Without --mock, each tool call is forwarded to the agency's HTTP tool bridge
  (POST {base_url}/tools/{tool_name}), the same handlers your WebMCP tools call. In production you
  would more likely expose these as a remote MCP server; see examples/claude-agent-integration.md.
- submit_agency_inquiry never runs without the person typing "yes" first.

Usage:
    python examples/claude_agency_scout.py --mock --need "SEO for a Shopify store, about $4,000 a month"
    python examples/claude_agency_scout.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5-5")

AGENCIES = {
    "northwind": {"name": "Northwind Growth Co.", "base_url": "https://northwind.example"},
    "harbor": {"name": "Harbor Digital", "base_url": "https://harbor.example"},
    "summit": {"name": "Summit Search Partners", "base_url": "https://summit.example"},
}

SYSTEM = """You help a person choose a marketing agency.
1. Call discover_marketing_services for EACH agency in the list, then get_case_studies for the
   agencies with matching packages.
2. Compare them in a short table: package, monthly price, what's included, minimum term.
3. Recommend one and say why, using only what the tools returned. Do not invent prices or results.
4. Draft an inquiry with submit_agency_inquiry for the recommended agency. The person must confirm;
   if they decline, stop and summarize.
Quote case-study claims only as returned in approved_claims."""


def load_tools() -> list[dict]:
    """Build Claude tool definitions from the WebMCP JSON, adding an agency_id parameter."""
    discovery = json.loads((ROOT / "webmcp-skills" / "marketing-discovery.json").read_text())
    agency_tools = json.loads((ROOT / "examples" / "marketing-agency-webmcp-tools.json").read_text())["tools"]
    wanted = [discovery] + [t for t in agency_tools if t["name"] in ("get_case_studies", "submit_agency_inquiry")]
    tools = []
    for definition in wanted:
        schema = strip_docs(definition["inputSchema"])
        schema["properties"] = {
            "agency_id": {"type": "string", "enum": list(AGENCIES), "description": "Which agency to ask."},
            **schema["properties"],
        }
        schema["required"] = ["agency_id", *schema.get("required", [])]
        tools.append({"name": definition["name"], "description": definition["description"], "input_schema": schema})
    return tools


def strip_docs(value):
    """Remove documentation-only keys ($comment) before sending schemas to the API."""
    if isinstance(value, dict):
        return {k: strip_docs(v) for k, v in value.items() if k != "$comment"}
    if isinstance(value, list):
        return [strip_docs(v) for v in value]
    return value


def mock_tool(name: str, args: dict) -> dict:
    """Fictional responses so the example runs without real agencies."""
    agency = args["agency_id"]
    if name == "discover_marketing_services":
        catalog = {
            "northwind": [("nw-seo-growth", "E-commerce SEO Growth", 3500, 3)],
            "harbor": [("hb-seo-core", "SEO Core", 2800, 6)],
            "summit": [("sm-seo-plus", "SEO Plus", 5200, 12)],
        }
        matches = [
            {"package_id": pid, "name": pname, "monthly_price": price, "currency": "USD",
             "minimum_term_months": term, "purchasable_by_agent": False}
            for pid, pname, price, term in catalog[agency] if price <= args.get("budget", 0)
        ]
        return {"matches": matches} if matches else {"matches": [], "no_match_reason": "Over budget."}
    if name == "get_case_studies":
        return {"case_studies": [{
            "title": f"{AGENCIES[agency]['name']}: online store organic growth (fictional)",
            "summary": "Fictional example case study.",
            "approved_claims": [],
            "url": f"{AGENCIES[agency]['base_url']}/case-studies/1",
        }]}
    if name == "submit_agency_inquiry":
        return {"inquiry_id": f"{agency}-inq-001", "status": "received",
                "next_step": "A strategist will reply by email within 1 business day."}
    return {"error": f"unknown tool {name}"}


def call_bridge(name: str, args: dict) -> dict:
    payload = {k: v for k, v in args.items() if k != "agency_id"}
    request = urllib.request.Request(
        f"{AGENCIES[args['agency_id']]['base_url']}/tools/{name}",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read())
    except Exception as exc:  # report the failure to the model instead of crashing
        return {"error": f"tool call failed: {exc.__class__.__name__}"}


def confirm_inquiry(args: dict) -> bool:
    """Human in the loop: show exactly what will be sent and ask."""
    print("\nThe agent wants to send this inquiry:")
    print(json.dumps({k: v for k, v in args.items() if k != "agency_id"}, indent=2))
    print(f"To: {AGENCIES[args['agency_id']]['name']}")
    return input("Send it? Type 'yes' to confirm: ").strip().lower() == "yes"


def run_tool(name: str, args: dict, mock: bool) -> dict:
    if args.get("agency_id") not in AGENCIES:
        return {"error": "unknown agency_id"}
    if name == "submit_agency_inquiry" and not confirm_inquiry(args):
        return {"status": "not_sent", "reason": "The person declined. Do not retry."}
    return mock_tool(name, args) if mock else call_bridge(name, args)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare three agencies with Claude and draft an inquiry.")
    parser.add_argument("--need", default="SEO for a Shopify store selling outdoor gear, about $4,000 a month",
                        help="what the person is looking for")
    parser.add_argument("--mock", action="store_true", help="answer tool calls from a local fictional catalog")
    parser.add_argument("--dry-run", action="store_true", help="print the tools and prompt; no API call")
    args = parser.parse_args()

    tools = load_tools()
    user = f"Agencies to compare: {', '.join(AGENCIES)}.\nMy need: {args.need}"
    if args.dry_run:
        print(json.dumps({"model": MODEL, "system": SYSTEM, "user": user,
                          "tools": [t["name"] for t in tools]}, indent=2))
        return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set (or rerun with --dry-run).", file=sys.stderr)
        return 2

    import anthropic

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user}]
    for _ in range(12):  # hard cap on tool rounds
        response = client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM,
                                          tools=tools, messages=messages)
        if response.stop_reason == "refusal":
            print("The model declined this request.", file=sys.stderr)
            return 2
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            print("".join(b.text for b in response.content if b.type == "text"))
            return 0
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_tool(block.name, dict(block.input), args.mock)
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(output), "is_error": "error" in output})
        messages.append({"role": "user", "content": results})  # all results in one message
    print("Stopped after too many tool rounds.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
