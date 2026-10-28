"""Builds module_6_performance_projects.ipynb — Performance, I/O & Mini-Projects.
This is the final module of the course.

Run with: python build_module_6.py
"""
from nb_utils import md, code, exercise_cells, build_notebook, save_notebook

FILENAME = "module_6_performance_projects.ipynb"
TITLE = "Module 6 — Performance, I/O & Mini-Projects"

intro_cells = [
    md(
        """
## Welcome

This is the last module of the course. The first four lessons round out
your mental model of NumPy's performance characteristics — memory layout,
vectorization patterns, and I/O — and the last two put everything you've
learned in Modules 1-5 to work in two end-to-end mini-projects.

**Learning goals**
- Read `.strides` and distinguish C order from Fortran order
- Avoid hidden costs: in-place ops with `out=`, preallocation vs growing
- Save/load arrays with `.npy`/`.npz`/text formats (round-tripped in memory)
- Build and sort structured arrays with named fields
- Apply the whole course to an image-as-array mini-project
- Apply the whole course to a stock-price-as-array mini-project

**Setup** — run this first.
"""
    ),
    code(
        """
import io
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
## Lesson 1 — Memory Layout: Strides & Order

`.strides` tells you how many **bytes** to step to move one position along
each axis. For a C-order (row-major, the default) `(2, 3)` array of
`float64`, moving one column over costs 8 bytes, but moving one row down
costs `3 * 8 = 24` bytes — because rows are stored one after another in
memory.

Fortran order (`order="F"`) stores **columns** contiguously instead — the
strides flip. This is why `.T` (transpose) is instant and never copies data:
it just swaps the strides and shape, leaving the underlying buffer alone.
That also means a transposed array is usually **not C-contiguous** anymore.
When an algorithm (or a library written in C) genuinely needs a contiguous
buffer, use `np.ascontiguousarray(arr)` — it returns `arr` itself if it's
already contiguous, and a real copy only if it isn't.
"""
    ),
    code(
        """
a = np.arange(6, dtype=np.float64).reshape(2, 3)
print("C-order strides:", a.strides)       # (24, 8): 24 bytes per row, 8 per column
print("is C-contiguous:", a.flags["C_CONTIGUOUS"])

at = a.T
print("\\ntransposed strides:", at.strides)   # strides just swapped, no copy
print("transpose is C-contiguous:", at.flags["C_CONTIGUOUS"])
print("transpose shares memory with a:", np.shares_memory(a, at))

f = np.asfortranarray(a)
print("\\nFortran-order strides:", f.strides)
"""
    ),
]

lesson_cells += exercise_cells(
    "1.1",
    "Spot the view",
    """
Write `second_row_view(matrix)` that returns a **view** (not a copy) of row
index `1` of a 2-D array, using basic slicing.
""",
    """
def second_row_view(matrix):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
m = np.arange(12).reshape(3, 4)
result = second_row_view(m)
print("second_row_view(m) ->")
print(result)

shares_memory = np.shares_memory(result, m)
print()
print("np.shares_memory(result, m) ->", shares_memory)

expected = np.array([4, 5, 6, 7])
_passed = np.array_equal(result, expected) and shares_memory

if _passed:
    result[0] = 999
    _passed = bool(m[1, 0] == 999)

if not _passed:
    print()
    print("Expected: a VIEW (shares memory with m) equal to", expected,
          "— and mutating it should mutate m too")
""",
    "Plain slicing with `matrix[1]` (or `matrix[1, :]`) already returns a view — "
    "no `.copy()` needed.",
    """
def second_row_view(matrix):
    return matrix[1]
""",
)

