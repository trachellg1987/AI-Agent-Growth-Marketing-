# Visa Intelligent Commerce explained

Written from public sources only. Product details change; check the official links before you build.

## What is Visa Intelligent Commerce?

Visa Intelligent Commerce (VIC) is Visa's program for letting AI agents **find and buy** on behalf of
people safely. Visa announced it in April 2025 with AI partners including Anthropic, Microsoft, Mistral AI,
OpenAI, Perplexity, Samsung and Stripe
([Visa press release](https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21361.html)).

The core idea: **an agent never needs your real card number.** It gets a token made for that agent,
which only works within limits you approved.

Official resources:

- [Visa Intelligent Commerce on Visa Developer](https://developer.visa.com/capabilities/visa-intelligent-commerce)
- [Intelligent Commerce developer guide (Visa Acceptance Platform)](https://developer.visaacceptance.com/docs/vas/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce.html)
- [github.com/visa/ai](https://github.com/visa/ai): Visa's open-source toolkit (API and MCP clients,
  an agent demo, Claude Code skills)
- [Visa MCP hub](https://mcp.visa.com)

## Three key services

### 1. Agent onboarding and vetting

Agent builders integrate with VIC as partners, and merchants need a way to tell a trusted agent from a
malicious bot. Visa's **Trusted Agent Protocol**, launched in October 2025, lets an agent sign its
requests cryptographically (built on HTTP Message Signatures, RFC 9421) so a merchant's site can verify
who is calling ([Finextra](https://www.finextra.com/newsarticle/46901/visa-builds-trust-protocol-for-agentic-commerce)).

### 2. Tokenized payment credentials (agent tokens)

The cardholder enrolls a card for an agent. Visa's token service issues an **agent-specific token**, and
the cardholder authenticates with a **Visa Payment Passkey**. For each purchase, the agent submits a
**purchase instruction** (what, how much, from whom), then retrieves single-use transaction credentials
to check out. Afterwards it **confirms** the transaction events back to Visa. These steps match the API
examples in [github.com/visa/ai](https://github.com/visa/ai): `enrollCard`,
`initiatePurchaseInstruction`, `getTransactionCredentials`, `sendConfirmations`.

### 3. Merchant integration

For a merchant (for example, a marketing agency selling a service package), an agent payment arrives as a
**tokenized card payment** through its normal acquirer or payment processor. The merchant doesn't
build a card vault and never sees the real card number. What changes:

- verify the agent (Trusted Agent Protocol) before accepting high-risk actions
- make your offers machine-readable (WebMCP tools with exact prices and terms)
- confirm, deliver, and support the order like any other online payment

## Why traditional payments don't work for agents

| Problem | What goes wrong |
| --- | --- |
| **Credential exposure** | Giving an agent a raw card number means it, its logs, and every site it visits can leak it. |
| **Authentication** | Checkout flows assume a human typing a one-time code. An agent can't, and shouldn't, impersonate the cardholder. |
| **Trust** | Merchants block bots by default. They can't distinguish a person's helpful agent from a fraudster's script. |
| **Intent** | A card has no idea what the person actually authorized ("up to $500, this vendor, this week"). |

## How VIC addresses it

| Problem | VIC approach |
| --- | --- |
| Credential exposure | Agent-specific tokens instead of card numbers; credentials retrieved per transaction |
| Authentication | Visa Payment Passkeys: the cardholder approves with a device passkey, not a password |
| Trust | Trusted Agent Protocol: signed agent requests that merchants can verify |
| Intent | Purchase instructions record what the cardholder approved, and the purchase is checked against them |

## Use cases

- **Shopping on a person's behalf:** "Find running shoes under $120 and buy them." The agent searches,
  then pays with its token within the approved limit.
- **B2B purchasing and bill pay:** an agent for a small business compares vendors (for example,
  marketing agencies) and pays an approved invoice. Visa also describes agentic capabilities for
  commercial payments ([Visa Commercial Solutions](https://corporate.visa.com/en/solutions/intelligent-commerce/vcs-agentic-ai.html)).
- **Recurring payments:** a monthly retainer or a usage-based tool charged within limits the person set.

## How visapaymentsfrontier.io fits

[visapaymentsfrontier.io](https://visapaymentsfrontier.io) is a live WebMCP site with two listed tools,
described in this repo's brief as `ask_site` and `submit_contact_lead`. It shows the **discovery and
lead-capture half** of the stack. VIC is the **payment half**. A partner who does both is fully agent-ready:
agents can find it, ask questions, express intent, and pay.

## Where this repo's code fits

| You are | You build | See |
| --- | --- | --- |
| A merchant (agency, SaaS) | WebMCP tools, agent verification, order creation, tokenized payment acceptance through your processor | [examples/marketing-agency-visa-ic-integration.ts](../examples/marketing-agency-visa-ic-integration.ts) |
| An agent builder | Card enrollment, purchase instructions, credential retrieval, confirmations | [visa-ic-skills/agent-payment-setup.ts](../visa-ic-skills/agent-payment-setup.ts) |
