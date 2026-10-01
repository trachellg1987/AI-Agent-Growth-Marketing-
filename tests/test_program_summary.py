import tempfile
import unittest
from pathlib import Path

from tests.helpers import ROOT, program_summary

SAMPLE = ROOT / "04-tool-use-python" / "sample-vas-client-programs.csv"
HEADER = "client_id,client_type,vas_product,status,start_date,source\n"


class SampleTests(unittest.TestCase):
    def setUp(self):
        self.columns, rows = program_summary.load(SAMPLE)
        self.summary = program_summary.summarize(rows)

    def test_columns(self):
        self.assertEqual(self.columns, list(program_summary.REQUIRED_COLUMNS))

    def test_totals(self):
        self.assertEqual((self.summary["rows"], self.summary["total_active"], self.summary["total_inactive"]),
                         (12, 8, 4))

    def test_per_product_counts(self):
        counts = {p["product"]: (p["active"], p["inactive"]) for p in self.summary["products"]}
        self.assertEqual(counts["Risk Scoring Service"], (3, 1))
        self.assertEqual(counts["Card Controls API"], (1, 1))


class ValidationTests(unittest.TestCase):
    def write(self, body):
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        handle.write(body)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return handle.name

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            program_summary.load(self.write("client_id,status\nC1,active\n"))

    def test_bad_status(self):
        with self.assertRaises(ValueError):
            program_summary.load(self.write(HEADER + "C1,fintech,X,paused,2025-01-01,email\n"))

    def test_bad_date(self):
        with self.assertRaises(ValueError):
            program_summary.load(self.write(HEADER + "C1,fintech,X,active,01/02/2025,email\n"))


if __name__ == "__main__":
    unittest.main()