lesson_cells += exercise_cells(
    "1.2",
    "Force a contiguous copy",
    """
Write `ensure_contiguous(arr)` that returns a C-contiguous version of
`arr`. If `arr` is already C-contiguous, return it unchanged (same
underlying buffer); otherwise return a new, C-contiguous array with the
same shape and values.
""",
    """
def ensure_contiguous(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
base = np.arange(6).reshape(2, 3)
same = ensure_contiguous(base)
print("ensure_contiguous(base) ->")
print(same)

already_contiguous_ok = np.shares_memory(same, base)
print()
print("np.shares_memory(result, base) (already contiguous, should be True) ->", already_contiguous_ok)

transposed = base.T
fixed = ensure_contiguous(transposed)
print()
print("ensure_contiguous(base.T) ->")
print(fixed)
print("is C-contiguous:", fixed.flags["C_CONTIGUOUS"])

_passed = (
    already_contiguous_ok
    and fixed.flags["C_CONTIGUOUS"]
    and np.array_equal(fixed, transposed)
)

if not _passed:
    print()
    print("Expected: base returned as-is (same memory), and a C-contiguous "
          "copy of base.T with the same values as:")
    print(transposed)
""",
    "`np.ascontiguousarray` does exactly this: no-op copy if already "
    "contiguous, real copy otherwise.",
    """
def ensure_contiguous(arr):
    return np.ascontiguousarray(arr)
""",
)

# ---------------------------------------------------------------------------
# Lesson 2
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 2 — Vectorization Performance Patterns

Three habits keep NumPy code fast:

1. **Never grow an array in a loop.** Appending to a Python list and
   converting once at the end is fine; calling `np.append`/`np.concatenate`
   inside a loop reallocates the whole buffer every iteration.
2. **Preallocate when you must fill incrementally** — `np.empty(shape)` or
   `np.zeros(shape)` once, then assign into slices.
3. **Reuse buffers with `out=`** when you don't need the original array
   anymore — `np.add(a, b, out=a)` writes the result into `a`'s existing
   memory instead of allocating a new array.
"""
    ),
    code(
        """
import time

n = 2_000_000
a = np.arange(n, dtype=np.float64)
b = np.ones(n)

start = time.perf_counter()
c = a + b                      # allocates a brand-new array
print(f"new allocation: {time.perf_counter() - start:.5f}s")

start = time.perf_counter()
np.add(a, b, out=a)            # reuses a's memory, no new allocation
print(f"in-place (out=): {time.perf_counter() - start:.5f}s")
"""
    ),
]

lesson_cells += exercise_cells(
    "2.1",
    "Increment in place",
    """
Write `increment_in_place(arr, amount)` that adds `amount` to every
element of `arr` **in place** (using the `out=` parameter so no new array
is allocated) and returns `arr` itself.
""",
    """
def increment_in_place(arr, amount):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
original = np.array([1.0, 2.0, 3.0])
result = increment_in_place(original, 5.0)
print("increment_in_place(np.array([1.0, 2.0, 3.0]), 5.0) ->")
print(result)

same_object = result is original
print()
print("result is original (must be mutated in place) ->", same_object)

expected = np.array([6.0, 7.0, 8.0])
_passed = same_object and np.allclose(original, expected)

if not _passed:
    print()
    print("Expected: the SAME array object, mutated in place to", expected)
""",
    "`np.add(arr, amount, out=arr)` writes the result back into `arr` and "
    "also returns `arr`.",
    """
def increment_in_place(arr, amount):
    return np.add(arr, amount, out=arr)
""",
)

lesson_cells += exercise_cells(
    "2.2",
    "Running totals, no loop",
    """
Write `running_totals(values)` that returns the cumulative sum of a 1-D
array (`result[i]` = sum of `values[0..i]`) without writing a Python `for`
or `while` loop.
""",
    """
def running_totals(values):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = running_totals(np.array([1, 2, 3, 4]))
print("running_totals(np.array([1, 2, 3, 4])) ->")
print(result)

expected = np.array([1, 3, 6, 10])
_passed = np.array_equal(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "There's a single built-in NumPy function that does exactly this: "
    "`np.cumsum`.",
    """
def running_totals(values):
    return np.cumsum(values)
""",
)

# ---------------------------------------------------------------------------
# Lesson 3
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 3 — Saving & Loading Arrays

- `np.save` / `np.load` write a **single** array to a binary `.npy` file.
- `np.savez` / `np.load` write **several named** arrays to one `.npz`
  archive (loading returns an `NpzFile` you index like a dict).
- `np.savetxt` / `np.loadtxt` write a plain-text, CSV-like format — human
  readable, but slower and loses exact dtype information.

All three normally take a file path, but they're equally happy with an
in-memory file-like object (`io.BytesIO` for the binary formats,
`io.StringIO` for text) — handy for round-tripping without touching disk,
which is exactly what the exercises below do. **Remember to `seek(0)`** on
the buffer after writing and before reading, since writing leaves the
buffer's position at the end.
"""
    ),
    code(
        """
