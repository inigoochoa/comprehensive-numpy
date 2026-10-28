"""Builds module_1_fundamentals.ipynb — NumPy Fundamentals & Array Creation.

Run with: python build_module_1.py
"""
from nb_utils import md, code, exercise_cells, build_notebook, save_notebook

FILENAME = "module_1_fundamentals.ipynb"
TITLE = "Module 1 — NumPy Fundamentals & Array Creation"

intro_cells = [
    md(
        """
## Welcome

This module lays the foundation for the whole course: what an `ndarray`
actually is, how to create one in every common way, how to inspect it, and
how to reshape and combine arrays. Every later module builds on these
mechanics, so take your time with the exercises here.

**Learning goals**
- Explain why NumPy arrays outperform plain Python lists for numeric work
- Create arrays with `np.array`, `np.zeros`/`ones`/`full`/`eye`, `np.arange`, `np.linspace`
- Read an array's `shape`, `ndim`, `size`, `dtype`, `itemsize`
- Cast between dtypes with `.astype`
- Reshape, flatten, and transpose arrays
- Combine and split arrays along an axis

**Setup** — run this first.
"""
    ),
    code(
        """
import numpy as np
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
## Lesson 1 — Why NumPy? `ndarray` vs. Python `list`

A Python `list` is a flexible, general-purpose container: each element is a
separate Python object, and the list itself is just an array of pointers to
those objects. That flexibility has a cost — looping over a list in pure
Python re-enters the interpreter for every single element.

A NumPy `ndarray` is a fixed-type, contiguous block of memory. Because every
element has the same dtype and a known size, NumPy can hand the whole loop
off to compiled C code — this is called **vectorization**, and it's the
single most important idea in this course.
"""
    ),
    code(
        """
# Same logical operation, two very different implementations.
a = [1, 2, 3, 4, 5]
b = [10, 20, 30, 40, 50]

# Python list: no "+" between lists means elementwise addition — you need a loop.
elementwise_sum_list = [x + y for x, y in zip(a, b)]
print("list comprehension:", elementwise_sum_list)

# NumPy array: "+" IS elementwise addition, done in compiled code.
arr_a = np.array(a)
arr_b = np.array(b)
print("vectorized:        ", arr_a + arr_b)
"""
    ),
    code(
        """
import time

big_a = list(range(2_000_000))
big_b = list(range(2_000_000))

start = time.perf_counter()
_ = [x + y for x, y in zip(big_a, big_b)]
print(f"Python loop:   {time.perf_counter() - start:.4f}s")

np_a = np.array(big_a)
np_b = np.array(big_b)

start = time.perf_counter()
_ = np_a + np_b
print(f"NumPy vectorized: {time.perf_counter() - start:.4f}s")
"""
    ),
    md(
        """
One more comparison you'll use constantly — including in this course's own
"check" cells, starting with the very next exercise: `==` between two arrays
compares **elementwise** and gives you back an array of booleans, not a
single answer. When you want one `True`/`False` for "are these two arrays
the same?", use `np.array_equal(a, b)` instead — it checks that both arrays
have the same shape and that every element matches.
"""
    ),
    code(
        """
a = np.array([1, 2, 3])
b = np.array([1, 2, 3])

print(a == b)                  # elementwise: array([ True,  True,  True])
print(np.array_equal(a, b))    # one answer: True
"""
    ),
]

