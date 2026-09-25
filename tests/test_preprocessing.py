import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lidar_tree_segmentation.preprocessing import (
    filter_low_height,
    localize_point_cloud,
    voxel_downsample_centroid,
)


class TestPreprocessing(unittest.TestCase):
    def test_localize_point_cloud(self):
        points = np.array([
            [10.0, 20.0, 100.0],
            [12.0, 21.0, 104.0],
        ])
        local, origin = localize_point_cloud(points)
        np.testing.assert_allclose(origin, [10.0, 20.0, 100.0])
        np.testing.assert_allclose(local[0], [0.0, 0.0, 0.0])
        np.testing.assert_allclose(local[1], [2.0, 1.0, 4.0])

    def test_voxel_downsample_uses_centroid(self):
        points = np.array([
            [0.01, 0.01, 0.01],
            [0.09, 0.09, 0.09],
            [0.21, 0.21, 0.21],
        ])
        out = voxel_downsample_centroid(points, voxel_size=0.10)
        self.assertEqual(len(out), 2)
        np.testing.assert_allclose(out[0], [0.05, 0.05, 0.05])

    def test_low_height_filter(self):
        points = np.array([
            [0.0, 0.0, 0.10],
            [0.0, 0.0, 0.21],
        ])
        out = filter_low_height(points, 0.20)
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0, 2], 0.21)


if __name__ == "__main__":
    unittest.main()
