import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT, ab_stats

SAMPLE = ROOT / "08-ab-test-analyzer" / "sample-ab-results.csv"


class NormalTests(unittest.TestCase):
    def test_cdf_at_zero_is_half(self):
        self.assertAlmostEqual(ab_stats.normal_cdf(0), 0.5)

    def test_ppf_975_is_196(self):
        self.assertAlmostEqual(ab_stats.normal_ppf(0.975), 1.959964, places=5)

    def test_ppf_inverts_cdf(self):
        for x in (-2.5, -0.3, 0.0, 1.1, 3.0):
            self.assertAlmostEqual(ab_stats.normal_ppf(ab_stats.normal_cdf(x)), x, places=6)

    def test_ppf_rejects_bounds(self):
        for p in (0, 1, -0.1):
            with self.assertRaises(ValueError):
                ab_stats.normal_ppf(p)


class ZTestTests(unittest.TestCase):
    def test_known_values(self):
        t = ab_stats.two_proportion_ztest(20, 400, 44, 400)
        self.assertAlmostEqual(t.rate_a, 0.05)
        self.assertAlmostEqual(t.rate_b, 0.11)
        self.assertAlmostEqual(t.z, 3.1277, places=3)
        self.assertAlmostEqual(t.p_value, 0.00176, places=4)
        self.assertAlmostEqual(t.rel_lift, 1.2)

    def test_identical_rates(self):
        t = ab_stats.two_proportion_ztest(10, 100, 10, 100)
        self.assertEqual(t.z, 0)
        self.assertAlmostEqual(t.p_value, 1.0)

    def test_ci_contains_difference(self):
        t = ab_stats.two_proportion_ztest(30, 300, 12, 300)
        self.assertLess(t.ci_low, t.abs_diff)
        self.assertGreater(t.ci_high, t.abs_diff)
        self.assertLess(t.ci_high, 0)

    def test_zero_baseline_has_no_relative_lift(self):
        self.assertIsNone(ab_stats.two_proportion_ztest(0, 50, 5, 50).rel_lift)

    def test_all_zero_conversions(self):
        t = ab_stats.two_proportion_ztest(0, 50, 0, 50)
        self.assertEqual(t.p_value, 1.0)

    def test_rejects_bad_counts(self):
        with self.assertRaises(ValueError):
            ab_stats.two_proportion_ztest(11, 10, 1, 10)
        with self.assertRaises(ValueError):
            ab_stats.two_proportion_ztest(1, 0, 1, 10)


class WilsonTests(unittest.TestCase):
    def test_interval_contains_rate(self):
        low, high = ab_stats.wilson_interval(20, 400)
        self.assertLess(low, 0.05)
        self.assertGreater(high, 0.05)

    def test_zero_conversions_lower_bound_is_zero(self):
        self.assertEqual(ab_stats.wilson_interval(0, 30)[0], 0.0)

    def test_rejects_empty_sample(self):
        with self.assertRaises(ValueError):
            ab_stats.wilson_interval(0, 0)


class HolmAndSampleSizeTests(unittest.TestCase):
    def test_holm_known_example(self):
        adjusted = ab_stats.holm_adjust([0.01, 0.04, 0.03])
        for got, want in zip(adjusted, [0.03, 0.06, 0.06]):
            self.assertAlmostEqual(got, want)

    def test_holm_caps_at_one(self):
        self.assertEqual(ab_stats.holm_adjust([0.6, 0.7]), [1.0, 1.0])

    def test_sample_size_reference_value(self):
        # 5% -> 6% at alpha 0.05, power 0.8 needs about 8,158 per variant.
        self.assertAlmostEqual(ab_stats.sample_size_per_variant(0.05, 0.01), 8158, delta=5)

    def test_sample_size_rejects_bad_inputs(self):
        with self.assertRaises(ValueError):
            ab_stats.sample_size_per_variant(0.05, 0)
        with self.assertRaises(ValueError):
            ab_stats.sample_size_per_variant(1.2, 0.01)


class AnalyzeSampleTests(unittest.TestCase):
    def setUp(self):
        self.result = ab_stats.analyze(ab_stats.load_rows(SAMPLE))
        self.verdicts = {r["segment"]: r["verdict"] for r in self.result["segments"]}

    def test_segment_verdicts(self):
        self.assertEqual(self.verdicts, {
            "fintech_acquirers": "B better",
            "regional_issuers": "no evidence of a difference",
            "large_issuers": "A better",
        })

    def test_pooled_hides_effects(self):
        self.assertEqual(self.result["overall_verdict"], "no evidence of a difference")
        self.assertTrue(self.result["segments_disagree"])

    def test_report_mentions_warning(self):
        report = ab_stats.format_report(self.result, "ROI assessment offer", "free pilot offer", "demo requests")
        self.assertIn("segments disagree", report)
        self.assertIn("free pilot offer", report)


class LoadRowsTests(unittest.TestCase):
    def write(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return handle.name

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            ab_stats.load_rows(self.write("segment,variant,visitors\nx,A,10\n"))

    def test_bad_variant(self):
        with self.assertRaises(ValueError):
            ab_stats.load_rows(self.write("segment,variant,visitors,conversions\nx,C,10,1\n"))

    def test_segment_needs_both_variants(self):
        rows = ab_stats.load_rows(self.write("segment,variant,visitors,conversions\nx,A,10,1\n"))
        with self.assertRaises(ValueError):
            ab_stats.analyze(rows)


if __name__ == "__main__":
    unittest.main()
