import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lidar_tree_segmentation.segmentation import (
    components_to_labels,
    make_features,
    run_cut_pursuit,
)


class TestSegmentationUtilities(unittest.TestCase):
    def test_components_to_labels_from_component_list(self):
        components = [
            np.array([0, 2], dtype=int),
            np.array([1, 3], dtype=int),
        ]
        labels = components_to_labels(components, 4)
        np.testing.assert_array_equal(labels, [0, 1, 0, 1])

    def test_feature_z_weight(self):
        points = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 2.0, 4.0],
            [2.0, 4.0, 8.0],
        ])
        features = make_features(points, z_weight=0.2)
        self.assertAlmostEqual(features[:, 2].std(), 0.2, places=6)

    def test_backend_injection(self):
        points = np.array([
            [0.0, 0.0, 0.0],
            [0.1, 0.0, 1.0],
            [5.0, 5.0, 0.0],
            [5.1, 5.0, 1.0],
        ])

        def fake_backend(k, regularization, features):
            return [
                np.array([0, 1], dtype=int),
                np.array([2, 3], dtype=int),
            ]

        labels = run_cut_pursuit(points, backend=fake_backend)
        np.testing.assert_array_equal(labels, [0, 0, 1, 1])


if __name__ == "__main__":
    unittest.main()
