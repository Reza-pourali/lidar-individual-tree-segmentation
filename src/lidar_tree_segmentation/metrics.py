"""Geometric metrics for individual-tree point-cloud segments."""

import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist
from sklearn.cluster import DBSCAN
from skimage.filters import threshold_otsu


def _safe_convex_hull_area_2d(xy):
    xy = np.asarray(xy, dtype=np.float64)
    if len(xy) < 4:
        return np.nan
    try:
        return float(ConvexHull(xy).volume)  # 2D `volume` is polygon area.
    except Exception:
        return np.nan


def _safe_convex_hull_volume_3d(points):
    points = np.asarray(points, dtype=np.float64)
    if len(points) < 10:
        return np.nan
    try:
        return float(ConvexHull(points).volume)
    except Exception:
        return np.nan


def pca_elongation_ratio(xy):
    """Return sqrt(lambda_max / lambda_min) for horizontal coordinates."""
    xy = np.asarray(xy, dtype=np.float64)
    if len(xy) < 5:
        return np.nan

    centered = xy - xy.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    try:
        eigenvalues = np.sort(np.linalg.eigvalsh(cov))[::-1]
    except Exception:
        return np.nan

    if eigenvalues[1] <= 1e-12:
        return np.inf
    return float(np.sqrt(eigenvalues[0] / eigenvalues[1]))


def robust_dbh_estimation(points, z_rel, breast_height=1.30):
    """Estimate DBH using a local breast-height section and robust radius.

    Steps:
    1. Estimate a stem center from low points.
    2. Search increasingly wide slices around breast height.
    3. If enough points exist, use DBSCAN to select the cluster nearest the
       estimated stem center.
    4. Remove the outer 10% of radial distances.
    5. Return twice the 90th-percentile retained radius.
    """
    points = np.asarray(points, dtype=np.float64)
    z_rel = np.asarray(z_rel, dtype=np.float64)

    if len(points) != len(z_rel):
        raise ValueError("points and z_rel must have the same length.")
    if len(points) == 0:
        return {
            "dbh_robust_m": np.nan,
            "dbh_raw_m": np.nan,
            "section_tolerance_m": np.nan,
            "section_points": 0,
            "selected_points": None,
        }

    low_limit = min(2.0, max(0.5, 0.25 * float(np.nanmax(z_rel))))
    low_points = points[z_rel <= low_limit]

    if len(low_points) >= 10:
        base_center = np.median(low_points[:, :2], axis=0)
    else:
        base_center = np.median(points[:, :2], axis=0)

    selected = None
    used_tolerance = np.nan

    for tolerance in (0.05, 0.10, 0.20, 0.30):
        section = points[np.abs(z_rel - breast_height) < tolerance]
        if len(section) < 5:
            continue

        selected = section
        if len(section) >= 12:
            xy = section[:, :2]
            try:
                cluster_labels = DBSCAN(eps=0.35, min_samples=4).fit_predict(xy)
                valid_labels = [v for v in np.unique(cluster_labels) if v != -1]
                best_label = None
                best_distance = np.inf

                for label in valid_labels:
                    cluster_xy = xy[cluster_labels == label]
                    if len(cluster_xy) < 4:
                        continue
                    distance = np.linalg.norm(cluster_xy.mean(axis=0) - base_center)
                    if distance < best_distance:
                        best_distance = distance
                        best_label = label

                if best_label is not None:
                    selected = section[cluster_labels == best_label]
            except Exception:
                pass

        if selected is not None and len(selected) >= 5:
            used_tolerance = float(tolerance)
            break

    if selected is None or len(selected) < 2:
        return {
            "dbh_robust_m": np.nan,
            "dbh_raw_m": np.nan,
            "section_tolerance_m": np.nan,
            "section_points": 0,
            "selected_points": None,
        }

    xy = selected[:, :2]
    center = np.median(xy, axis=0)
    radius = np.linalg.norm(xy - center, axis=1)

    if len(radius) >= 8:
        limit = np.percentile(radius, 90)
        xy_clean = xy[radius <= limit]
        radius_clean = radius[radius <= limit]
    else:
        xy_clean = xy
        radius_clean = radius

    robust_dbh = (
        float(2.0 * np.percentile(radius_clean, 90))
        if len(radius_clean) >= 2
        else np.nan
    )

    try:
        raw_dbh = float(np.max(pdist(xy_clean))) if len(xy_clean) >= 2 else np.nan
    except Exception:
        raw_dbh = np.nan

    return {
        "dbh_robust_m": robust_dbh,
        "dbh_raw_m": raw_dbh,
        "section_tolerance_m": used_tolerance,
        "section_points": int(len(selected)),
        "selected_points": selected,
    }