arr = np.array([1, 2, 3, 4])

buf = io.BytesIO()
np.save(buf, arr)
buf.seek(0)
loaded = np.load(buf)
print("single array round-trip:", loaded)

buf2 = io.BytesIO()
np.savez(buf2, first=arr, second=arr * 10)
buf2.seek(0)
archive = np.load(buf2)
print("multi-array round-trip:", archive["first"], archive["second"])
"""
    ),
]

lesson_cells += exercise_cells(
    "3.1",
    "Round-trip a single array",
    """
Write `roundtrip_npy(arr)` that writes `arr` to an in-memory `io.BytesIO`
buffer with `np.save`, reads it back with `np.load`, and returns the
loaded array.
""",
    """
def roundtrip_npy(arr):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
original = np.array([3.5, -1.0, 2.25])
result = roundtrip_npy(original)
print("roundtrip_npy(np.array([3.5, -1.0, 2.25])) ->")
print(result)

_passed = np.allclose(result, original) and result is not original

if not _passed:
    print()
    print("Expected: a freshly loaded array (not the same object), equal to", original)
""",
    "`buf = io.BytesIO()`, then `np.save(buf, arr)`, then `buf.seek(0)` "
    "before `np.load(buf)`.",
    """
def roundtrip_npy(arr):
    buf = io.BytesIO()
    np.save(buf, arr)
    buf.seek(0)
    return np.load(buf)
""",
)

lesson_cells += exercise_cells(
    "3.2",
    "Round-trip two named arrays",
    """
Write `roundtrip_npz(a, b)` that saves `a` and `b` into one in-memory
`.npz` archive under the keys `"a"` and `"b"` with `np.savez`, reloads it,
and returns a plain `dict` `{"a": ..., "b": ...}` of the loaded arrays.
""",
    """
def roundtrip_npz(a, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
a = np.array([1, 2, 3])
b = np.array([[1, 2], [3, 4]])
result = roundtrip_npz(a, b)
print("roundtrip_npz(a, b) ->")
print(result)

_passed = (
    isinstance(result, dict)
    and set(result.keys()) == {"a", "b"}
    and np.array_equal(result.get("a"), a)
    and np.array_equal(result.get("b"), b)
)

if not _passed:
    print()
    print("Expected:")
    print({"a": a, "b": b})
""",
    "`np.savez(buf, a=a, b=b)`, `buf.seek(0)`, then `np.load(buf)` returns "
    "an `NpzFile` — index it with `[\"a\"]` and `[\"b\"]`.",
    """
def roundtrip_npz(a, b):
    buf = io.BytesIO()
    np.savez(buf, a=a, b=b)
    buf.seek(0)
    archive = np.load(buf)
    return {"a": archive["a"], "b": archive["b"]}
""",
)

# ---------------------------------------------------------------------------
# Lesson 4
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 4 — Structured Arrays

A **structured array** has a dtype made of named fields, so each element
is a small fixed-layout record rather than a single number — useful for
tabular data when you don't want to bring in `pandas`. Define the dtype
with a list of `(field_name, field_dtype)` pairs, then index a field by
name like a dict key. `np.sort(arr, order="field_name")` sorts the whole
array by one field.
"""
    ),
    code(
        """
dtype = np.dtype([("name", "U10"), ("age", "i4"), ("score", "f8")])
people = np.array(
    [("Ana", 34, 91.5), ("Boris", 29, 88.0), ("Chiko", 41, 95.25)],
    dtype=dtype,
)
print(people["name"])
print(people["score"])

by_age = np.sort(people, order="age")
print(by_age)
"""
    ),
]