lesson_cells += exercise_cells(
    "1.1",
    "No loops allowed",
    """
Write `elementwise_product(a, b)` that takes two same-length Python `list`s
of numbers and returns a NumPy array containing their elementwise product.
You may **not** use a `for` loop, `while` loop, or list/generator
comprehension anywhere in your implementation — convert to arrays and let
NumPy do the work.
""",
    """
def elementwise_product(a, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = elementwise_product([1, 2, 3], [4, 5, 6])
print("elementwise_product([1, 2, 3], [4, 5, 6]) ->")
print(result)

expected = np.array([4, 10, 18])
_passed = (
    isinstance(result, np.ndarray)
    and np.array_equal(result, expected)
    and np.array_equal(elementwise_product([0, -1], [5, 5]), np.array([0, -5]))
)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Convert both lists to arrays with `np.array(...)`, then use the `*` operator.",
    """
def elementwise_product(a, b):
    return np.array(a) * np.array(b)
""",
)

# ---------------------------------------------------------------------------
# Lesson 2
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 2 — Creating Arrays

There are three common families of array-creation functions:

| Family | Functions | Use case |
|---|---|---|
| From existing data | `np.array`, `np.asarray` | You already have a list/tuple of values |
| Filled with a constant | `np.zeros`, `np.ones`, `np.full`, `np.eye` | You need a placeholder of a given shape |
| Evenly spaced ranges | `np.arange`, `np.linspace` | You need a sequence of numbers |

`np.arange(start, stop, step)` works like Python's `range` but returns an
array and accepts floats. `np.linspace(start, stop, num)` instead fixes the
**count** of points (inclusive of both ends by default), which is usually
what you want for plotting.
"""
    ),
    code(
        """
print(np.zeros((2, 3)))
print()
print(np.full((2, 2), fill_value=7))
print()
print(np.eye(3))
print()
print(np.arange(0, 10, 2))       # stop is exclusive
print(np.linspace(0, 1, 5))      # stop is inclusive
"""
    ),
    md(
        """
A quick preview before the next exercise — Module 2 covers indexing and
slicing in full depth, but you'll need a taste of it now. Slicing an array
works just like slicing a Python list — `arr[start:stop:step]` — except it
extends naturally to multiple axes by separating them with a comma. So
`arr[::2, ::2]` means "every other row, every other column": `::2` alone
means "the whole axis, stepping by 2."
"""
    ),
    code(
        """
grid = np.arange(16).reshape(4, 4)
print(grid)
print()
print(grid[::2, ::2])   # every other row, every other column
"""
    ),
]

lesson_cells += exercise_cells(
    "2.1",
    "Build a checkerboard",
    """
Write `checkerboard(n)` that returns an `(n, n)` array of `int` dtype
containing a checkerboard pattern of `0`s and `1`s, where position `(0, 0)`
is `1`. For `n=4` the result should be:

```
[[1 0 1 0]
 [0 1 0 1]
 [1 0 1 0]
 [0 1 0 1]]
```
""",
    """
def checkerboard(n):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = checkerboard(4)
print("checkerboard(4) ->")
print(result)

expected = np.array([[1, 0, 1, 0],
                      [0, 1, 0, 1],
                      [1, 0, 1, 0],
                      [0, 1, 0, 1]])
_passed = np.array_equal(result, expected) and checkerboard(2).tolist() == [[1, 0], [0, 1]]

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Build an `(n, n)` array of zeros with `np.zeros`, then use slicing with a "
    "step of 2 on rows and columns — `board[0::2, 0::2]` and `board[1::2, 1::2]` "
    "— to set the right cells to 1.",
    """
def checkerboard(n):
    board = np.zeros((n, n), dtype=int)
    board[0::2, 0::2] = 1
    board[1::2, 1::2] = 1
    return board
""",
)

# ---------------------------------------------------------------------------
# Lesson 3
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 3 — Array Attributes & Dtypes

Every array carries metadata describing its layout:

- `.shape` — a tuple with the size along each axis
- `.ndim` — number of axes (`len(shape)`)
- `.size` — total number of elements
- `.dtype` — the element type (`int64`, `float64`, `bool`, ...)
- `.itemsize` — bytes per element

NumPy infers a dtype from your data, but mixing an `int` with a `float`
upcasts the whole array to `float64` — there is no per-element typing.
"""
    ),
    code(
        """
arr = np.array([[1, 2, 3], [4, 5, 6]])
print("shape:   ", arr.shape)
print("ndim:    ", arr.ndim)
print("size:    ", arr.size)
print("dtype:   ", arr.dtype)
print("itemsize:", arr.itemsize, "bytes")

mixed = np.array([1, 2, 3.5])   # one float -> whole array becomes float64
print(mixed.dtype)
"""
    ),
]

