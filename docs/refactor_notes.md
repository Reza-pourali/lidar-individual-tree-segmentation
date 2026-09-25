# Refactor Notes

This repository is a cleaned, application-ready refactor of the Python
individual-tree extraction workflow used in the coursework.

## Changes made before publication

### 1. Removed hard-coded local paths

The original script searched a fixed Windows directory. The public version
uses command-line paths and reusable functions.

### 2. English-only source code and documentation

All Persian comments and report-only text were removed from the public source.

### 3. Clearer height terminology

The coursework subtracts the minimum XYZ coordinate of the input vegetation
cloud. This produces a local Z coordinate, but it is not automatically a
terrain-normalized height if the terrain is sloped.

The public repository therefore describes this value as **local height above
the minimum input Z** unless the input is already ground-normalized.

### 4. Voxel centroid instead of first-point sampling

The original downsampling kept the first point encountered in every 0.1 m
voxel. The public implementation replaces each occupied voxel with its
centroid, which is less sensitive to input point order.

### 5. Cut Pursuit backend isolated behind an adapter

The coursework used an external module exposing:

```python
perform_cut_pursuit(k_neighbors, regularization, features)
```

That course-specific backend is not bundled here. The adapter supports the
same interface and can also accept an injected compatible backend.

### 6. Misleading BCV label removed from the refactored metrics

In the original code:

- `CV` was the convex-hull volume of the crown points.
- `BCV` was computed as the convex-hull volume of the lower/trunk subset.

Therefore `BCV` was not actually a bounding crown volume.

The public implementation uses explicit names instead:

- `crown_hull_volume_m3`
- `lower_structure_hull_volume_m3`

The historical `coursework_cv_m3` and `coursework_bcv_m3` values are retained
only in the documented-results CSV so the original report remains traceable.

### 7. Heuristic scores are labeled as heuristics

The parameter-sweep score and tree quality score are ranking heuristics, not
accuracy metrics. The public documentation makes that distinction explicit.

## Reproducibility limitation

The original vegetation LAS file and the exact Cut Pursuit backend are not
redistributed with this repository. Therefore the exact segmentation cannot be
recomputed from the public repository alone.

The original numerical results and Python-generated figures are preserved as
documented coursework outputs, while the refactored geometry, preprocessing,
selection, and adapter code is covered by unit tests.
