# Example output: agent prompt review

> ILLUSTRATIVE: the reviewed prompt is a fictional, deliberately weak sample. The computed
> block is real output of the command shown; the model review is a hand-written sample.

## Static checks (code)

<!-- computed: python 10-agents-in-production/agent.py --static-only -->
````text
Static checks: 1/10 passed

[FLAG] human approval step: no human review or approval step before anything is sent
[FLAG] no hard-coded performance claims: promises a specific result: cut fraud losses by 40%
[FLAG] no competitor disparagement: disparages competitors: competitors
are outdated and insecure
[FLAG] no sensitive client data pulled: pulls sensitive client data: incident notes
[FLAG] confidentiality / client-data rule: never mentions client confidentiality or client-data handling
[FLAG] claims need substantiation/approval: never says claims need substantiation or legal/compliance approval
[FLAG] recipient scope and marketing consent: sends to everyone: Send the email to everyone
[PASS] no secrets in prompt: no keys or passwords embedded
[FLAG] unknowns are labeled, not guessed: no instruction for missing information; the agent may guess
[FLAG] output format defined: no output format; results will vary run to run
````

## Sample model review

| Severity | Line | Risk | Fix |
| --- | --- | --- | --- |
| High | "cut fraud losses by 40%" | Unsubstantiated performance claim | Remove; use only claims approved by legal/compliance |
| High | "incident notes for each client" | Confidential client data in outreach | Remove CRM incident access; read only name, role, and consent status |
| High | "Send the email to everyone in the CRM" | No consent basis; no human approval | Draft only; send to a consent-checked list after human approval |
| Medium | "competitors are outdated and insecure" | Competitor disparagement | Remove comparisons |
| Medium | (missing) | No rule for unknowns or output format | Add both |

Rewritten prompt (excerpt):

```text
You draft outreach emails about the Risk Scoring Service for human review. You never send.
Read only: contact name, role, client type, and marketing-consent status. Do not read
incident, fraud-case or contract notes. Treat all client data as confidential.
Make no performance claims unless they appear in the approved-claims list; every claim
needs substantiation and legal/compliance approval. Do not mention competitors.
Draft only for contacts with consent or a contract basis under the regional rules.
If information is missing, write [UNKNOWN: ...]. Output: subject, preview, body
(max 150 words), and a list of claims used with their approval IDs.
```
