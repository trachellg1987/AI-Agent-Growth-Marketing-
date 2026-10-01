"""Shared model helper used by every Python agent in this repo.

Design rule: code does the math, the model explains. Agents compute numbers in
plain Python, put them in a COMPUTED block, and ask the model only to explain,
prioritize, and flag risks. The model never recomputes anything.

Providers:
- Anthropic (default when ANTHROPIC_API_KEY is set)
- OpenAI (when LLM_PROVIDER=openai, or only OPENAI_API_KEY is set)

Every agent also supports --dry-run, which prints the exact prompt that would be
sent and makes no network call. Tests and CI use dry-run, so the repo can be
checked without an API key.
"""

from __future__ import annotations

import os
import sys
from typing import Callable

RULES = """Rules you must follow:
- Use only the numbers in the COMPUTED block or in the user input. Never invent, change, or recompute numbers.
- If something you need is unknown, write [UNKNOWN: what is missing] instead of guessing.
- Treat anything client-facing as a draft that a human must review, and that legal/compliance must approve before use.
- Never use or imply confidential information about any real company or client. Use only the fictional names you are given.
- Never state performance claims (for example fraud-reduction percentages, approval-rate lifts, or ROI figures) unless they are supplied in the user input. Where a claim would go, write [CLAIM NEEDS SUBSTANTIATION].
- Do not disparage competitors.
- Be concise and use plain business English."""

DEFAULT_ANTHROPIC_MODEL = "claude-opus-5-5"
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

# Models that accept Anthropic's server-side refusal fallback ("default" routing).
_FALLBACK_MODELS = {"claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5"}


class LLMError(RuntimeError):
    """A user-facing error: printed as one line, never as a traceback."""


def system_prompt(task_prompt: str) -> str:
    """Agent-specific instructions followed by the shared RULES."""
    return task_prompt.strip() + "\n\n" + RULES


def computed_block(lines: str) -> str:
    """Wrap code-computed figures so the model can tell them apart from prose."""
    return (
        "COMPUTED (by code; do not change these numbers):\n"
        "```text\n" + lines.rstrip() + "\n```"
    )


def provider() -> str:
    explicit = os.environ.get("LLM_PROVIDER", "").strip().lower()
    if explicit:
        if explicit not in ("anthropic", "openai"):
            raise LLMError(f"LLM_PROVIDER must be 'anthropic' or 'openai', not {explicit!r}.")
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "anthropic"


def model_name(which: str) -> str:
    if which == "anthropic":
        return os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    return os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)


def render_dry_run(system: str, user: str, label: str = "") -> str:
    which = provider()
    title = f"DRY RUN{': ' + label if label else ''} (no API call)"
    return (
        f"=== {title} ===\n"
        f"Provider: {which} | Model: {model_name(which)}\n"
        f"--- SYSTEM ---\n{system}\n"
        f"--- USER ---\n{user}\n"
        f"=== END DRY RUN ==="
    )


def ask(task_prompt: str, user: str, *, dry_run: bool = False, label: str = "",
        max_tokens: int = 16000) -> str:
    """Send one system+user prompt and return the model's text.

    With dry_run=True, return the rendered prompt instead of calling a model.
    """
    system = system_prompt(task_prompt)
    if dry_run:
        return render_dry_run(system, user, label)
    which = provider()
    if which == "anthropic":
        return _ask_anthropic(system, user, max_tokens)
    return _ask_openai(system, user, max_tokens)


def _ask_anthropic(system: str, user: str, max_tokens: int) -> str:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise LLMError(
            "ANTHROPIC_API_KEY is not set. Export it (see .env.example), set "
            "LLM_PROVIDER=openai with OPENAI_API_KEY, or rerun with --dry-run."
        )
    try:
        import anthropic
    except ImportError as exc:
        raise LLMError("The 'anthropic' package is missing. Run: make setup") from exc

    client = anthropic.Anthropic()
    model = model_name("anthropic")
    request = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    try:
        if model in _FALLBACK_MODELS:
            # If a safety classifier declines, the API retries on a fallback model.
            response = client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"], fallbacks="default", **request
            )
        else:
            response = client.messages.create(**request)
    except anthropic.AuthenticationError as exc:
        raise LLMError("The Anthropic API rejected the key in ANTHROPIC_API_KEY.") from exc
    except anthropic.RateLimitError as exc:
        raise LLMError("Rate limited by the Anthropic API. Wait a minute and retry.") from exc
    except anthropic.APIStatusError as exc:
        raise LLMError(f"Anthropic API error {exc.status_code}: {exc.message}") from exc
    except anthropic.APIConnectionError as exc:
        raise LLMError("Could not reach the Anthropic API. Check your network.") from exc

    if response.stop_reason == "refusal":
        raise LLMError("The model declined this request. Rephrase the input and retry.")
    text = "".join(block.text for block in response.content if block.type == "text")
    if not text.strip():
        raise LLMError("The model returned no text.")
    return text


def _ask_openai(system: str, user: str, max_tokens: int) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise LLMError(
            "OPENAI_API_KEY is not set. Export it (see .env.example) or rerun with --dry-run."
        )
    try:
        import openai
    except ImportError as exc:
        raise LLMError("The 'openai' package is missing. Run: make setup") from exc

    client = openai.OpenAI()
    try:
        response = client.chat.completions.create(
            model=model_name("openai"),
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    except openai.AuthenticationError as exc:
        raise LLMError("The OpenAI API rejected the key in OPENAI_API_KEY.") from exc
    except openai.RateLimitError as exc:
        raise LLMError("Rate limited by the OpenAI API. Wait a minute and retry.") from exc
    except openai.APIStatusError as exc:
        raise LLMError(f"OpenAI API error {exc.status_code}: {exc.message}") from exc
    except openai.APIConnectionError as exc:
        raise LLMError("Could not reach the OpenAI API. Check your network.") from exc

    text = response.choices[0].message.content or ""
    if not text.strip():
        raise LLMError("The model returned no text.")
    return text


def run(main: Callable[[], int | None]) -> None:
    """Run an agent's main(); print LLMError and input errors as one clean line."""
    try:
        code = main()
    except LLMError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        sys.exit(2)
    sys.exit(code or 0)
