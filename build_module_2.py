"""Builds module_2_indexing_views.ipynb — Indexing, Slicing & Views.

Run with: python build_module_2.py
"""
from nb_utils import md, code, exercise_cells, build_notebook, save_notebook

FILENAME = "module_2_indexing_views.ipynb"
TITLE = "Module 2 — Indexing, Slicing & Views"

intro_cells = [
    md(
        """
## Welcome

Indexing is how you *select* data out of an array, and it's where NumPy has
the most surprises for people coming from Python lists — especially around
whether what you get back is a **view** (shares memory with the original)
or a **copy** (independent). Getting this wrong is one of the most common
sources of silent bugs in real NumPy code, so this module slows down and
builds careful intuition before moving on.

**Learning goals**
- Index and slice 1-D and multi-D arrays, including negative indices and steps
- Build and combine boolean masks to filter data
- Use fancy (integer-array) indexing
- Know exactly when an operation returns a view vs. a copy — and why it matters
- Use `np.newaxis` and `...` (Ellipsis) to index higher-dimensional arrays

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
# Lesson 1 — Basic indexing & slicing
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 1 — Basic Indexing & Slicing

Array indexing extends Python's `list[start:stop:step]` syntax to any
number of dimensions, with one index/slice per axis, separated by commas:
`arr[row_slice, col_slice]`. Negative indices count from the end, and a
negative step reverses direction.

| Expression | Meaning |
|---|---|
| `arr[2]` | element/row at index 2 |
| `arr[-1]` | last element/row |
| `arr[1:4]` | indices 1, 2, 3 |
| `arr[::2]` | every other element |
| `arr[::-1]` | reversed |
| `arr[1:3, 0:2]` | rows 1-2, columns 0-1 |
"""
    ),
    code(
        """
arr = np.arange(10)
print(arr[2], arr[-1], arr[1:4], arr[::2], arr[::-1])

grid = np.arange(16).reshape(4, 4)
print(grid)
print(grid[1:3, 0:2])   # rows 1-2, cols 0-1
print(grid[:, 2])       # every row, column 2
print(grid[-1, :])      # last row
"""
    ),
]

lesson_cells += exercise_cells(
    "1.1",
    "Border of a grid",
    """
Write `border(grid)` that takes a 2-D array and returns its last row
reversed — i.e. `grid[-1][::-1]`.
""",
    """
def border(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
g = np.arange(9).reshape(3, 3)
result = border(g)
print("border(np.arange(9).reshape(3, 3)) ->")
print(result)

expected = np.array([8, 7, 6])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Index the last row with `grid[-1]`, then reverse it with `[::-1]`.",
    """
def border(grid):
    return grid[-1][::-1]
""",
)

lesson_cells += exercise_cells(
    "1.2",
    "Every other row and column",
    """
Write `downsample(grid)` that returns every other row AND every other
column of a 2-D array, starting from index 0 (i.e. `grid[0::2, 0::2]`).
""",
    """
def downsample(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
g = np.arange(16).reshape(4, 4)
result = downsample(g)
print("downsample(np.arange(16).reshape(4, 4)) ->")
print(result)

expected = np.array([[0, 2], [8, 10]])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Apply a step-2 slice to both axes at once: `grid[0::2, 0::2]`.",
    """
def downsample(grid):
    return grid[0::2, 0::2]
""",
)

# ---------------------------------------------------------------------------
# Lesson 2 — Boolean indexing
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 2 — Boolean Indexing

Comparing an array to a value produces a **boolean mask** — an array of
`True`/`False` the same shape as the original. Indexing with that mask
returns only the elements where it's `True`. To combine conditions, you
must use the bitwise operators `&`, `|`, `~` (NOT Python's `and`/`or`/`not`
— those don't work elementwise and will raise an error on arrays with more
than one element). `np.where(condition, a, b)` is the vectorized
if/else: pick from `a` where `condition` is True, else from `b`.

Two more things come up constantly once you're working with masks. First,
`True`/`False` behave as `1`/`0` in arithmetic, so `mask.sum()` counts how
many elements are `True` — a quick way to count matches without reaching
for the full aggregation toolkit (Module 4 covers `.sum()`, `.mean()`, and
friends in depth). Second, indexing itself never mutates anything, but if
you're about to change values and want to leave the original untouched,
call `.copy()` first to get an independent array — Lesson 4 covers views
vs. copies in full.
"""
    ),
    code(
        """
arr = np.array([3, -1, 7, -5, 2, 0, 9])
mask = arr > 0
print(mask)
print(arr[mask])                      # positive values only
print(arr[(arr > 0) & (arr < 8)])     # combine with & , not "and"

clipped = np.where(arr < 0, 0, arr)   # replace negatives with 0
print(clipped)

arr[arr < 0] = 0                      # assign through a mask, in place
print(arr)
"""
    ),
]

lesson_cells += exercise_cells(
    "2.1",
    "Clip to a range",
    """
Write `clip_range(arr, low, high)` that returns a **new** array where every
value below `low` is replaced by `low`, and every value above `high` is
replaced by `high` (values already in range are unchanged). Do not use
`np.clip` — build it from boolean masks and `np.where` (or boolean
assignment on a copy) to practice the mechanics.
""",
    """
def clip_range(arr, low, high):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = clip_range(np.array([-5, 0, 3, 10, 15]), 0, 10)
print("clip_range(np.array([-5, 0, 3, 10, 15]), 0, 10) ->")
print(result)

expected = np.array([0, 0, 3, 10, 10])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Make a copy first (`out = arr.copy()`), then assign through two masks: "
    "`out[out < low] = low` and `out[out > high] = high`.",
    """
def clip_range(arr, low, high):
    out = arr.copy()
    out[out < low] = low
    out[out > high] = high
    return out
""",
)

