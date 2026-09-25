import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lidar_tree_segmentation.metrics import (
    compute_tree_metrics,
    robust_dbh_estimation,
)


class TestMetrics(unittest.TestCase):
    def test_robust_dbh_on_synthetic_cylinder(self):
        rng = np.random.default_rng(7)
        theta = np.linspace(0, 2 * np.pi, 120, endpoint=False)
        radius = 0.20

        x = radius * np.cos(theta) + rng.normal(0, 0.004, len(theta))
        y = radius * np.sin(theta) + rng.normal(0, 0.004, len(theta))
        z = np.full(len(theta), 1.30) + rng.normal(0, 0.01, len(theta))
        section = np.column_stack((x, y, z))

        lower = np.column_stack((
            rng.normal(0, 0.08, 80),
            rng.normal(0, 0.08, 80),
            rng.uniform(0.0, 1.0, 80),
        ))
        points = np.vstack((lower, section))
        z_rel = points[:, 2] - points[:, 2].min()

        result = robust_dbh_estimation(points, z_rel)
        self.assertTrue(np.isfinite(result["dbh_robust_m"]))
        self.assertAlmostEqual(result["dbh_robust_m"], 0.40, delta=0.08)

    def test_compute_tree_metrics_uses_explicit_volume_names(self):
        rng = np.random.default_rng(2)
        points = np.column_stack((
            rng.normal(0, 0.5, 500),
            rng.normal(0, 0.5, 500),
            rng.uniform(0, 8, 500),
        ))
        result = compute_tree_metrics(points, tree_id=5)
        self.assertIn("crown_hull_volume_m3", result)
        self.assertIn("lower_structure_hull_volume_m3", result)
        self.assertNotIn("BCV_m3", result)


if __name__ == "__main__":
    unittest.main()
