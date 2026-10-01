import unittest

from tests.helpers import capacity

CHANNELS = ("email_nurture:3000:0.001:0.5,account_manager:120:0.08:150,"
            "webinar:600:0.01:20,workshop:25:0.2:2000")


class ParseTests(unittest.TestCase):
    def test_parses_channels(self):
        channels = capacity.parse_channels(CHANNELS)
        self.assertEqual(len(channels), 4)
        am = channels[1]
        self.assertAlmostEqual(am.monthly_capacity, 9.6)
        self.assertAlmostEqual(am.cost_per_client, 1875)

    def test_rejects_bad_channel(self):
        for spec in ("email:100:0.1", "email:100:1.5:1", "email:-5:0.1:1", "email:x:0.1:1"):
            with self.assertRaises(ValueError):
                capacity.parse_channels(spec)


class MathTests(unittest.TestCase):
    def test_no_attrition_is_linear(self):
        self.assertAlmostEqual(capacity.required_monthly_adds(300, 60, 6, 0.0), 10)

    def test_example_monthly_adds(self):
        self.assertAlmostEqual(capacity.required_monthly_adds(300, 100, 6, 0.01), 20.0886, places=3)

    def test_trajectory_reaches_goal(self):
        adds = capacity.required_monthly_adds(300, 100, 6, 0.01)
        self.assertAlmostEqual(capacity.trajectory(300, adds, 6, 0.01)[-1][2], 400)

    def test_rejects_bad_attrition(self):
        with self.assertRaises(ValueError):
            capacity.required_monthly_adds(300, 100, 6, 1.0)


class PlanTests(unittest.TestCase):
    def test_example_plan(self):
        p = capacity.plan(300, 100, 6, 0.01, capacity.parse_channels(CHANNELS))
        self.assertTrue(p["feasible"])
        self.assertEqual([a["channel"].name for a in p["allocations"]],
                         ["email_nurture", "account_manager", "webinar", "workshop"])
        self.assertEqual(p["marginal"]["channel"].name, "workshop")
        self.assertAlmostEqual(p["marginal"]["clients"], 20.0886 - 18.6, places=3)

    def test_shortfall_when_capacity_is_low(self):
        p = capacity.plan(300, 100, 6, 0.01, capacity.parse_channels("email:100:0.05:1"))
        self.assertFalse(p["feasible"])
        self.assertAlmostEqual(p["shortfall"], 20.0886 - 5, places=3)
        self.assertIn("INFEASIBLE", capacity.format_plan(p))


if __name__ == "__main__":
    unittest.main()
