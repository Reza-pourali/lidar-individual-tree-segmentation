# Documented Python Results

## Point-cloud reduction

| Stage | Points |
| --- | ---: |
| Raw input | 1,060,218 |
| After low-height filter | 1,016,747 |
| After 0.1 m voxelization | 72,216 |

## Cut Pursuit parameter sweep

| Test | K | Regularization | Z weight | Initial components | Valid segments | Mean height | Max height | Heuristic score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 12 | 1.5 | 0.2 | 47 | 22 | 6.6280 m | 12.7309 m | 9.8231 |
| 2 | 16 | 2.5 | 0.2 | 31 | 14 | 7.4137 m | 12.7309 m | 10.5374 |
| 3 | 20 | 3.5 | 0.2 | 26 | 12 | 7.3810 m | 12.7309 m | 10.3910 |

The coursework selected Test 2.

## Final documented configuration

- voxel size: 0.1 m
- K neighbors: 16
- regularization: 2.5
- Z weight: 0.2
- initial Cut Pursuit components: 31
- valid tree candidates after filtering: 12
- mean candidate-tree height: 7.8189 m
- minimum height: 2.4623 m
- maximum height: 12.7309 m
- height standard deviation: 2.8553 m

## Selected trees

| Tree ID | Points | Height | Crown width | Crown-base height | Robust DBH |
| --- | ---: | ---: | ---: | ---: | ---: |
| 18 | 27,386 | 10.4037 m | 11.1954 m | 4.8565 m | 0.6117 m |
| 7 | 5,228 | 12.7309 m | 2.2285 m | 6.7908 m | 0.2304 m |
| 8 | 7,257 | 9.2804 m | 4.3390 m | 3.9343 m | 0.2160 m |
| 0 | 3,216 | 9.2394 m | 2.3842 m | 5.0716 m | 0.2514 m |

The coursework also reported `CV` and `BCV` values. Those historical fields
are preserved in `data/documented_selected_tree_metrics.csv`, but the refactor
does not reuse the `BCV` name because the original implementation computed it
from the lower/trunk subset rather than from a crown bounding volume.
