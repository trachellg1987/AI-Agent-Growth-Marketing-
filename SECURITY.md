# Security policy

## Reporting a problem

Please do not open a public issue for security problems. Use GitHub's private vulnerability
reporting on this repository (Security tab, "Report a vulnerability").

## What must never be committed

- API keys, tokens, or passwords. Keep keys in `.env`, which is git-ignored; `.env.example`
  holds names only.
- Confidential or non-public information about any real company or client: client names,
  contracts, pricing, incident or fraud-case notes, performance data, or internal documents.
- Real client exports. Use `data/` or `*.local.csv` (both git-ignored) for local files.

`make validate` scans for common key formats, but it cannot recognize confidential business
information. That is the contributor's responsibility.

## How the agents limit exposure

- Agents send aggregates to the model, not client rows (see agent 04).
- `--dry-run` shows exactly what would be sent before anything is sent.
- The shared rules in `common/llm.py` tell the model never to use or imply confidential
  information about any real company or client.
