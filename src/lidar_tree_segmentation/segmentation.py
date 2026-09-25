"""Cut Pursuit adapter and segmentation utilities."""

import numpy as np


def make_features(points, z_weight=0.20):
    """Standardize XYZ and downweight Z before graph segmentation."""
    points = np.asarray(points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must have shape (n, 3).")
    if z_weight <= 0:
        raise ValueError("z_weight must be positive.")

    mean = points.mean(axis=0)
    std = points.std(axis=0)
    std[std < 1e-12] = 1.0

    features = (points - mean) / std
    features[:, 2] *= z_weight
    return features


def components_to_labels(components, n_points):
    """Convert common Cut Pursuit outputs to a dense integer label vector."""
    if isinstance(components, np.ndarray):
        if components.ndim == 1 and len(components) == n_points:
            return components.astype(int, copy=False)

    if isinstance(components, (list, tuple)):
        # Some backends return a label array as one element of a tuple.
        for item in components:
            if isinstance(item, np.ndarray) and item.ndim == 1 and len(item) == n_points:
                return item.astype(int, copy=False)

        # Other backends return a list of point-index arrays.
        labels = np.full(n_points, -1, dtype=int)
        assigned = False
        for component_id, component in enumerate(components):
            arr = np.asarray(component)
            if arr.ndim != 1 or not np.issubdtype(arr.dtype, np.integer):
                continue
            if len(arr) == 0:
                continue
            if arr.min() < 0 or arr.max() >= n_points:
                continue
            labels[arr.astype(int)] = component_id
            assigned = True

        if assigned:
            return labels

    raise RuntimeError("Cut Pursuit output could not be converted to labels.")


def load_cut_pursuit_backend():
    """Load the external backend used by the original coursework.

    The repository does not vendor the course-specific `cut_pursuit` module.
    A compatible module must expose:

        perform_cut_pursuit(k_neighbors, regularization, features)
    """
    try:
        from cut_pursuit import perform_cut_pursuit
    except ImportError as exc:
        raise ImportError(
            "The external `cut_pursuit` backend is not installed. "
            "Install/provide the same backend used for the coursework, "
            "or pass a compatible backend callable explicitly."
        ) from exc
    return perform_cut_pursuit


def run_cut_pursuit(
    points,
    k_neighbors=16,
    regularization=2.5,
    z_weight=0.20,
    backend=None,
):
    """Run the Cut Pursuit backend and return dense segment labels."""
    if k_neighbors < 1:
        raise ValueError("k_neighbors must be positive.")
    if regularization <= 0:
        raise ValueError("regularization must be positive.")

    features = make_features(points, z_weight=z_weight)
    backend = backend or load_cut_pursuit_backend()
    components = backend(k_neighbors, regularization, features)
    return components_to_labels(components, len(points))


def segmentation_diagnostics(points, labels, min_points=150):
    """Return basic segment statistics for parameter-sweep diagnostics."""
    points = np.asarray(points, dtype=np.float64)
    labels = np.asarray(labels)

    rows = []
    for label in np.unique(labels):
        if label < 0:
            continue
        segment = points[labels == label]
        if len(segment) < min_points:
            continue

        height = float(np.ptp(segment[:, 2]))
        width_x = float(np.ptp(segment[:, 0]))
        width_y = float(np.ptp(segment[:, 1]))
        rows.append({
            "segment_id": int(label),
            "num_points": int(len(segment)),
            "height_m": height,
            "max_width_m": max(width_x, width_y),
        })
    return rows
