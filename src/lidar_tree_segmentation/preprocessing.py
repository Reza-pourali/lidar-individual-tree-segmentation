"""Point-cloud preprocessing for the tree-segmentation pipeline."""

import numpy as np


def _validate_points(points):
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must have shape (n, 3).")
    if len(points) == 0:
        raise ValueError("point cloud is empty.")
    if not np.isfinite(points).all():
        raise ValueError("point cloud contains non-finite coordinates.")
    return points


def localize_point_cloud(points):
    """Shift XYZ coordinates so the minimum of each axis becomes zero.

    This reproduces the coordinate treatment used in the coursework. The
    resulting Z coordinate is a local height above the minimum Z in the input
    vegetation cloud; it should not be interpreted as terrain-normalized
    height unless the input has already been ground-normalized.
    """
    points = _validate_points(points)
    origin = points.min(axis=0)
    return points - origin, origin


def filter_low_height(points, min_height=0.20):
    """Remove points at or below a local-height threshold."""
    points = _validate_points(points)
    if min_height < 0:
        raise ValueError("min_height must be non-negative.")
    return points[points[:, 2] > min_height]


def voxel_downsample_centroid(points, voxel_size=0.10):
    """Downsample a point cloud by replacing each occupied voxel with its centroid.

    The original coursework kept the first point encountered in each voxel.
    Using the centroid is deterministic with respect to point order and gives
    a more representative voxel location.
    """
    points = _validate_points(points)
    if voxel_size <= 0:
        raise ValueError("voxel_size must be positive.")

    keys = np.floor(points / voxel_size).astype(np.int64)
    unique_keys, inverse = np.unique(keys, axis=0, return_inverse=True)

    counts = np.bincount(inverse)
    centroids = np.zeros((len(unique_keys), 3), dtype=np.float64)

    for dim in range(3):
        centroids[:, dim] = np.bincount(
            inverse,
            weights=points[:, dim],
            minlength=len(unique_keys),
        ) / counts

    return centroids
