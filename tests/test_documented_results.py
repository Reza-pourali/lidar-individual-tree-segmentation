import csv
import json
import unittest
from pathlib import Path


class TestDocumentedResults(unittest.TestCase):
    def test_final_configuration_and_selected_trees(self):
        root = Path(__file__).resolve().parents[1]

        with (root / "data" / "documented_summary.json").open(encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["k_neighbors"], 16)
        self.assertAlmostEqual(summary["regularization"], 2.5)
        self.assertAlmostEqual(summary["z_weight"], 0.2)
        self.assertEqual(summary["selected_tree_ids"], [18, 7, 8, 0])

        with (root / "data" / "documented_selected_tree_metrics.csv").open(
            newline="", encoding="utf-8"
        ) as f:
            rows = list(csv.DictReader(f))

        self.assertEqual(len(rows), 4)
        tallest = max(rows, key=lambda r: float(r["tree_height_m"]))
        self.assertEqual(int(tallest["tree_id"]), 7)
        self.assertAlmostEqual(float(tallest["tree_height_m"]), 12.7309)


if __name__ == "__main__":
    unittest.main()
