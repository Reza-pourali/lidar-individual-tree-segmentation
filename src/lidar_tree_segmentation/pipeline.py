"""End-to-end orchestration for the tree-segmentation workflow."""

from dataclasses import dataclass
import pandas as pd
import numpy as np

from .metrics import compute_tree_metrics
from .preprocessing import (
    filter_low_height,
    localize_point_cloud,
    voxel_downsample_centroid,
)
from .segmentation import run_cut_pursuit
from .selection import (
    filter_tree_candidates,
    score_tree_candidates,
)


@dataclass(frozen=True)
class PipelineConfig:
    min_low_height_m: float = 0.20
    voxel_size_m: float = 0.10
    k_neighbors: int = 16
    regularization: float = 2.5
    z_weight: float = 0.20


def run_pipeline(xyz_raw, config=PipelineConfig(), backend=None):
    """Run preprocessing, segmentation, metrics, filtering, and scoring."""
    local_xyz, origin = localize_point_cloud(xyz_raw)
    filtered = filter_low_height(local_xyz, config.min_low_height_m)
    voxelized = voxel_downsample_centroid(filtered, config.voxel_size_m)

    labels = run_cut_pursuit(
        voxelized,
        k_neighbors=config.k_neighbors,
        regularization=config.regularization,
        z_weight=config.z_weight,
        backend=backend,
    )

    rows = []
    for label in np.unique(labels):
        if label < 0:
            continue
        segment = voxelized[labels == label]
        if len(segment) < 50:
            continue

        row = compute_tree_metrics(segment, tree_id=int(label))
        row["x_center"] = float(segment[:, 0].mean())
        row["y_center"] = float(segment[:, 1].mean())
        rows.append(row)

    all_metrics = pd.DataFrame(rows)
    valid = filter_tree_candidates(all_metrics)
    ranked = score_tree_candidates(valid)

    return {
        "origin": origin,
        "filtered_points": filtered,
        "voxelized_points": voxelized,
        "labels": labels,
        "all_metrics": all_metrics,
        "valid_candidates": ranked,
    }