lesson_cells += exercise_cells(
    "4.1",
    "Build a structured array",
    """
Write `make_people(names, ages, scores)` that takes three equal-length
sequences and returns a structured array with dtype
`[("name", "U10"), ("age", "i4"), ("score", "f8")]`, one record per
input triple.
""",
    """
def make_people(names, ages, scores):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = make_people(["Ana", "Boris"], [34, 29], [91.5, 88.0])
print('make_people(["Ana", "Boris"], [34, 29], [91.5, 88.0]) ->')
print(result)

_passed = (
    result.dtype.names == ("name", "age", "score")
    and result[0]["name"] == "Ana"
    and result[0]["age"] == 34
    and np.isclose(result[1]["score"], 88.0)
)

if not _passed:
    print()
    print('Expected: a structured array with fields ("name", "age", "score"), '
          'first record name "Ana"/age 34, second record score ≈ 88.0')
""",
    "Zip the three sequences into a list of tuples, then pass that list "
    "and the dtype straight to `np.array(...)`.",
    """
def make_people(names, ages, scores):
    dtype = np.dtype([("name", "U10"), ("age", "i4"), ("score", "f8")])
    records = list(zip(names, ages, scores))
    return np.array(records, dtype=dtype)
""",
)

lesson_cells += exercise_cells(
    "4.2",
    "Sort by score",
    """
Write `sort_by_score(people)` that takes a structured array with a
`"score"` field and returns it sorted in **ascending** order by that
field.
""",
    """
def sort_by_score(people):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
dtype = np.dtype([("name", "U10"), ("age", "i4"), ("score", "f8")])
people = np.array(
    [("Ana", 34, 91.5), ("Boris", 29, 88.0), ("Chiko", 41, 95.25)],
    dtype=dtype,
)
result = sort_by_score(people)
print("sort_by_score(people) ->")
print(result)

expected_names = ["Boris", "Ana", "Chiko"]
_passed = list(result["name"]) == expected_names and np.all(np.diff(result["score"]) >= 0)

if not _passed:
    print()
    print("Expected names in ascending-score order:", expected_names)
""",
    "`np.sort` takes an `order=` keyword for structured arrays — "
    "`np.sort(people, order=\"score\")`.",
    """
def sort_by_score(people):
    return np.sort(people, order="score")
""",
)

# ---------------------------------------------------------------------------
# Lesson 5 — Capstone: Image manipulation
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 5 — Capstone: Image Manipulation with NumPy

A grayscale image is nothing more than a 2-D array of brightness values
(`0`-`255`). Every "image processing" operation below is really just
array indexing, broadcasting, and boolean masking — the exact tools from
Modules 1-3, no special image library required.

Below we synthesize a small 40×40 image containing a bright square and a
bright circle on a dark background, purely from array operations (no file
is loaded, so this runs identically anywhere, including Colab).
"""
    ),
    code(
        """
rng = np.random.default_rng(seed=7)

size = 40
img = rng.integers(0, 40, size=(size, size)).astype(np.uint8)  # dim background noise

# bright square: rows/cols 5..15
img[5:15, 5:15] = 220

# bright circle of radius 10 centered at (28, 28)
yy, xx = np.indices((size, size))
circle_mask = (yy - 28) ** 2 + (xx - 28) ** 2 <= 10 ** 2
img[circle_mask] = 200

plt.imshow(img, cmap="gray", vmin=0, vmax=255)
plt.title("Synthetic grayscale image")
plt.colorbar()
plt.show()
"""
    ),
    md(
        """
Every slice you write, like `img[5:15, 5:15]` above, is really Python
building a `slice(5, 15)` object per axis and handing a tuple of them to
`img.__getitem__`. Because that's just an object, you can construct it
yourself, store it in a variable, and use it later — `row_slice = slice(5, 15)`
then `img[row_slice]` is identical to `img[5:15]`. For multiple axes, a
tuple of slices works the same way: `(slice(5, 15), slice(0, 10))` is the
same index as `img[5:15, 0:10]`. The exercise below asks you to accept a
`crop_slice` built this way, so the caller can crop to whatever region it
wants.
"""
    ),
    code(
        """
# `a:b` syntax and an explicit slice object are the same thing.
row_slice = slice(5, 15)
print(np.array_equal(img[5:15, 5:15], img[row_slice, row_slice]))

# A tuple of slices works for multi-dimensional indexing too.
region = (slice(5, 15), slice(0, 10))
print(np.array_equal(img[region], img[5:15, 0:10]))
"""
    ),
]

lesson_cells += exercise_cells(
    "5.1",
    "Threshold, crop, and measure brightness",
    """
Write `analyze_image(img, threshold, crop_slice)` that performs three
chained steps on a 2-D grayscale array `img`:

