# Cut Pursuit Backend

The original coursework imported:

```python
from cut_pursuit import perform_cut_pursuit
```

and called:

```python
perform_cut_pursuit(k_neighbors, regularization, features)
```

The exact backend package/source used in the course environment was not
included with the submitted project files, so it is not vendored or guessed in
this public repository.

The adapter in `segmentation.py` supports either:

1. a locally installed module named `cut_pursuit` exposing
   `perform_cut_pursuit`, or
2. an explicitly injected callable with the same argument signature.

All other preprocessing, metrics, candidate filtering, selection, and
documented-result utilities work independently of that backend.