lesson_cells += exercise_cells(
    "2.2",
    "Count values in a band",
    """
Write `count_in_band(arr, low, high)` that returns how many elements of
`arr` satisfy `low <= x <= high`, as a plain Python `int`.
""",
    """
def count_in_band(arr, low, high):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = count_in_band(np.array([1, 5, 8, 12, 20]), 5, 12)
print("count_in_band(np.array([1, 5, 8, 12, 20]), 5, 12) ->")
print(result)

expected = 3
_passed = result == expected and isinstance(result, int)

if not _passed:
    print()
    print("Expected:", expected, "(as a plain Python int)")
""",
    "Combine two comparisons with `&`, then `.sum()` the boolean mask — "
    "`True` counts as 1. Wrap the result in `int(...)`.",
    """
def count_in_band(arr, low, high):
    mask = (arr >= low) & (arr <= high)
    return int(mask.sum())
""",
)

# ---------------------------------------------------------------------------
# Lesson 3 — Fancy indexing
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 3 — Fancy Indexing

"Fancy indexing" means indexing with an array (or list) of integers instead
of a single index or a slice. It lets you pick out an arbitrary, possibly
repeated, possibly reordered set of elements/rows/columns in one shot. You
can combine a fancy index on one axis with a slice on another. Unlike basic
slicing, **fancy indexing always returns a copy**, never a view.
"""
    ),
    code(
        """
arr = np.array([10, 20, 30, 40, 50])
print(arr[[0, 2, 4]])        # pick specific elements
print(arr[[3, 3, 1]])        # repeats allowed, any order

grid = np.arange(12).reshape(4, 3)
print(grid[[0, 2]])          # rows 0 and 2
print(grid[[0, 2], :2])      # rows 0 and 2, first two columns
print(grid[[0, 1, 2], [0, 1, 2]])  # (0,0), (1,1), (2,2) -- paired coordinates!
"""
    ),
]

lesson_cells += exercise_cells(
    "3.1",
    "Reorder rows",
    """
Write `reorder_rows(grid, order)` that takes a 2-D array and a list of row
indices `order`, and returns a new array with the rows rearranged into that
order (rows may repeat or be dropped).
""",
    """
def reorder_rows(grid, order):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
g = np.arange(9).reshape(3, 3)
result = reorder_rows(g, [2, 0, 0])
print("reorder_rows(np.arange(9).reshape(3, 3), [2, 0, 0]) ->")
print(result)

expected = np.array([[6, 7, 8], [0, 1, 2], [0, 1, 2]])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Fancy-index the row axis directly: `grid[order]`.",
    """
def reorder_rows(grid, order):
    return grid[order]
""",
)

