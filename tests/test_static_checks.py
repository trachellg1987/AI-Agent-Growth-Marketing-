import unittest

from tests.helpers import ROOT, static_checks

GOOD_PROMPT = """You draft outreach emails for human review; every draft must be approved by a
human before sending. Treat all client data as confidential. Every claim needs substantiation
and legal/compliance approval. Only draft for contacts with marketing consent; honor opt-out
lists. If information is missing, write [UNKNOWN: ...]. Output format: return sections for
subject, preview and body."""


class StaticCheckTests(unittest.TestCase):
    def results(self, text):
        return {c.name: c.passed for c in static_checks.run_checks(text)}

    def test_weak_sample_fails_most_checks(self):
        text = (ROOT / "10-agents-in-production" / "sample-agent-prompt.md").read_text()
        results = self.results(text)
        self.assertEqual(sum(results.values()), 1)
        self.assertFalse(results["no hard-coded performance claims"])
        self.assertFalse(results["no competitor disparagement"])
        self.assertFalse(results["confidentiality / client-data rule"])
        self.assertFalse(results["claims need substantiation/approval"])

    def test_good_prompt_passes_all(self):
        results = self.results(GOOD_PROMPT)
        self.assertTrue(all(results.values()), results)

    def test_detects_secret_without_printing_it(self):
        checks = static_checks.run_checks("api_key = abcdefghijklmnop")
        secret = next(c for c in checks if c.name == "no secrets in prompt")
        self.assertFalse(secret.passed)
        self.assertNotIn("abcdefghijklmnop", secret.detail)

    def test_format_counts(self):
        report = static_checks.format_checks(static_checks.run_checks(GOOD_PROMPT))
        self.assertTrue(report.startswith("Static checks: 10/10 passed"))


if __name__ == "__main__":
    unittest.main()