1. Build a boolean `"mask"` the same shape as `img` where pixels are
   strictly greater than `threshold`.
2. Build a `"crop"`: the sub-array `img[crop_slice]`, where `crop_slice`
   is a tuple of two `slice` objects (one per axis) — e.g.
   `(slice(0, 10), slice(0, 10))`.
3. Compute `"bright_fraction"`: the fraction (a Python `float` between 0
   and 1) of pixels **within that crop** that are strictly greater than
   `threshold`.

Return a dict with exactly the keys `"mask"`, `"crop"`, and
`"bright_fraction"`.
""",
    """
def analyze_image(img, threshold, crop_slice):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
test_img = np.array([
    [10, 10, 200, 200],
    [10, 10, 200, 200],
    [5,  5,  5,   5],
    [5,  5,  5,   5],
])
crop_slice = (slice(0, 2), slice(0, 4))
result = analyze_image(test_img, 100, crop_slice)
print("analyze_image(test_img, 100, crop_slice) ->")
print(result)

expected_mask = test_img > 100
expected_crop = test_img[crop_slice]
expected_fraction = 0.5  # 4 of 8 crop pixels are 200

_passed = (
    isinstance(result, dict)
    and set(result.keys()) == {"mask", "crop", "bright_fraction"}
    and result["mask"].shape == test_img.shape
    and result["mask"].dtype == bool
    and np.array_equal(result["mask"], expected_mask)
    and np.array_equal(result["crop"], expected_crop)
    and np.isclose(result["bright_fraction"], expected_fraction)
)

if not _passed:
    print()
    print("Expected:")
    print({"mask": expected_mask, "crop": expected_crop, "bright_fraction": expected_fraction})
""",
    "`mask = img > threshold`. `crop = img[crop_slice]`. For the fraction, "
    "reuse the mask but computed on the crop (or slice the mask itself with "
    "`crop_slice`) and take `.mean()` of the boolean array — the mean of a "
    "boolean array IS the fraction of `True` values.",
    """
def analyze_image(img, threshold, crop_slice):
    mask = img > threshold
    crop = img[crop_slice]
    bright_fraction = float((crop > threshold).mean())
    return {"mask": mask, "crop": crop, "bright_fraction": bright_fraction}
""",
)

# ---------------------------------------------------------------------------
# Lesson 6 — Capstone: Stock price analysis
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 6 — Capstone: Analyzing a Stock Price Series

We'll model a daily closing-price series as a **random walk**: start at
some price, then repeatedly add a small random daily change. This is
synthetic data (seeded, so it's reproducible), but the *analysis* below is
exactly what you'd run on a real price series.

One technique here hasn't been taught yet: a **rolling mean without
pandas**. `np.convolve(prices, kernel, mode="valid")`, with
`kernel = np.ones(window) / window`, slides a length-`window` averaging
kernel across the series and keeps only the positions where the kernel
fully overlaps the data (`mode="valid"`) — so the result has length
`len(prices) - window + 1`. It's a vectorized way to compute a moving
average with zero explicit loops.
"""
    ),
    code(
        """
rng = np.random.default_rng(seed=42)

n_days = 250
daily_changes = rng.normal(loc=0.05, scale=1.0, size=n_days)
prices = 100 + np.cumsum(daily_changes)

plt.plot(prices)
plt.title("Synthetic daily closing price")
plt.xlabel("day")
plt.ylabel("price")
plt.show()

window = 10
kernel = np.ones(window) / window
rolling = np.convolve(prices, kernel, mode="valid")
print("prices:", prices.shape, "rolling mean:", rolling.shape)
"""
    ),
]