lesson_cells += exercise_cells(
    "3.1",
    "Describe an array",
    """
Write `describe(arr)` that returns a dict with keys `"shape"`, `"ndim"`,
`"size"`, and `"dtype_name"` (the dtype as a string, e.g. `"int64"`) for the
given array.
""",
    """
def describe(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = describe(np.zeros((3, 4)))
print("describe(np.zeros((3, 4))) ->")
print(result)

expected = {"shape": (3, 4), "ndim": 2, "size": 12, "dtype_name": "float64"}
_passed = (
    result.get("shape") == expected["shape"]
    and result.get("ndim") == expected["ndim"]
    and result.get("size") == expected["size"]
    and "float" in str(result.get("dtype_name"))
)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`str(arr.dtype)` gives you the dtype name as a string.",
    """
def describe(arr):
    return {
        "shape": arr.shape,
        "ndim": arr.ndim,
        "size": arr.size,
        "dtype_name": str(arr.dtype),
    }
""",
)

lesson_cells += [
    md(
        """
One more pair of tools before the next exercise. `np.floor(x)` rounds each
element down to the nearest integer (elementwise) — `np.ceil` and
`np.round` work the same way for rounding up / to the nearest. And
`np.all(bool_array)` collapses a whole boolean array down to a single
`True`/`False`: `True` only if **every** element is `True`. `np.any` is the
mirror image — `True` if **at least one** element is `True`.
"""
    ),
    code(
        """
print(np.floor(np.array([1.2, 2.9, -0.5])))     # [ 1.  2. -1.]
print(np.all(np.array([True, True, False])))     # False — not all True
print(np.any(np.array([True, True, False])))     # True — at least one True
"""
    ),
]

lesson_cells += exercise_cells(
    "3.2",
    "Safe integer casting",
    """
Write `to_int_safe(arr)` that casts a float array to `int64` using
`.astype`, but raises a `ValueError` (with any message) if doing so would
silently truncate a non-integer value (e.g. casting `2.5` to `2`).
""",
    """
def to_int_safe(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = to_int_safe(np.array([1.0, 2.0, 3.0]))
print("to_int_safe(np.array([1.0, 2.0, 3.0])) ->")
print(result, "dtype:", result.dtype)

ok_basic = result.dtype == np.int64 and np.array_equal(result, [1, 2, 3])

try:
    to_int_safe(np.array([1.0, 2.5]))
    raised_value_error = False
except ValueError:
    raised_value_error = True
except Exception:
    raised_value_error = False

print()
print("to_int_safe(np.array([1.0, 2.5])) ->",
      "raised ValueError" if raised_value_error else "did NOT raise ValueError")

_passed = ok_basic and raised_value_error

if not _passed:
    print()
    print("Expected: [1 2 3] with dtype int64, and a ValueError for [1.0, 2.5]")
""",
    "Compare `arr` to `np.floor(arr)` elementwise with `==`, then wrap that "
    "in `np.all(...)` to get a single True/False before deciding whether to cast.",
    """
def to_int_safe(arr):
    if not np.all(arr == np.floor(arr)):
        raise ValueError("array contains non-integer values")
    return arr.astype(np.int64)
""",
)

# ---------------------------------------------------------------------------
# Lesson 4
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 4 — Reshaping & Dimensions

`.reshape(new_shape)` returns a view with the same data laid out under a
different shape (total element count must match — use `-1` to let NumPy
infer one dimension). `.ravel()` flattens to 1-D (a view when possible),
`.flatten()` always returns a copy. `.T` (or `np.transpose`) swaps axes, and
`np.newaxis` inserts a new length-1 axis, which is the standard way to turn
a 1-D array into a row or column vector.
"""
    ),
    code(
        """
arr = np.arange(12)
print(arr.reshape(3, 4))
print(arr.reshape(3, -1).shape)   # -1 means "figure this dimension out"

col = arr[:4][:, np.newaxis]      # turn a 1-D array into a column vector
print(col.shape)
print(arr.reshape(3, 4).T)        # transpose
"""
    ),
]

