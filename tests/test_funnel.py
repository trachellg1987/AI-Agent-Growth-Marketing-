import unittest

from tests.helpers import funnel

SPEC = "reached:0.70,engaged:0.25,pilot:0.60,signed:0.30"


class ParseTests(unittest.TestCase):
    def test_parses_in_order(self):
        stages = funnel.parse_funnel(SPEC)
        self.assertEqual([s.name for s in stages], ["reached", "engaged", "pilot", "signed"])
        self.assertEqual(stages[1].rate, 0.25)

    def test_rejects_bad_format(self):
        with self.assertRaises(ValueError):
            funnel.parse_funnel("reached=0.7")

    def test_rejects_rate_out_of_range(self):
        for spec in ("reached:0", "reached:1.5", "reached:abc"):
            with self.assertRaises(ValueError):
                funnel.parse_funnel(spec)

    def test_rejects_duplicate_stage(self):
        with self.assertRaises(ValueError):
            funnel.parse_funnel("a:0.5,a:0.5")


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.stages = funnel.parse_funnel(SPEC)

    def test_backward_rounds_up(self):
        self.assertEqual(funnel.backward_counts(20, self.stages), [
            ("eligible", 640), ("reached", 448), ("engaged", 112), ("pilot", 67), ("signed", 20)])

    def test_forward_rounds_down(self):
        self.assertEqual(funnel.forward_capacity(600, self.stages), [
            ("eligible", 600), ("reached", 420), ("engaged", 105), ("pilot", 63), ("signed", 18)])

    def test_example_is_infeasible(self):
        p = funnel.plan(20, 600, self.stages, 120000, 12)
        self.assertFalse(p["feasible"])
        self.assertEqual(p["max_signed"], 18)
        self.assertAlmostEqual(p["last_stage_rate_needed"], 20 / 63)
        self.assertEqual(p["budget_per_signed"], 6000)
        self.assertIn("INFEASIBLE", funnel.format_plan(p))

    def test_lower_target_is_feasible(self):
        p = funnel.plan(18, 600, self.stages, 120000, 12)
        self.assertTrue(p["feasible"])
        self.assertIn("FEASIBLE", funnel.format_plan(p))

    def test_rejects_non_positive_inputs(self):
        with self.assertRaises(ValueError):
            funnel.plan(0, 600, self.stages, 1000, 12)
        with self.assertRaises(ValueError):
            funnel.plan(20, 600, self.stages, -1, 12)


if __name__ == "__main__":
    unittest.main()
