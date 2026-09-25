"""LAS input/output helpers."""

from pathlib import Path
import numpy as np


def read_las_xyz(path):
    """Read XYZ coordinates from a LAS/LAZ file."""
    try:
        import laspy
    except ImportError as exc:
        raise ImportError(
            "LAS I/O requires laspy. Install project dependencies first."
        ) from exc

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    las = laspy.read(path)
    xyz = np.column_stack((las.x, las.y, las.z)).astype(np.float64)
    return xyz
