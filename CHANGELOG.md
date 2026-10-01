# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-01

### Changed

- Reframed every agent, example, and case study for B2B Value Added Services: clients are
  issuers, acquirers, merchants and fintechs, and buyers are roles such as head of fraud/risk,
  head of cards, head of payments, and procurement.
- Portfolio categories follow the public FY2025 Visa Form 10-K (Issuing Solutions, Acceptance
  Solutions, Risk and Security Solutions, Advisory and Other Services), cited in the README.
- Context templates (`.agents/`) cover client types, buyer personas, sales motion (account
  managers, workshops, pilots), and compliance (regional marketing consent, client
  confidentiality, claims approval). All `[FILL IN]` placeholders kept.
- Agent 04 reads `sample-vas-client-programs.csv` and reports live and inactive client
  programs per VAS product; only column names and counts reach the model.
- Agent 05's Critic checks unsupported performance claims, client confidentiality, regional
  marketing-consent rules, claims needing legal approval, and competitor disparagement.
- Agent 07 plans new signed clients; the example is deliberately infeasible to show the flag.
- Agent 08 compares an ROI assessment offer with a free pilot offer across fintech/acquirer,
  regional issuer, and large issuer segments.
- Agent 09 plans live client programs net of monthly attrition and names the marginal channel.
- Agent 10 reviews a deliberately weak B2B outreach prompt with ten static checks.

### Added

- Shared rules: never use or imply confidential information about any real company or
  client; no performance claims unless supplied.
- Computed blocks in the docs are generated from real runs and re-checked by `make examples`.
- `make test-api`: agents run against a local fake Anthropic/OpenAI server.
- `docs/DESIGN-DECISIONS.md`.
- `make validate` rejects terms that belong to telecom add-on marketing rather than B2B VAS.

## [0.1.0] - 2026-10-01

### Added

- Repo scaffold: ten numbered agent folders, `common/llm.py` with Anthropic and OpenAI
  support and `--dry-run`, 13 skills with standard-library math scripts, unit tests,
  validation, smoke test, scaffold script, CI workflow, devcontainer, and markdownlint config.
