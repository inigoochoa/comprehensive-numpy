"""Builds module_3_operations_broadcasting.ipynb — Array Operations & Broadcasting.

Run with: python build_module_3.py
"""
from nb_utils import md, code, exercise_cells, build_notebook, save_notebook

FILENAME = "module_3_operations_broadcasting.ipynb"
TITLE = "Module 3 — Array Operations & Broadcasting"

intro_cells = [
    md(
        """
## Welcome

This module is the heart of "thinking in NumPy." You'll learn what a ufunc
actually is, the broadcasting rules that let arrays of different shapes
combine without you writing a single loop, and how to spot — and fix — code
that's secretly looping in disguise.

**Learning goals**
- Explain what a universal function (ufunc) is and why operators are ufuncs in disguise
- Apply the three broadcasting rules to predict the output shape of an operation
- Rewrite loop-based numeric code as vectorized NumPy
- Use comparison/logical ufuncs and `np.where` for vectorized conditionals
- Build pairwise/outer computations with broadcasting instead of nested loops
- Recognize that `np.vectorize` is a convenience, not a performance tool

**Setup** — run this first.
"""
    ),
    code(
        """
import numpy as np
import time
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
## Lesson 1 — Universal Functions (ufuncs)

A **ufunc** is a function that operates elementwise on arrays, implemented
in compiled C, supporting broadcasting, type casting, and more. Most of the
math you already use is a ufunc: `arr + 1` is shorthand for
`np.add(arr, 1)`, and `arr1 * arr2` is shorthand for `np.multiply(arr1, arr2)`.

| Category | Examples |
|---|---|
| Unary (one array in) | `np.sqrt`, `np.exp`, `np.log`, `np.abs`, `np.negative` |
| Binary (two arrays in) | `np.add`, `np.subtract`, `np.multiply`, `np.divide`, `np.power` |

Because ufuncs are just functions, you can call them directly when you want
to pass extra keyword arguments (like `out=` to write into an existing
array) that an operator like `+` doesn't give you access to.
"""
    ),
    code(
        """
a = np.array([1.0, 4.0, 9.0, 16.0])

print(a + 1)              # operator form
print(np.add(a, 1))       # explicit ufunc form -- identical result

print(np.sqrt(a))         # unary ufunc
print(np.multiply(a, 2))  # binary ufunc
"""
    ),
]

lesson_cells += exercise_cells(
    "1.1",
    "Operators in disguise",
    """
Write `same_result(a, b)` that returns `True` if `a + b` (operator form) and
`np.add(a, b)` (explicit ufunc form) produce exactly equal arrays for the
given inputs, `False` otherwise. Use this to convince yourself they're
always the same operation.
""",
    """
def same_result(a, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = same_result(np.array([1, 2, 3]), np.array([4, 5, 6]))
print("same_result(np.array([1, 2, 3]), np.array([4, 5, 6])) ->")
print(result)

_passed = (
    result is True
    and same_result(np.array([1.5, 2.5]), np.array([0.5, 0.5])) is True
)

if not _passed:
    print()
    print("Expected: True")
""",
    "Use `np.array_equal` to compare `a + b` with `np.add(a, b)`, and wrap the "
    "result in `bool(...)` so you return a plain Python bool.",
    """
def same_result(a, b):
    return bool(np.array_equal(a + b, np.add(a, b)))
""",
)

lesson_cells += exercise_cells(
    "1.2",
    "Normalize with ufuncs only",
    """
Write `rescale(arr)` that maps every value of a float array into the
`[0, 1]` range using the formula `(x - min) / (max - min)`, using only
ufuncs/array ops (`.min()`, `.max()`, `-`, `/`) — no Python loop.
""",
    """
def rescale(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = rescale(np.array([0.0, 5.0, 10.0]))
print("rescale(np.array([0.0, 5.0, 10.0])) ->")
print(result)

expected = np.array([0.0, 0.5, 1.0])
_passed = np.allclose(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`arr.min()` and `arr.max()` give you scalars; subtract and divide the "
    "whole array by them at once.",
    """
def rescale(arr):
    lo, hi = arr.min(), arr.max()
    return (arr - lo) / (hi - lo)
""",
)

# ---------------------------------------------------------------------------
# Lesson 2
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 2 — Broadcasting Rules

Broadcasting lets NumPy combine arrays of *different* shapes without you
copying data to make them match. The rule set, applied by comparing shapes
from the **right**:

1. If the two shapes have a different number of dimensions, pad the smaller
   shape with `1`s on the **left** until they match.
2. Two dimensions are compatible if they're equal, **or** one of them is `1`
   (the size-1 dimension is stretched to match the other).
3. If any pair of dimensions is neither equal nor `1`, broadcasting fails
   with a `ValueError`.
"""
    ),
    code(
        """
# (3,) + scalar -> scalar broadcasts to every element
print(np.array([1, 2, 3]) + 10)

# (3,1) + (1,4) -> (3,4): both arrays stretch along their size-1 axis
col = np.array([[1], [2], [3]])        # shape (3, 1)
row = np.array([[10, 20, 30, 40]])     # shape (1, 4)
print(col + row)
print((col + row).shape)
"""
    ),
    code(
        """
# A genuine mismatch: (3,) and (4,) share no size-1 dimension to stretch.
try:
    np.array([1, 2, 3]) + np.array([1, 2, 3, 4])
except ValueError as e:
    print("ValueError:", e)
"""
    ),
]

