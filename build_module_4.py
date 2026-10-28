"""Builds module_4_aggregations_statistics.ipynb — Aggregations, Statistics & Sorting.

Run with: python build_module_4.py
"""
from nb_utils import md, code, exercise_cells, build_notebook, save_notebook

FILENAME = "module_4_aggregations_statistics.ipynb"
TITLE = "Module 4 — Aggregations, Statistics & Sorting"

intro_cells = [
    md(
        """
## Welcome

This module is about turning an array into a number — or a handful of
numbers — that summarize it. You'll learn how to aggregate along a
specific axis, locate extremes, sort, and count unique values. By the end
you'll chain all of these together to analyze a small real-flavored
dataset.

**Learning goals**
- Aggregate with `sum`/`mean`/`std`/`min`/`max`, controlling direction with `axis`
- Locate extremes with `argmin`/`argmax` and `np.unravel_index`
- Sort arrays and get an ordering with `np.sort` / `arr.sort()` / `np.argsort`
- Count unique values with `np.unique`
- Combine these tools to analyze a dataset end to end

**Setup** — run this first.
"""
    ),
    code(
        """
import numpy as np
import matplotlib.pyplot as plt
print(np.__version__)
"""
    ),
]

lesson_cells = []

# ---------------------------------------------------------------------------
# Lesson 1
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 1 — Aggregations & the `axis` Parameter

`np.sum`, `np.mean`, `np.std`, `np.min`, `np.max` all reduce an array to
fewer numbers. Called with no `axis`, they collapse the **whole** array to
a single scalar. With `axis=0` they reduce *along rows* — one result per
**column**. With `axis=1` they reduce *along columns* — one result per
**row**.

| Call | Meaning |
|---|---|
| `arr.sum()` | one total, whole array |
| `arr.sum(axis=0)` | one total per column (walks down each column) |
| `arr.sum(axis=1)` | one total per row (walks across each row) |

Pass `keepdims=True` to keep the reduced axis as length-1 instead of
dropping it — handy when you want the result to broadcast back against the
original array.
"""
    ),
    code(
        """
grid = np.array([[1, 2, 3],
                  [4, 5, 6]])

print("whole array sum:", grid.sum())
print("column sums (axis=0):", grid.sum(axis=0))
print("row sums (axis=1):   ", grid.sum(axis=1))
print("row means, keepdims: ", grid.mean(axis=1, keepdims=True).ravel())

# keepdims=True lets you broadcast the result back against the original:
centered = grid - grid.mean(axis=1, keepdims=True)
print(centered)
"""
    ),
]

lesson_cells += exercise_cells(
    "1.1",
    "Column-normalize a matrix",
    """
Write `normalize_columns(grid)` that returns a copy of `grid` where each
**column** has been divided by that column's sum, so every column sums to
`1.0`. `grid` is a 2-D array of positive floats.
""",
    """
def normalize_columns(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
grid = np.array([[1.0, 2.0], [3.0, 2.0]])
result = normalize_columns(grid)
print("normalize_columns(grid) ->")
print(result)

expected = np.array([[0.25, 0.5], [0.75, 0.5]])
_passed = np.allclose(result.sum(axis=0), [1.0, 1.0]) and np.allclose(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Divide `grid` by `grid.sum(axis=0)` — broadcasting lines up a "
    "length-`n_cols` array against each row automatically.",
    """
def normalize_columns(grid):
    return grid / grid.sum(axis=0)
""",
)

lesson_cells += exercise_cells(
    "1.2",
    "Row-wise range",
    """
Write `row_ranges(grid)` that returns a 1-D array with, for each row, the
difference between that row's max and min value (`max - min`).
""",
    """
def row_ranges(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
grid = np.array([[1, 5, 3], [10, 2, 8]])
result = row_ranges(grid)
print("row_ranges(grid) ->")
print(result)

expected = np.array([4, 8])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`grid.max(axis=1) - grid.min(axis=1)`.",
    """
def row_ranges(grid):
    return grid.max(axis=1) - grid.min(axis=1)
""",
)

# ---------------------------------------------------------------------------
# Lesson 2
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 2 — `argmin`/`argmax` and Locating Extremes

`.max()` tells you the **value**; `.argmax()` tells you **where** it is.
Called on a flat array, `argmax` returns a single flat index. Called with
`axis` on a 2-D array, it returns one index per row/column — the position
*within that row/column*, not a flat index into the whole array.

To turn a flat index (from calling `argmax()` on a 2-D array with no
`axis`) back into `(row, col)` coordinates, use
`np.unravel_index(flat_index, arr.shape)`.
"""
    ),
    code(
        """
grid = np.array([[3, 9, 1],
                  [7, 2, 8]])

print("flat argmax:", grid.argmax())                 # index into flattened array
print("as coords:  ", np.unravel_index(grid.argmax(), grid.shape))
print("argmax per row (axis=1):", grid.argmax(axis=1))
print("argmin per column (axis=0):", grid.argmin(axis=0))
"""
    ),
]