lesson_cells += exercise_cells(
    "6.1",
    "Returns, worst day, and a rolling mean",
    """
Write `analyze_prices(prices, window)` that performs three chained
computations on a 1-D array of daily closing prices:

1. `"daily_returns"`: a vectorized array of length `len(prices) - 1` where
   `daily_returns[i] = prices[i+1] / prices[i] - 1` (no Python loop).
2. `"worst_day_index"` and `"worst_day_return"`: the index into
   `daily_returns` of the single worst (most negative) daily return, and
   that return's value.
3. `"rolling_mean"`: the simple moving average of `prices` over `window`
   days, computed with `np.convolve` and `mode="valid"` as described above
   (length `len(prices) - window + 1`).

Return a dict with exactly the keys `"daily_returns"`, `"worst_day_index"`,
`"worst_day_return"`, and `"rolling_mean"`.
""",
    """
def analyze_prices(prices, window):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
prices = np.array([100.0, 102.0, 101.0, 95.0, 105.0, 107.0])
result = analyze_prices(prices, window=3)
print("analyze_prices(prices, window=3) ->")
print(result)

expected_returns = prices[1:] / prices[:-1] - 1
expected_worst_idx = int(np.argmin(expected_returns))
expected_worst_return = expected_returns[expected_worst_idx]
kernel = np.ones(3) / 3
expected_rolling = np.convolve(prices, kernel, mode="valid")

_passed = (
    isinstance(result, dict)
    and set(result.keys()) == {
        "daily_returns", "worst_day_index", "worst_day_return", "rolling_mean"
    }
    and np.allclose(result["daily_returns"], expected_returns)
    and result["worst_day_index"] == expected_worst_idx
    and np.isclose(result["worst_day_return"], expected_worst_return)
    and np.allclose(result["rolling_mean"], expected_rolling)
    and len(result["rolling_mean"]) == len(prices) - 3 + 1
)

if not _passed:
    print()
    print("Expected:")
    print({
        "daily_returns": expected_returns,
        "worst_day_index": expected_worst_idx,
        "worst_day_return": expected_worst_return,
        "rolling_mean": expected_rolling,
    })
""",
    "`daily_returns = prices[1:] / prices[:-1] - 1`. Use `np.argmin` for "
    "the worst index, then index back into `daily_returns` for its value. "
    "For the rolling mean, build `kernel = np.ones(window) / window` and "
    "call `np.convolve(prices, kernel, mode=\"valid\")`.",
    """
def analyze_prices(prices, window):
    daily_returns = prices[1:] / prices[:-1] - 1
    worst_day_index = int(np.argmin(daily_returns))
    worst_day_return = float(daily_returns[worst_day_index])
    kernel = np.ones(window) / window
    rolling_mean = np.convolve(prices, kernel, mode="valid")
    return {
        "daily_returns": daily_returns,
        "worst_day_index": worst_day_index,
        "worst_day_return": worst_day_return,
        "rolling_mean": rolling_mean,
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

- `.strides` and C-vs-Fortran order explain *why* transpose is free and
  why some operations need `np.ascontiguousarray` first.
- Avoid hidden allocation costs: preallocate instead of growing arrays,
  and use `out=` for in-place ops when you don't need the original.
- `np.save`/`load`, `np.savez`, and `np.savetxt`/`loadtxt` cover binary,
  multi-array, and text persistence — all work with in-memory buffers too.
- Structured arrays give you named, typed fields without needing `pandas`.
- Both capstones were just Modules 1-5's tools — indexing, broadcasting,
  aggregation, sorting — aimed at a concrete problem.
"""
    ),
    md(
        """
## 🎓 Course Complete!

You've made it through the whole course:

1. **NumPy Fundamentals & Array Creation** — what an array is, and every
   way to build one.
2. **Indexing, Slicing & Views** — selecting exactly the data you want,
   and knowing when you get a view vs. a copy.
3. **Array Operations & Broadcasting** — vectorized math and the
   broadcasting rules that make it work across shapes.
4. **Aggregations, Statistics & Sorting** — summarizing and ordering data
   along any axis.
5. **Linear Algebra & Random** — vectors, matrices, and reproducible
   randomness.
6. **Performance, I/O & Mini-Projects** — memory layout, persistence, and
   two real mini-projects tying it all together.

**Where to go next:**
- **pandas** — labeled, tabular data built on top of NumPy arrays.
- **matplotlib** / **seaborn** — deeper, more polished visualization.
- **scipy** — advanced scientific computing (optimization, signal
  processing, statistics) that extends what you've learned here.

Nicely done — go build something with it. 🎉
"""
    ),
]

nb = build_notebook(TITLE, FILENAME, intro_cells, lesson_cells)
save_notebook(nb, FILENAME)
print(f"Wrote {FILENAME} with {len(nb['cells'])} cells.")