lesson_cells += exercise_cells(
    "2.1",
    "Predict, then verify",
    """
Write `broadcast_shape(shape_a, shape_b)` that takes two shape **tuples**
and returns the resulting broadcast shape as a tuple, by actually creating
`np.zeros` arrays of those shapes, adding them, and reading off `.shape`.
If broadcasting is impossible, return `None` instead of raising.
""",
    """
def broadcast_shape(shape_a, shape_b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = broadcast_shape((3, 1), (1, 4))
print("broadcast_shape((3, 1), (1, 4)) ->")
print(result)

_passed = (
    result == (3, 4)
    and broadcast_shape((5,), (1,)) == (5,)
    and broadcast_shape((3,), (4,)) is None
)

if not _passed:
    print()
    print("Expected: (3, 4)")
""",
    "Wrap the addition in a `try/except ValueError` and return `None` in the "
    "`except` branch; otherwise return `(a + b).shape`.",
    """
def broadcast_shape(shape_a, shape_b):
    try:
        result = np.zeros(shape_a) + np.zeros(shape_b)
        return result.shape
    except ValueError:
        return None
""",
)

lesson_cells += [
    md(
        """
A quick preview before this next exercise — Module 4 covers aggregations
and the `axis` parameter in full, but you need one piece of it now:
`matrix.mean(axis=1)` averages across axis 1 (the columns), collapsing each
row down to a single number, so a `(3, 4)` matrix becomes a `(3,)` array of
row means. Passing `keepdims=True` keeps that collapsed axis as a length-1
dimension instead of dropping it — `(3, 1)` instead of `(3,)` — which is
exactly what you need here, because a `(3, 1)` array broadcasts cleanly
against the original `(3, 4)` matrix while a plain `(3,)` array doesn't.
"""
    ),
    code(
        """
m = np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]])
print(m.mean(axis=1))                   # shape (2,)  -- can't broadcast against m
print(m.mean(axis=1, keepdims=True))    # shape (2, 1) -- broadcasts against m
print(m.mean(axis=1, keepdims=True).shape)
"""
    ),
]

lesson_cells += exercise_cells(
    "2.2",
    "Per-row normalization",
    """
Write `subtract_row_means(matrix)` that takes a 2-D array and returns a new
array where the mean of each **row** has been subtracted from that row —
using broadcasting, not a loop over rows.
""",
    """
def subtract_row_means(matrix):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
m = np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]])
result = subtract_row_means(m)
print("subtract_row_means(m) ->")
print(result)

_passed = np.allclose(result.mean(axis=1), [0.0, 0.0]) and np.allclose(result[0], [-1.0, 0.0, 1.0])

if not _passed:
    print()
    print("Expected: each row's mean is 0, with row 0 == [-1. 0. 1.]")
""",
    "`matrix.mean(axis=1)` gives one mean per row as a 1-D array of shape "
    "`(n_rows,)` — you need it as `(n_rows, 1)` to broadcast correctly against "
    "`matrix`. Use `[:, np.newaxis]` (or `keepdims=True` in `.mean`).",
    """
def subtract_row_means(matrix):
    row_means = matrix.mean(axis=1, keepdims=True)
    return matrix - row_means
""",
)

# ---------------------------------------------------------------------------
# Lesson 3
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 3 — Vectorization vs. Explicit Loops

"Vectorizing" means replacing an element-by-element Python loop with a
single array-level operation that NumPy executes in compiled code. The
result is not just shorter code — it's dramatically faster for large
arrays, because Python's per-element overhead disappears entirely.
"""
    ),
    code(
        """
