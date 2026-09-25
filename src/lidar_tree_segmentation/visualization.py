"""Visualization helpers for Cut Pursuit tree outputs."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


def save_segmentation_map(points, labels, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(points[:, 0], points[:, 1], c=labels, s=2, cmap="tab20")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Cut Pursuit Segmentation")
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_tree_height_map(points, labels, metrics_df, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 7))
    if len(metrics_df):
        vmin = float(metrics_df["tree_height_m"].min())
        vmax = float(metrics_df["tree_height_m"].max())

        scatter = None
        for _, row in metrics_df.iterrows():
            label = int(row["tree_id"])
            segment = points[labels == label]
            scatter = ax.scatter(
                segment[:, 0],
                segment[:, 1],
                c=np.full(len(segment), row["tree_height_m"]),
                s=2,
                cmap="viridis",
                vmin=vmin,
                vmax=vmax,
            )
        if scatter is not None:
            fig.colorbar(scatter, ax=ax, label="Tree height (m)")

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Tree Height Map")
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