lesson_cells += exercise_cells(
    "3.2",
    "Diagonal via coordinates",
    """
Write `pick_diagonal(grid)` that returns the main diagonal of a square 2-D
array using **paired fancy indexing** (`grid[rows, cols]`), not
`np.diagonal` or `np.diag`.
""",
    """
def pick_diagonal(grid):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
g = np.arange(9).reshape(3, 3)
result = pick_diagonal(g)
print("pick_diagonal(np.arange(9).reshape(3, 3)) ->")
print(result)

expected = np.array([0, 4, 8])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Build row and column index arrays with `np.arange(len(grid))` and use "
    "them both: `grid[idx, idx]`.",
    """
def pick_diagonal(grid):
    idx = np.arange(len(grid))
    return grid[idx, idx]
""",
)

# ---------------------------------------------------------------------------
# Lesson 4 — Views vs. copies
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 4 — Views vs. Copies

This is the single most important mental model in this module:

| Operation | View or copy? |
|---|---|
| Basic slicing (`arr[1:4]`, `grid[:, 0]`) | **View** |
| Boolean indexing (`arr[mask]`) | **Copy** |
| Fancy indexing (`arr[[0, 2]]`) | **Copy** |
| `.reshape()` (when possible) | **View** |
| `.ravel()` | View when possible, else copy |
| `.flatten()` | Always a **copy** |

A view shares the same underlying memory as the array it came from — `arr2
= arr[1:4]` doesn't copy any data, it just creates a new array object that
*looks at* part of `arr`'s buffer. **Mutating a view mutates the original.**
Check `arr2.base is arr` (or `arr2.base is not None`) to tell if something
is a view — though `.base` chains can get indirect (a view of a view), so
`np.shares_memory(a, b)` is the more robust way to ask "do these two arrays
point at the same underlying memory?" directly, without worrying about how
many `.base` hops apart they are. Call `.copy()` whenever you need a truly
independent array.
"""
    ),
    code(
        """
original = np.array([1, 2, 3, 4, 5])
view = original[1:4]
print("view.base is original:", view.base is original)

view[0] = 999                 # mutating the VIEW...
print("original:", original)  # ...mutates the ORIGINAL too!

safe_copy = original[1:4].copy()
safe_copy[0] = -1
print("original after mutating the copy:", original)   # unaffected
"""
    ),
]

lesson_cells += exercise_cells(
    "4.1",
    "A function that must not mutate its input",
    """
Write `double_first_n(arr, n)` that returns a **new** array equal to `arr`
but with its first `n` elements doubled. Calling this function must leave
the original `arr` completely unchanged — a common bug is slicing (which
gives a view) and then mutating in place.
""",
    """
def double_first_n(arr, n):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
original = np.array([1, 2, 3, 4, 5])
result = double_first_n(original, 3)
print("double_first_n(np.array([1, 2, 3, 4, 5]), 3) ->")
print(result)
print()
print("original array after the call ->", original)

expected = np.array([2, 4, 6, 4, 5])
original_unchanged = np.array_equal(original, np.array([1, 2, 3, 4, 5]))
_passed = np.array_equal(result, expected) and original_unchanged

if not _passed:
    print()
    print("Expected result:", expected, "- and the original should still read [1 2 3 4 5]")
""",
    "Start from `arr.copy()`, not from `arr` directly or a slice of it — "
    "then mutate the copy freely.",
    """
def double_first_n(arr, n):
    out = arr.copy()
    out[:n] *= 2
    return out
""",
)

lesson_cells += exercise_cells(
    "4.2",
    "Is it a view?",
    """
Write `is_view_of(sub, original)` that returns `True` if `sub` is a view
into `original`'s memory (i.e. shares its buffer), and `False` if `sub` is
an independent copy. Hint: this should work for both the array returned by
slicing AND the array itself (`original.base is None`, but it IS the data
— treat that case as "not a copy", i.e. return `True` only when `sub` is
genuinely backed by `original`'s memory).
""",
    """
def is_view_of(sub, original):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
original = np.arange(10)
view = original[2:5]
copy = original[2:5].copy()
fancy = original[[2, 3, 4]]

r_view = is_view_of(view, original)
r_copy = is_view_of(copy, original)
r_fancy = is_view_of(fancy, original)
print("is_view_of(original[2:5], original) ->", r_view)
print("is_view_of(original[2:5].copy(), original) ->", r_copy)
print("is_view_of(original[[2, 3, 4]], original) ->", r_fancy)

_passed = (r_view == True) and (r_copy == False) and (r_fancy == False)

if not _passed:
    print()
    print("Expected: True, False, False")
""",
    "`np.shares_memory(sub, original)` answers exactly this question and "
    "handles all the edge cases correctly — no need to reinvent it with `.base`.",
    """
def is_view_of(sub, original):
    return bool(np.shares_memory(sub, original))
""",
)