def clip_and_square_loop(values, lo, hi):
    out = []
    for v in values:
        v = max(lo, min(hi, v))   # clip
        out.append(v * v)         # square
    return out


def clip_and_square_vectorized(values, lo, hi):
    clipped = np.clip(values, lo, hi)
    return clipped ** 2


data = list(range(-5, 6))
print(clip_and_square_loop(data, -2, 2))
print(clip_and_square_vectorized(np.array(data), -2, 2))
"""
    ),
    code(
        """
big = list(range(1_000_000))
big_arr = np.array(big)

start = time.perf_counter()
clip_and_square_loop(big, -500_000, 500_000)
print(f"loop:       {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
clip_and_square_vectorized(big_arr, -500_000, 500_000)
print(f"vectorized: {time.perf_counter() - start:.4f}s")
"""
    ),
]

lesson_cells += exercise_cells(
    "3.1",
    "De-loop a threshold function",
    """
Here is a loop-based function:

```python
def flag_outliers_loop(values, threshold):
    flags = []
    for v in values:
        flags.append(abs(v) > threshold)
    return flags
```

Write `flag_outliers_vectorized(values, threshold)` that takes a NumPy array
and a scalar threshold, and returns a **boolean NumPy array** with the same
result — no loop, no comprehension.
""",
    """
def flag_outliers_vectorized(values, threshold):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = flag_outliers_vectorized(np.array([1, -10, 3, 8]), 5)
print("flag_outliers_vectorized(np.array([1, -10, 3, 8]), 5) ->")
print(result)

expected = np.array([False, True, False, True])
_passed = result.dtype == np.bool_ and np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`np.abs(values) > threshold` is already a full boolean array — that's the "
    "whole function.",
    """
def flag_outliers_vectorized(values, threshold):
    return np.abs(values) > threshold
""",
)

lesson_cells += [
    md(
        """
One more vectorization-friendly function worth knowing: `np.cumsum(arr)`
returns the running (cumulative) sum — replacing exactly the kind of loop
that keeps adding to a running total as it walks through a sequence.
"""
    ),
    code(
        """
print(np.cumsum(np.array([1, 2, 3, 4])))   # [1, 3, 6, 10]
"""
    ),
]

lesson_cells += exercise_cells(
    "3.2",
    "Vectorized running total check",
    """
Write `matches_cumulative_sum(values, running_totals)` that checks, without
any explicit Python loop, whether `running_totals` equals the cumulative
sum of `values` (i.e. `running_totals[i] == sum(values[:i+1])` for every
`i`). Return a single `bool`.
""",
    """
def matches_cumulative_sum(values, running_totals):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
v = np.array([1, 2, 3, 4])
good = np.array([1, 3, 6, 10])
bad = np.array([1, 3, 7, 10])

result_good = matches_cumulative_sum(v, good)
print("matches_cumulative_sum(v, good) ->")
print(result_good)

result_bad = matches_cumulative_sum(v, bad)
print("matches_cumulative_sum(v, bad) ->")
print(result_bad)

_passed = result_good is True and result_bad is False

if not _passed:
    print()
    print("Expected: True for `good`, False for `bad`")
""",
    "`np.cumsum(values)` computes the running total in one call; compare it to "
    "`running_totals` with `np.array_equal`.",
    """
def matches_cumulative_sum(values, running_totals):
    return bool(np.array_equal(np.cumsum(values), running_totals))
""",
)

# ---------------------------------------------------------------------------
# Lesson 4
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 4 — Comparison & Logical Ufuncs

Comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`) are ufuncs too — they
return a boolean array instead of raising/short-circuiting like Python's
`==` on lists does. Combine boolean arrays with `&`, `|`, `~` (never the
Python keywords `and`/`or`/`not`, which don't work elementwise).

For floating-point data, never compare with `==` directly — use
`np.isclose(a, b)` (or `np.allclose` for whole arrays), which accounts for
rounding error. Both also accept an `atol=` (absolute tolerance) keyword,
useful when the default relative tolerance alone isn't strict enough —
e.g. when comparing values near zero. `np.where(condition, if_true,
if_false)` is the vectorized equivalent of a Python ternary/if-else,
applied elementwise.
"""
    ),
    code(
        """
a = np.array([1, 2, 3, 4, 5])

mask = (a > 1) & (a < 5)           # combine with & , not `and`
print(mask)
print(a[mask])

print(np.where(a % 2 == 0, "even", "odd"))

x = np.array([0.1 + 0.2, 0.3])
print(x[0] == x[1])        # False due to floating point!
print(np.isclose(x[0], x[1]))
"""
    ),
]

lesson_cells += exercise_cells(
    "4.1",
    "Classify values",
    """
Write `classify(arr)` that returns an array of strings the same length as
`arr`, where each element is `"negative"`, `"zero"`, or `"positive"`
depending on the sign of the corresponding input value. Use `np.where`
(you'll need it twice, nested) — no loop.
""",
    """
def classify(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = classify(np.array([-5, 0, 7]))
print("classify(np.array([-5, 0, 7])) ->")
print(list(result))

expected = ["negative", "zero", "positive"]
_passed = list(result) == expected

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "First handle the positive/non-positive split with one `np.where`, then "
    "wrap that call in a second `np.where` that handles the zero case.",
    """
def classify(arr):
    return np.where(arr > 0, "positive", np.where(arr == 0, "zero", "negative"))
""",
)

lesson_cells += exercise_cells(
    "4.2",
    "Close enough",
    """
Write `count_close_pairs(a, b, tol)` that returns how many positions `i`
satisfy `np.isclose(a[i], b[i], atol=tol)`, as a plain Python `int`.
""",
    """
def count_close_pairs(a, b, tol):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
a = np.array([1.0, 2.0, 3.0001])
b = np.array([1.0001, 2.5, 3.0])
result = count_close_pairs(a, b, tol=0.01)
print("count_close_pairs(a, b, tol=0.01) ->")
print(result)

_passed = result == 2

if not _passed:
    print()
    print("Expected: 2")
""",
    "`np.isclose(a, b, atol=tol)` gives a boolean array; `.sum()` on a boolean "
    "array counts the `True`s.",
    """
def count_close_pairs(a, b, tol):
    return int(np.isclose(a, b, atol=tol).sum())
""",
)

# ---------------------------------------------------------------------------
# Lesson 5
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 5 — Outer Operations & Pairwise Computation via Broadcasting

`np.outer(a, b)` computes every product `a[i] * b[j]` and arranges them into
a matrix of shape `(len(a), len(b))`. More generally, you can build *any*
pairwise table — differences, distances, comparisons — by reshaping one
array to a column `(n, 1)` and the other to a row `(1, m)`, then letting
broadcasting fill in the full `(n, m)` grid. This avoids a nested Python
loop entirely.
"""
    ),
    code(
        """
a = np.array([1, 2, 3])
b = np.array([10, 20])

print(np.outer(a, b))               # every a[i] * b[j]

# Pairwise absolute differences, without np.outer:
diffs = np.abs(a[:, np.newaxis] - b[np.newaxis, :])
print(diffs)
print(diffs.shape)                   # (3, 2): one row per element of a
"""
    ),
]

lesson_cells += exercise_cells(
    "5.1",
    "Pairwise squared distances",
    """
Write `pairwise_sq_dist(a, b)` that takes two 1-D arrays and returns a 2-D
array of shape `(len(a), len(b))` where entry `[i, j]` is
`(a[i] - b[j]) ** 2`. No nested loop — use broadcasting with `np.newaxis`.
""",
    """
def pairwise_sq_dist(a, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = pairwise_sq_dist(np.array([0, 1]), np.array([0, 2, 3]))
print("pairwise_sq_dist(np.array([0, 1]), np.array([0, 2, 3])) ->")
print(result)

expected = np.array([[0, 4, 9], [1, 1, 4]])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`a[:, np.newaxis]` has shape `(len(a), 1)`; `b[np.newaxis, :]` has shape "
    "`(1, len(b))`. Subtract them, then square.",
    """
def pairwise_sq_dist(a, b):
    return (a[:, np.newaxis] - b[np.newaxis, :]) ** 2
""",
)

lesson_cells += exercise_cells(
    "5.2",
    "Multiplication table",
    """
Write `multiplication_table(n)` that returns the `n x n` multiplication
table (entry `[i, j]` equals `(i+1) * (j+1)`) using `np.outer` on
`np.arange(1, n+1)` — not a loop.
""",
    """
def multiplication_table(n):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = multiplication_table(3)
print("multiplication_table(3) ->")
print(result)

expected = np.array([[1, 2, 3], [2, 4, 6], [3, 6, 9]])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`np.arange(1, n + 1)` gives `[1, 2, ..., n]`; pass it to `np.outer` twice "
    "(as both arguments).",
    """
def multiplication_table(n):
    r = np.arange(1, n + 1)
    return np.outer(r, r)
""",
)

# ---------------------------------------------------------------------------
# Lesson 6
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 6 — Case Study: Vectorizing a Real Loop

Let's take a realistic loop-based function and vectorize it end to end.

```python
def score_loop(values):
    \"\"\"Clip each value into [0, 100], then apply a bonus:
    +10 if the clipped value is above 80, otherwise no bonus.\"\"\"
    out = []
    for v in values:
        v = max(0, min(100, v))
        if v > 80:
            v += 10
        out.append(v)
    return out