lesson_cells += exercise_cells(
    "2.1",
    "Find the hotspot",
    """
Write `hotspot(grid)` that returns the `(row, col)` coordinates (as a tuple
of two Python ints) of the single largest value in a 2-D array.
""",
    """
def hotspot(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
grid = np.array([[1, 2], [9, 3]])
result = hotspot(grid)
print("hotspot(grid) ->")
print(result)

grid2 = np.array([[5, 1, 2], [3, 4, 9]])
result2 = hotspot(grid2)
print("hotspot(grid2) ->")
print(result2)

_passed = result == (1, 0) and result2 == (1, 2)

if not _passed:
    print()
    print("Expected: (1, 0) and (1, 2)")
""",
    "`np.unravel_index(grid.argmax(), grid.shape)` gives you the coordinates "
    "as numpy integers — wrap each in `int(...)` for plain Python ints.",
    """
def hotspot(grid):
    row, col = np.unravel_index(grid.argmax(), grid.shape)
    return (int(row), int(col))
""",
)

lesson_cells += exercise_cells(
    "2.2",
    "Best score per student",
    """
Each row of `scores` is one student's scores across several tests. Write
`best_test_per_student(scores)` that returns a 1-D array with, for each
student (row), the **index** (0-based, position within that row) of their
best test.
""",
    """
def best_test_per_student(scores):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
scores = np.array([[70, 95, 60], [88, 40, 91]])
result = best_test_per_student(scores)
print("best_test_per_student(scores) ->")
print(result)

expected = np.array([1, 2])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "You want one argmax per row — that's `axis=1`.",
    """
def best_test_per_student(scores):
    return scores.argmax(axis=1)
""",
)

# ---------------------------------------------------------------------------
# Lesson 3
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 3 — Sorting

- `np.sort(arr)` returns a **sorted copy**; `arr.sort()` sorts **in place**
  and returns `None`.
- `np.argsort(arr)` doesn't sort anything — it returns the **indices** that
  *would* sort the array. This is the tool you reach for when you need to
  sort one array "by" another (e.g. sort names by score).
- Both accept `axis` on 2-D arrays, sorting each row/column independently
  (each row sorted on its own does **not** sort the matrix as a whole).
"""
    ),
    code(
        """
arr = np.array([3, 1, 4, 1, 5])
print("np.sort (copy):   ", np.sort(arr), "| original untouched:", arr)

order = np.argsort(arr)
print("argsort indices:  ", order)
print("names sorted by score, using argsort as a key:")
names = np.array(["c", "a", "d", "b", "e"])
scores = np.array([30, 90, 10, 90, 50])
print(names[np.argsort(scores)])
"""
    ),
]

