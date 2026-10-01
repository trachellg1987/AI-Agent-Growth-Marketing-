---
name: consent-check
description: Check an audience list plan against regional marketing-consent rules, contract basis, and opt-out lists before any email, webinar invite, or nurture send.
---

# Consent check

## When to use

Before a send or an invite list is finalized.

## Inputs

Audience definition (segments, regions, roles), channel, the consent rules in
`.agents/product-marketing-context.md`.

## Steps

1. Split the audience by region; apply the consent rule for each region and channel.
2. Remove contacts on opt-out or suppression lists.
3. Separate account-manager relationship contacts (contract basis) from marketing contacts (consent).

## Output

Who can be contacted, by which channel, on what basis, and who must be excluded.

## Guardrails

- This is a planning aid, not legal advice. Your privacy or legal team owns the rules.
- Never build the list from data the agent was not authorized to read.

## Used by

`03-campaign-brief`, `05-multi-agent-workflow`