```

A tempting shortcut is `np.vectorize(score_loop_single_element)`: it *looks*
vectorized because it accepts arrays, but internally it still calls your
Python function once per element in a Python loop — you get NumPy's
*syntax* without NumPy's *speed*. Prefer composing real ufuncs
(`np.clip`, `np.where`, comparisons) instead.
"""
    ),
    code(
        """
def score_loop(values):
    out = []
    for v in values:
        v = max(0, min(100, v))
        if v > 80:
            v += 10
        out.append(v)
    return out


def score_vectorized(values):
    clipped = np.clip(values, 0, 100)
    return np.where(clipped > 80, clipped + 10, clipped)


sample = [-5, 50, 85, 120]
print(score_loop(sample))
print(score_vectorized(np.array(sample)))
"""
    ),
]

lesson_cells += exercise_cells(
    "6.1",
    "Vectorize the scoring function",
    """
Write `score_vectorized_checked(values)` that reproduces `score_loop`'s
behavior exactly (clip to `[0, 100]`, then `+10` bonus if the clipped value
is `> 80`) using only `np.clip` and `np.where` — no loop, no
`np.vectorize`. Return a NumPy array.
""",
    """
def score_vectorized_checked(values):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
values = np.array([-5, 50, 85, 120])
result = score_vectorized_checked(values)
print("score_vectorized_checked(np.array([-5, 50, 85, 120])) ->")
print(result)

expected = np.array(score_loop(list(values)))
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Clip first with `np.clip(values, 0, 100)`, then use `np.where` on the "
    "clipped result to add the bonus conditionally.",
    """
def score_vectorized_checked(values):
    clipped = np.clip(values, 0, 100)
    return np.where(clipped > 80, clipped + 10, clipped)
""",
)

lesson_cells += exercise_cells(
    "6.2",
    "Spot the fake vectorization",
    """
Write `is_real_ufunc_pipeline(func)` that takes a function and returns
`False` if `func` is an instance of `np.vectorize` (i.e. built by wrapping a
scalar Python function), and `True` otherwise. This is a quick sanity check
you can literally run on your own code to catch accidental fake
vectorization.
""",
    """
def is_real_ufunc_pipeline(func):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
fake = np.vectorize(lambda v: v * 2)
result_fake = is_real_ufunc_pipeline(fake)
print("is_real_ufunc_pipeline(np.vectorize(...)) ->")
print(result_fake)

result_real = is_real_ufunc_pipeline(score_vectorized)
print("is_real_ufunc_pipeline(score_vectorized) ->")
print(result_real)

_passed = result_fake is False and result_real is True

if not _passed:
    print()
    print("Expected: False for the np.vectorize-wrapped function, True for score_vectorized")
""",
    "Use `isinstance(func, np.vectorize)`.",
    """
def is_real_ufunc_pipeline(func):
    return not isinstance(func, np.vectorize)
""",
)

# ---------------------------------------------------------------------------
# Wrap-up
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## 🎯 Key Takeaways

- Operators (`+`, `*`, `>`, ...) are shorthand for **ufuncs**
  (`np.add`, `np.multiply`, `np.greater`, ...) running in compiled code.
- Broadcasting compares shapes right-to-left: equal dims match, size-1 dims
  stretch, anything else raises `ValueError`.
- A vectorized rewrite of a loop isn't just shorter — it's dramatically
  faster, because per-element Python overhead disappears.
- Build boolean masks with `&`/`|`/`~` and `np.where`; never trust `==` on
  floats — use `np.isclose`/`np.allclose`.
- `np.outer` and `[:, np.newaxis]` / `[np.newaxis, :]` broadcasting build
  full pairwise tables without nested loops.
- `np.vectorize` is a convenience for mapping a scalar function over an
  array — it does **not** give you a real performance improvement; prefer
  composing real ufuncs.

Next up: **Module 4 — Aggregations, Statistics & Sorting**, where you'll
learn to summarize and reorder array data along any axis.
"""
    )
]

nb = build_notebook(TITLE, FILENAME, intro_cells, lesson_cells)
save_notebook(nb, FILENAME)
print(f"Wrote {FILENAME} with {len(nb['cells'])} cells.")