lesson_cells += exercise_cells(
    "3.1",
    "Rank the runners",
    """
Write `top_n_names(names, times, n)` that returns the `n` names (as a NumPy
array of strings) belonging to the **smallest** `n` values in `times` —
i.e. the fastest `n` runners — ordered from fastest to slowest. `names`
and `times` are same-length 1-D arrays.
""",
    """
def top_n_names(names, times, n):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
names = np.array(["alice", "bob", "cara", "dan"])
times = np.array([12.3, 10.1, 15.0, 9.8])
result = top_n_names(names, times, 2)
print("top_n_names(names, times, 2) ->")
print(result)

expected = ["dan", "bob"]
_passed = list(result) == expected

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`np.argsort(times)` gives ascending order (fastest first, since lower "
    "time is better); slice the first `n` of `names[order]`.",
    """
def top_n_names(names, times, n):
    order = np.argsort(times)
    return names[order][:n]
""",
)

lesson_cells += exercise_cells(
    "3.2",
    "Sort each row independently",
    """
Write `sort_rows_desc(grid)` that returns a copy of `grid` with each row
sorted in **descending** order (columns no longer correspond to anything
meaningful across rows — that's expected).
""",
    """
def sort_rows_desc(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
grid = np.array([[3, 1, 2], [9, 7, 8]])
result = sort_rows_desc(grid)
print("sort_rows_desc(grid) ->")
print(result)

expected = np.array([[3, 2, 1], [9, 8, 7]])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Sort ascending along `axis=1` with `np.sort`, then reverse each row "
    "with `[:, ::-1]`.",
    """
def sort_rows_desc(grid):
    return np.sort(grid, axis=1)[:, ::-1]
""",
)

# ---------------------------------------------------------------------------
# Lesson 4
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 4 — Unique Values & Counting

`np.unique(arr)` returns the sorted distinct values in an array. Pass
`return_counts=True` to also get how many times each value occurred, or
`return_index=True` to get the index of each value's **first** occurrence.
Both are commonly used together with the unique values to build a simple
frequency table.
"""
    ),
    code(
        """
votes = np.array(["cat", "dog", "cat", "cat", "fox", "dog"])

values, counts = np.unique(votes, return_counts=True)
print("values:", values)
print("counts:", counts)

for value, count in zip(values, counts):
    print(f"{value}: {count}")
"""
    ),
]

lesson_cells += exercise_cells(
    "4.1",
    "Most common value",
    """
Write `most_common(arr)` that returns the most frequently occurring value
in a 1-D array. Assume there's a unique winner (no ties to break).
""",
    """
def most_common(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = most_common(np.array([1, 2, 2, 3, 2]))
print("most_common(np.array([1, 2, 2, 3, 2])) ->")
print(result)

result2 = most_common(np.array(["a", "b", "b", "a", "a"]))
print("most_common(np.array(['a', 'b', 'b', 'a', 'a'])) ->")
print(result2)

_passed = result == 2 and result2 == "a"

if not _passed:
    print()
    print("Expected: 2 and 'a'")
""",
    "`np.unique(arr, return_counts=True)` gives you `(values, counts)` — "
    "find the index of the largest count with `.argmax()` and index into "
    "`values`.",
    """
def most_common(arr):
    values, counts = np.unique(arr, return_counts=True)
    return values[counts.argmax()]
""",
)

lesson_cells += exercise_cells(
    "4.2",
    "Values seen exactly once",
    """
Write `singletons(arr)` that returns, sorted, the values in a 1-D array
that occur **exactly once**.
""",
    """
def singletons(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = singletons(np.array([1, 2, 2, 3, 4, 4, 4, 5]))
print("singletons(np.array([1, 2, 2, 3, 4, 4, 4, 5])) ->")
print(result)

expected = np.array([1, 3, 5])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Get `(values, counts)` from `np.unique(..., return_counts=True)`, then "
    "boolean-index `values` with `counts == 1`.",
    """
def singletons(arr):
    values, counts = np.unique(arr, return_counts=True)
    return values[counts == 1]
""",
)

# ---------------------------------------------------------------------------
# Lesson 5 — capstone
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 5 — Putting It Together: Analyzing Daily Temperatures

Let's generate a month of synthetic daily high temperatures (°C) and use
everything from this module — aggregation, `argmin`/`argmax`, sorting, and
counting — to analyze it in one exercise.
"""
    ),
    code(
        """
rng = np.random.default_rng(seed=7)
days = np.arange(1, 31)
# a gentle seasonal wave plus daily noise, just to have realistic-looking data
temps = 18 + 4 * np.sin(np.linspace(0, np.pi, 30)) + rng.normal(0, 1.5, size=30)
temps = np.round(temps, 1)

plt.figure(figsize=(8, 3))
plt.plot(days, temps, marker="o")
plt.xlabel("Day of month")
plt.ylabel("High temp (°C)")
plt.title("Synthetic daily high temperatures")
plt.show()

print(temps)
"""
    ),
]

lesson_cells += exercise_cells(
    "5.1",
    "Temperature report",
    """
Write `temperature_report(temps, threshold)` that takes the 1-D array of
daily temperatures and a `threshold` value, and returns a dict with:

- `"hottest_day"`: the **1-based** day number (int) with the highest temp
  (day 1 = `temps[0]`)
- `"coldest_day"`: the 1-based day number (int) with the lowest temp
- `"mean"`: the mean temperature (float)
- `"std"`: the standard deviation (float)
- `"days_above_threshold"`: how many days exceeded `threshold` (int)
- `"sorted_desc"`: the temperatures sorted from hottest to coldest (array)

Use `argmax`/`argmin`, `mean`/`std`, boolean indexing + `.sum()` (or
`np.count_nonzero`), and `np.sort` — don't write a loop.
""",
    """
def temperature_report(temps, threshold):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
temps_demo = np.array([10.0, 25.0, 5.0, 18.0, 20.0])
result = temperature_report(temps_demo, threshold=19.0)
print("temperature_report(temps_demo, threshold=19.0) ->")
print(result)

expected = {
    "hottest_day": 2,
    "coldest_day": 3,
    "mean": float(temps_demo.mean()),
    "std": float(temps_demo.std()),
    "days_above_threshold": 2,
    "sorted_desc": np.array([25.0, 20.0, 18.0, 10.0, 5.0]),
}
_passed = (
    isinstance(result, dict)
    and result.get("hottest_day") == expected["hottest_day"]
    and result.get("coldest_day") == expected["coldest_day"]
    and np.isclose(result.get("mean", np.nan), expected["mean"])
    and np.isclose(result.get("std", np.nan), expected["std"])
    and result.get("days_above_threshold") == expected["days_above_threshold"]
    and np.array_equal(result.get("sorted_desc"), expected["sorted_desc"])
)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`temps.argmax()` is a 0-based flat index — add 1 to get the day number. "
    "`(temps > threshold).sum()` counts how many exceed the threshold. "
    "`np.sort(temps)[::-1]` sorts hottest-first.",
    """
def temperature_report(temps, threshold):
    return {
        "hottest_day": int(temps.argmax()) + 1,
        "coldest_day": int(temps.argmin()) + 1,
        "mean": float(temps.mean()),
        "std": float(temps.std()),
        "days_above_threshold": int((temps > threshold).sum()),
        "sorted_desc": np.sort(temps)[::-1],
    }
""",
)

# ---------------------------------------------------------------------------
# Wrap-up
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## 🎯 Key Takeaways

- `axis=0` reduces **down** columns (one result per column); `axis=1`
  reduces **across** rows (one result per row).
- `argmin`/`argmax` locate *where* an extreme value is; `np.unravel_index`
  turns a flat index back into `(row, col)` coordinates.
- `np.sort` returns a copy, `arr.sort()` sorts in place, and `np.argsort`
  gives you an ordering you can apply to another array.
- `np.unique(..., return_counts=True)` is your go-to for frequency
  analysis without writing a loop.
- Real analysis is usually a short **chain** of these tools, not a single
  call.

Next up: **Module 5 — Linear Algebra & Random**, where you'll work with
vectors, matrices, and NumPy's modern random number generator.
"""
    )
]

nb = build_notebook(TITLE, FILENAME, intro_cells, lesson_cells)
save_notebook(nb, FILENAME)
print(f"Wrote {FILENAME} with {len(nb['cells'])} cells.")
