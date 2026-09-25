"""Print documented results from the original Python coursework run."""

from pathlib import Path
import json
import csv


def main():
    root = Path(__file__).resolve().parents[1]

    with (root / "data" / "documented_summary.json").open(encoding="utf-8") as f:
        summary = json.load(f)

    print("Documented final configuration")
    print("Voxel size:", summary["voxel_size_m"])
    print("K neighbors:", summary["k_neighbors"])
    print("Regularization:", summary["regularization"])
    print("Z weight:", summary["z_weight"])
    print("Initial components:", summary["initial_cut_pursuit_components"])
    print("Valid tree candidates:", summary["valid_tree_candidates"])
    print("Mean tree height:", summary["mean_tree_height_m"])

    print("\nSelected trees")
    with (root / "data" / "documented_selected_tree_metrics.csv").open(
        newline="", encoding="utf-8"
    ) as f:
        for row in csv.DictReader(f):
            print(
                f"Tree {row['tree_id']}: "
                f"height={float(row['tree_height_m']):.4f} m, "
                f"crown width={float(row['crown_width_m']):.4f} m, "
                f"DBH={float(row['dbh_robust_m']):.4f} m"
            )


if __name__ == "__main__":
    main()
