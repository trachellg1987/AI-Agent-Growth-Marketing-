# Contributing

Thanks for helping. This repo teaches agentic workflows for B2B VAS marketing, so every
change should keep three rules intact: code does the math, unknowns are labeled, and a
human approves anything client-facing.

## Setup

```bash
make setup   # model SDKs, only needed for live runs and make test-api
make test    # must pass before you open a pull request
make lint    # needs Node.js for markdownlint
```

## Adding an agent

1. `make scaffold NAME=my-agent` (prompt-only) or `make scaffold NAME=my-agent PYTHON=1`.
2. Fill in `README.md`, `prompt.md`, and `example-output.md`.
3. Put any math in a skill script (`skills/<skill>/scripts/`), load it with
   `common.skills.load_skill_script`, and add unit tests in `tests/`.
4. Support `--dry-run`, and `--stats-only` if the agent computes anything.
5. Add a case to `scripts/smoke_test.py`.
6. Add computed blocks to your docs and run `make examples-update`. Never hand-type
   computed numbers.

## Content rules

- Fictional clients only ("Regional Bank A"), and generic, fictional product names.
- Label every example and case study ILLUSTRATIVE.
- No confidential or non-public information about any company or client.
- No performance claims without a source; use `[CLAIM NEEDS SUBSTANTIATION]`.
- Use client language: clients, client programs, issuers, acquirers, merchants, fintechs.
  `make validate` rejects terms that belong to telecom add-on marketing rather than B2B VAS.
- No company logos.

## Pull requests

Fill in the pull request template. Keep changes small and focused, and explain why.
