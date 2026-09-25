"""Run the individual-tree Cut Pursuit pipeline on a vegetation LAS file."""

from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lidar_tree_segmentation.io import read_las_xyz
from lidar_tree_segmentation.pipeline import PipelineConfig, run_pipeline
from lidar_tree_segmentation.visualization import (
    save_segmentation_map,
    save_tree_height_map,
)


def parse_args():
    p = argparse.ArgumentParser(
        description="Segment individual trees and extract structural metrics."
    )
    p.add_argument("input_las")
    p.add_argument("--output-dir", default="outputs")
    p.add_argument("--min-height", type=float, default=0.20)
    p.add_argument("--voxel-size", type=float, default=0.10)
    p.add_argument("--k-neighbors", type=int, default=16)
    p.add_argument("--regularization", type=float, default=2.5)
    p.add_argument("--z-weight", type=float, default=0.20)
    return p.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    xyz = read_las_xyz(args.input_las)
    config = PipelineConfig(
        min_low_height_m=args.min_height,
        voxel_size_m=args.voxel_size,
        k_neighbors=args.k_neighbors,
        regularization=args.regularization,
        z_weight=args.z_weight,
    )

    result = run_pipeline(xyz, config=config)

    result["all_metrics"].to_csv(output_dir / "all_segment_metrics.csv", index=False)
    result["valid_candidates"].to_csv(output_dir / "valid_tree_candidates.csv", index=False)

    save_segmentation_map(
        result["voxelized_points"],
        result["labels"],
        output_dir / "segmentation.png",
    )
    save_tree_height_map(
        result["voxelized_points"],
        result["labels"],
        result["valid_candidates"],
        output_dir / "tree_height_map.png",
    )

    print(f"Raw points: {len(xyz):,}")
    print(f"After low-height filtering: {len(result['filtered_points']):,}")
    print(f"After voxelization: {len(result['voxelized_points']):,}")
    print(f"Valid tree candidates: {len(result['valid_candidates']):,}")


if __name__ == "__main__":
    main()