lesson_cells += exercise_cells(
    "4.1",
    "Flatten and pair up",
    """
Write `to_pairs(arr)` that takes an array of any shape with an even number
of elements and returns it reshaped into shape `(-1, 2)` — i.e. a sequence
of `[a, b]` pairs, read in row-major (C) order.
""",
    """
def to_pairs(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = to_pairs(np.array([[1, 2, 3], [4, 5, 6]]))
print("to_pairs(np.array([[1, 2, 3], [4, 5, 6]])) ->")
print(result)

expected = np.array([[1, 2], [3, 4], [5, 6]])
_passed = np.array_equal(result, expected) and to_pairs(np.arange(4)).shape == (2, 2)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`.ravel()` first to get a flat 1-D sequence, then `.reshape(-1, 2)`.",
    """
def to_pairs(arr):
    return arr.ravel().reshape(-1, 2)
""",
)

# ---------------------------------------------------------------------------
# Lesson 5
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 5 — Combining & Splitting Arrays

- `np.concatenate([a, b], axis=...)` joins arrays along an existing axis
  (shapes must match on every other axis).
- `np.vstack` / `np.hstack` are convenience wrappers for concatenating along
  axis 0 / axis 1.
- `np.stack([a, b], axis=...)` joins arrays along a **new** axis instead —
  use this when you want to go from several `(n,)` arrays to one `(2, n)`
  or `(n, 2)` array.
- `np.split(arr, n, axis=...)` divides an array into `n` equal pieces along
  an axis.
"""
    ),
    code(
        """
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(np.concatenate([a, b]))          # (6,)
print(np.stack([a, b]))                # (2, 3) — new axis 0
print(np.stack([a, b], axis=1))        # (3, 2) — new axis 1

m = np.arange(8).reshape(2, 4)
left, right = np.split(m, 2, axis=1)
print(left)
print(right)
"""
    ),
]

lesson_cells += exercise_cells(
    "5.1",
    "Interleave two signals",
    """
Write `interleave(a, b)` that takes two 1-D arrays of the same length `n`
and returns a single 1-D array of length `2n` where values alternate:
`[a[0], b[0], a[1], b[1], ...]`. Do this using `np.stack` and `reshape` —
no Python loop.
""",
    """
def interleave(a, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = interleave(np.array([1, 3, 5]), np.array([2, 4, 6]))
print("interleave(np.array([1, 3, 5]), np.array([2, 4, 6])) ->")
print(result)

expected = np.array([1, 2, 3, 4, 5, 6])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`np.stack([a, b], axis=1)` gives you an `(n, 2)` array of pairs — "
    "flatten that.",
    """
def interleave(a, b):
    return np.stack([a, b], axis=1).ravel()
""",
)

# ---------------------------------------------------------------------------
# Wrap-up
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## 🎯 Key Takeaways

- NumPy arrays beat Python lists for numeric work because they're
  contiguous, fixed-type, and support **vectorized** operations in compiled
  code.
- Pick the right creation function for the job: `np.array` from existing
  data, `np.zeros`/`ones`/`full`/`eye` for placeholders, `np.arange`/
  `np.linspace` for ranges.
- `.shape`, `.ndim`, `.size`, `.dtype` tell you everything about an array's
  layout; `.astype` converts between dtypes (and can silently lose data).
- `.reshape`, `.ravel`, `.flatten`, `.T`, and `np.newaxis` rearrange data
  without changing its values.
- `np.concatenate`/`vstack`/`hstack` join along an existing axis;
  `np.stack` creates a new one.

Next up: **Module 2 — Indexing, Slicing & Views**, where you'll learn how
to select exactly the data you want — and which selections give you a view
vs. a copy.
"""
    )
]

nb = build_notebook(TITLE, FILENAME, intro_cells, lesson_cells)
save_notebook(nb, FILENAME)
print(f"Wrote {FILENAME} with {len(nb['cells'])} cells.")