# ---------------------------------------------------------------------------
# Lesson 5 — np.newaxis and Ellipsis
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 5 — `np.newaxis` and `...` (Ellipsis)

`np.newaxis` (an alias for `None`) inserts a new length-1 axis at the
position you place it — the standard way to turn a 1-D array into an
explicit row or column vector, which matters a lot once you start
broadcasting (Module 3). `...` (Ellipsis) means "as many full slices `:` as
needed to cover the remaining axes" — handy for indexing deep into a
high-dimensional array without writing a `:` for every axis in between.
"""
    ),
    code(
        """
v = np.array([1, 2, 3])
print(v.shape)                       # (3,)
print(v[:, np.newaxis].shape)        # (3, 1) -- column vector
print(v[np.newaxis, :].shape)        # (1, 3) -- row vector

cube = np.arange(24).reshape(2, 3, 4)
print(cube[..., 0].shape)            # same as cube[:, :, 0] -> (2, 3)
print(cube[0, ...].shape)            # same as cube[0, :, :] -> (3, 4)

grid = np.zeros((3, 3))
grid[1, :] = [7, 8, 9]               # assign into a slice
print(grid)
"""
    ),
]

lesson_cells += exercise_cells(
    "5.1",
    "To column vector",
    """
Write `to_column(v)` that takes a 1-D array of shape `(n,)` and returns it
reshaped to a column vector of shape `(n, 1)` using `np.newaxis` (not
`.reshape`).
""",
    """
def to_column(v):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = to_column(np.array([1, 2, 3]))
print("to_column(np.array([1, 2, 3])) ->")
print(result)
print("shape:", result.shape)

_passed = result.shape == (3, 1) and np.array_equal(result.ravel(), np.array([1, 2, 3]))

if not _passed:
    print()
    print("Expected shape (3, 1) containing [1, 2, 3]")
""",
    "`v[:, np.newaxis]` adds a new axis at position 1.",
    """
def to_column(v):
    return v[:, np.newaxis]
""",
)

lesson_cells += exercise_cells(
    "5.2",
    "First channel of any stack of images",
    """
Write `first_channel(images)` that takes an array of shape
`(n_images, height, width, n_channels)` (or any number of leading axes
followed by a channel axis last) and returns just channel 0 for every
image, using `...` so your function works regardless of how many
leading axes there are.
""",
    """
def first_channel(images):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
imgs = np.arange(2 * 4 * 4 * 3).reshape(2, 4, 4, 3)
result = first_channel(imgs)
print("first_channel(imgs) with imgs.shape ==", imgs.shape, "->")
print(result)

expected = imgs[:, :, :, 0]
_passed = result.shape == (2, 4, 4) and np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`images[..., 0]` takes channel 0 regardless of how many axes come before it.",
    """
def first_channel(images):
    return images[..., 0]
""",
)

# ---------------------------------------------------------------------------
# Wrap-up
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## 🎯 Key Takeaways

- Index one axis at a time with `arr[rows, cols]`; negative indices and
  step slices (`::2`, `::-1`) work on every axis.
- Boolean masks (`arr > 0`) filter data; combine conditions with `&`/`|`/`~`,
  never Python's `and`/`or`/`not`. `np.where` is the vectorized if/else.
- Fancy indexing (`arr[[0, 2, 4]]`) lets you pick, repeat, and reorder
  elements arbitrarily — and always returns a copy.
- **Basic slicing returns a view; boolean and fancy indexing return a
  copy.** Mutating a view mutates the original array. Use `.copy()` when
  you need independence, and `np.shares_memory` to check.
- `np.newaxis` inserts a length-1 axis (crucial for broadcasting); `...`
  stands in for "all the remaining axes."

Next up: **Module 3 — Array Operations & Broadcasting**, where the shapes
you've been building here start combining with each other automatically.
"""
    )
]

nb = build_notebook(TITLE, FILENAME, intro_cells, lesson_cells)
save_notebook(nb, FILENAME)
print(f"Wrote {FILENAME} with {len(nb['cells'])} cells.")
