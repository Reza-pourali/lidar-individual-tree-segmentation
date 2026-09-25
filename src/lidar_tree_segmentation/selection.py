"""Geometric filtering and quality-based tree selection."""

import numpy as np
import pandas as pd


def filter_tree_candidates(
    metrics,
    min_points=150,
    min_height_m=2.0,
    min_width_m=0.5,
    max_width_m=18.0,
    max_elongation=5.5,
    dbh_range_m=(0.03, 1.30),
    max_dbh_crown_ratio=0.35,
):
    """Apply geometric plausibility filters to segment metrics."""
    df = pd.DataFrame(metrics).copy()
    if len(df) == 0:
        return df

    required = {
        "num_points", "tree_height_m", "max_width_m",
        "elongation_ratio", "dbh_robust_m", "crown_width_m",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing metric columns: {sorted(missing)}")

    valid = df[
        (df["num_points"] >= min_points)
        & (df["tree_height_m"] >= min_height_m)
        & (df["max_width_m"] >= min_width_m)
        & (df["max_width_m"] <= max_width_m)
    ].copy()

    valid = valid[
        valid["elongation_ratio"].isna()
        | (valid["elongation_ratio"] <= max_elongation)
    ].copy()

    low_dbh, high_dbh = dbh_range_m
    valid = valid[
        valid["dbh_robust_m"].isna()
        | (
            (valid["dbh_robust_m"] >= low_dbh)
            & (valid["dbh_robust_m"] <= high_dbh)
        )
    ].copy()

    ratio = valid["dbh_robust_m"] / (valid["crown_width_m"] + 1e-12)
    valid = valid[
        ratio.isna() | (ratio <= max_dbh_crown_ratio)
    ].copy()

    return valid.reset_index(drop=True)


def _normalize_series(series):
    series = series.astype(float)
    finite = series[np.isfinite(series)]
    if len(finite) == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    span = finite.max() - finite.min()
    if span < 1e-12:
        return pd.Series(np.ones(len(series)), index=series.index)
    return (series - finite.min()) / span


def score_tree_candidates(candidate_df):
    """Compute the documented-style quality score for candidate ranking.

    This is a heuristic ranking score, not an accuracy metric.
    """
    df = candidate_df.copy()
    if len(df) == 0:
        df["quality_score"] = []
        return df

    df["height_n"] = _normalize_series(df["tree_height_m"])
    df["points_n"] = _normalize_series(df["num_points"])

    compactness = df["compactness"].astype(float)
    compactness = compactness.fillna(compactness.median())
    df["compactness_n"] = np.clip(compactness, 0, 1)

    elongation = df["elongation_ratio"].fillna(1.0)
    df["elongation_penalty"] = np.clip((elongation - 1.0) / 5.0, 0, 1)

    dbh = df["dbh_robust_m"]
    dbh_score = np.full(len(df), 0.6)
    dbh_score[(dbh >= 0.05) & (dbh <= 0.90)] = 1.0
    dbh_score[(dbh > 0.90) & (dbh <= 1.30)] = 0.6
    df["dbh_score"] = dbh_score

    df["width_penalty"] = np.clip(
        (df["max_width_m"] - 10.0) / 8.0,
        0,
        1,
    )

    df["quality_score"] = (
        0.35 * df["height_n"]
        + 0.20 * df["points_n"]
        + 0.15 * df["compactness_n"]
        + 0.20 * df["dbh_score"]
        - 0.15 * df["elongation_penalty"]
        - 0.10 * df["width_penalty"]
    )

    return df.sort_values("quality_score", ascending=False).reset_index(drop=True)


def select_spatially_separated(candidate_df, n_select=4, min_distance_m=4.0):
    """Select high-scoring candidates while enforcing XY separation."""
    if n_select < 1:
        raise ValueError("n_select must be positive.")

    df = candidate_df.copy()
    required = {"x_center", "y_center"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing coordinate columns: {sorted(missing)}")

    selected_rows = []
    for _, row in df.iterrows():
        center = np.array([row["x_center"], row["y_center"]], dtype=float)

        if all(
            np.linalg.norm(
                center
                - np.array([s["x_center"], s["y_center"]], dtype=float)
            ) >= min_distance_m
            for s in selected_rows
        ):
            selected_rows.append(row)

        if len(selected_rows) == n_select:
            break

    return pd.DataFrame(selected_rows).reset_index(drop=True)
