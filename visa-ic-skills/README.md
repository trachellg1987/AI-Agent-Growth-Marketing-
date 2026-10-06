# Visa Intelligent Commerce skills

[agent-payment-setup.ts](agent-payment-setup.ts) holds function templates for the **agent side** of Visa
Intelligent Commerce (VIC): the AI platform that pays on a cardholder's behalf.

| Template | What it does |
| --- | --- |
| `createAgentCredential` | Enrolls the cardholder's card for the agent (agent-specific token) |
| `createPurchaseInstruction` | Records what the cardholder approved: merchant, cap, expiry |
| `initiatePayment` | Checks the mandate, retrieves single-use credentials, checks out, confirms |
| `AgentWallet` | Lists, revokes, and lowers caps on approvals |
| `handleWebhook` | Verify-then-process pattern for signed webhooks |
| `MeteredTab` | Usage-based billing settled once per period within an approved cap (a pattern, not a Visa product) |

The method names mirror `VicApiClient` in Visa's open-source toolkit,
[github.com/visa/ai](https://github.com/visa/ai). You implement two small adapters with it: `VicClient` and
`VicPayloads` (built with Visa's payload builders, so field names match the API).

Merchants (agencies, SaaS tools) accept the resulting payments with
[examples/marketing-agency-visa-ic-integration.ts](../examples/marketing-agency-visa-ic-integration.ts).

Simplified examples: not affiliated with or reviewed by Visa. Test in Visa's sandbox first. Official docs:
[developer.visa.com](https://developer.visa.com/capabilities/visa-intelligent-commerce).
