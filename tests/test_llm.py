import os
import unittest
from unittest import mock

import tests.helpers  # noqa: F401  (puts the repo root on sys.path)
from common import llm

NO_KEYS = {k: v for k, v in os.environ.items()
           if not k.endswith("_API_KEY") and k not in ("LLM_PROVIDER", "ANTHROPIC_MODEL", "OPENAI_MODEL")}


class LLMHelperTests(unittest.TestCase):
    def test_rules_cover_confidentiality_and_claims(self):
        self.assertIn("confidential information about any real company or client", llm.RULES)
        self.assertIn("performance claims", llm.RULES)

    def test_system_prompt_appends_rules(self):
        self.assertTrue(llm.system_prompt("Task.").endswith(llm.RULES))

    def test_computed_block_wraps_text(self):
        block = llm.computed_block("a 1\nb 2\n")
        self.assertIn("COMPUTED (by code", block)
        self.assertIn("```text\na 1\nb 2\n```", block)

    @mock.patch.dict(os.environ, NO_KEYS, clear=True)
    def test_dry_run_makes_no_call(self):
        out = llm.ask("Task.", "Hello", dry_run=True, label="x")
        self.assertIn("DRY RUN: x", out)
        self.assertIn(llm.DEFAULT_ANTHROPIC_MODEL, out)

    @mock.patch.dict(os.environ, {**NO_KEYS, "OPENAI_API_KEY": "k"}, clear=True)
    def test_provider_falls_back_to_openai_key(self):
        self.assertEqual(llm.provider(), "openai")

    @mock.patch.dict(os.environ, {**NO_KEYS, "LLM_PROVIDER": "other"}, clear=True)
    def test_rejects_unknown_provider(self):
        with self.assertRaises(llm.LLMError):
            llm.provider()

    @mock.patch.dict(os.environ, NO_KEYS, clear=True)
    def test_missing_key_is_clear(self):
        with self.assertRaises(llm.LLMError) as ctx:
            llm.ask("Task.", "Hello")
        self.assertIn("ANTHROPIC_API_KEY is not set", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