def split_lower_structure_and_crown(points):
    """Split a segment into lower structure and crown using an Otsu height threshold."""
    points = np.asarray(points, dtype=np.float64)
    z = points[:, 2]
    z_min = float(z.min())
    z_rel = z - z_min
    height = float(z_rel.max())

    if height <= 0:
        return points.copy(), np.empty((0, 3)), 0.0

    try:
        threshold = float(threshold_otsu(z_rel))
    except Exception:
        threshold = 0.35 * height

    threshold = float(np.clip(threshold, 0.25 * height, 0.60 * height))
    lower = points[z_rel < threshold]
    crown = points[z_rel >= threshold]

    if len(lower) < 10 or len(crown) < 10:
        threshold = 0.35 * height
        lower = points[z_rel < threshold]
        crown = points[z_rel >= threshold]

    return lower, crown, threshold


def compute_tree_metrics(points, tree_id=None):
    """Compute geometric metrics for one segmented tree candidate."""
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 2:
        raise ValueError("points must have shape (n, 3) with at least two points.")

    z = points[:, 2]
    z_min = float(z.min())
    z_rel = z - z_min
    tree_height = float(z_rel.max())

    width_x = float(np.ptp(points[:, 0]))
    width_y = float(np.ptp(points[:, 1]))
    width_max = max(width_x, width_y)
    width_min = min(width_x, width_y)

    footprint_area = _safe_convex_hull_area_2d(points[:, :2])
    elongation = pca_elongation_ratio(points[:, :2])

    if np.isnan(footprint_area) or width_max <= 1e-12:
        compactness = np.nan
    else:
        compactness = float(
            footprint_area / (np.pi * (width_max / 2.0) ** 2)
        )

    lower, crown, crown_threshold = split_lower_structure_and_crown(points)

    if len(crown):
        crown_base_height = float(crown[:, 2].min() - z_min)
        crown_width = max(
            float(np.ptp(crown[:, 0])),
            float(np.ptp(crown[:, 1])),
        )
    else:
        crown_base_height = np.nan
        crown_width = np.nan

    dbh = robust_dbh_estimation(points, z_rel)

    # Explicit names avoid the misleading "BCV" label used in the coursework.
    crown_hull_volume = _safe_convex_hull_volume_3d(crown)
    lower_structure_hull_volume = _safe_convex_hull_volume_3d(lower)

    apex_index = int(np.argmax(points[:, 2]))

    return {
        "tree_id": None if tree_id is None else int(tree_id),
        "num_points": int(len(points)),
        "tree_height_m": tree_height,
        "width_x_m": width_x,
        "width_y_m": width_y,
        "max_width_m": width_max,
        "min_width_m": width_min,
        "footprint_area_m2": footprint_area,
        "compactness": compactness,
        "elongation_ratio": elongation,
        "height_width_ratio": tree_height / (width_max + 1e-12),
        "crown_width_m": crown_width,
        "crown_base_height_m": crown_base_height,
        "dbh_robust_m": dbh["dbh_robust_m"],
        "dbh_raw_m": dbh["dbh_raw_m"],
        "dbh_section_tolerance_m": dbh["section_tolerance_m"],
        "dbh_section_points": dbh["section_points"],
        "crown_hull_volume_m3": crown_hull_volume,
        "lower_structure_hull_volume_m3": lower_structure_hull_volume,
        "apex_x_m": float(points[apex_index, 0]),
        "apex_y_m": float(points[apex_index, 1]),
        "crown_threshold_m": float(crown_threshold),
    }
