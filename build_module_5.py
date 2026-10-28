"""Builds module_5_linalg_random.ipynb — Linear Algebra & Random.

Run with: python build_module_5.py
"""
from nb_utils import md, code, exercise_cells, build_notebook, save_notebook

FILENAME = "module_5_linalg_random.ipynb"
TITLE = "Module 5 — Linear Algebra & Random"

intro_cells = [
    md(
        """
## Welcome

This module covers two pillars of scientific computing with NumPy: linear
algebra (vectors, matrices, and the equations that relate them) and random
number generation (sampling, simulation, and reproducibility). Together
they're the backbone of everything from graphics to machine learning to
Monte Carlo simulation — which is exactly where this module ends up.

**Learning goals**
- Compute dot products, norms, and cosine similarity between vectors
- Multiply matrices with `@` and know how it differs from elementwise `*`
- Solve linear systems with `np.linalg.solve` instead of inverting matrices by hand
- Find eigenvalues/eigenvectors and verify them directly from their definition
- Generate reproducible random numbers with the modern `Generator` API
- Combine random sampling with vectorized boolean indexing to run a simulation

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
## Lesson 1 — Vectors & Dot Products

The **dot product** of two same-length vectors, `np.dot(a, b)` or simply
`a @ b`, multiplies corresponding elements and sums the results. It shows
up everywhere: it's the core of matrix multiplication (next lesson), and
`np.linalg.norm(v)` — a vector's length/magnitude — is just
`sqrt(v @ v)`.

A useful derived quantity is **cosine similarity**, which measures the
angle between two vectors regardless of their length:

```
cos(theta) = (a @ b) / (||a|| * ||b||)
```

It ranges from `-1` (opposite direction) to `1` (same direction), with `0`
meaning the vectors are orthogonal.
"""
    ),
    code(
        """
a = np.array([1.0, 2.0, 3.0])
b = np.array([4.0, 5.0, 6.0])

print("dot:   ", np.dot(a, b), a @ b)
print("norm a:", np.linalg.norm(a), np.sqrt(a @ a))

cos_theta = (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))
print("cos similarity:", cos_theta)
"""
    ),
]

lesson_cells += exercise_cells(
    "1.1",
    "Unit vector",
    """
Write `to_unit_vector(v)` that returns `v` scaled to have length (norm)
exactly `1`, pointing in the same direction. Use `np.linalg.norm`.
""",
    """
def to_unit_vector(v):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result = to_unit_vector(np.array([3.0, 4.0]))
print("to_unit_vector(np.array([3.0, 4.0])) ->")
print(result)

expected = np.array([0.6, 0.8])
_passed = np.allclose(np.linalg.norm(result), 1.0) and np.allclose(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Divide `v` by `np.linalg.norm(v)`.",
    """
def to_unit_vector(v):
    return v / np.linalg.norm(v)
""",
)

lesson_cells += exercise_cells(
    "1.2",
    "Cosine similarity",
    """
Write `cosine_similarity(a, b)` that returns the cosine similarity between
two 1-D vectors, as defined above.
""",
    """
def cosine_similarity(a, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
same_dir = cosine_similarity(np.array([1.0, 0.0]), np.array([5.0, 0.0]))
print("cosine_similarity([1, 0], [5, 0]) ->")
print(same_dir)

orthogonal = cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
opposite = cosine_similarity(np.array([1.0, 0.0]), np.array([-1.0, 0.0]))
print("cosine_similarity([1, 0], [0, 1]) ->", orthogonal)
print("cosine_similarity([1, 0], [-1, 0]) ->", opposite)

_passed = (
    np.allclose(same_dir, 1.0)
    and np.allclose(orthogonal, 0.0)
    and np.allclose(opposite, -1.0)
)

if not _passed:
    print()
    print("Expected: 1.0, 0.0, and -1.0 respectively")
""",
    "`(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))` — just transcribe "
    "the formula above.",
    """
def cosine_similarity(a, b):
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))
""",
)

# ---------------------------------------------------------------------------
# Lesson 2
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 2 — Matrix Multiplication

For 2-D arrays, `@` performs real **matrix multiplication**: given
`A` of shape `(m, n)` and `B` of shape `(n, p)`, `A @ B` has shape
`(m, p)`, where each entry is the dot product of a row of `A` and a
column of `B`. The inner dimensions (`n`) must match.

This is completely different from `A * B`, which is the **elementwise**
(Hadamard) product and requires `A` and `B` to have the same shape (or be
broadcastable) — there's no "inner dimension" concept at all.
"""
    ),
    code(
        """
A = np.array([[1, 2], [3, 4], [5, 6]])   # shape (3, 2)
B = np.array([[1, 0], [0, 1]])           # shape (2, 2)

print("A @ B shape:", (A @ B).shape)     # (3, 2)
print(A @ B)

C = np.array([[1, 2], [3, 4], [5, 6]])   # same shape as A
print("A * C (elementwise):")
print(A * C)
"""
    ),
]

lesson_cells += exercise_cells(
    "2.1",
    "Weighted row sums",
    """
Write `weighted_sums(matrix, weights)` that takes a `(m, n)` matrix and a
length-`n` `weights` vector, and returns a length-`m` vector where each
entry is the weighted sum of the corresponding row. Use a single matrix
multiplication — no loop.
""",
    """
def weighted_sums(matrix, weights):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
m = np.array([[1, 2, 3], [4, 5, 6]])
w = np.array([1, 0, 1])
result = weighted_sums(m, w)
print("weighted_sums(matrix, weights) ->")
print(result)

expected = np.array([4, 10])
_passed = np.allclose(result, expected)

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "`matrix @ weights` does exactly this: a `(m, n) @ (n,)` product gives "
    "a length-`m` vector.",
    """
def weighted_sums(matrix, weights):
    return matrix @ weights
""",
)

lesson_cells += exercise_cells(
    "2.2",
    "Matmul vs. Hadamard",
    """
Write `both_products(A, B)` that takes two same-shape square matrices and
returns a tuple `(matmul_result, hadamard_result)`: the true matrix product
`A @ B` and the elementwise product `A * B`.
""",
    """
def both_products(A, B):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
matmul_result, hadamard_result = both_products(A, B)
print("both_products(A, B) ->")
print("matmul:  ", matmul_result.tolist())
print("hadamard:", hadamard_result.tolist())

expected_matmul = A @ B
expected_hadamard = A * B
_passed = (
    np.array_equal(matmul_result, expected_matmul)
    and np.array_equal(hadamard_result, expected_hadamard)
    and not np.array_equal(matmul_result, hadamard_result)
)

if not _passed:
    print()
    print("Expected matmul:  ", expected_matmul.tolist())
    print("Expected hadamard:", expected_hadamard.tolist())
""",
    "Literally return `(A @ B, A * B)`.",
    """
def both_products(A, B):
    return A @ B, A * B
""",
)

# ---------------------------------------------------------------------------
# Lesson 3
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 3 — Solving Linear Systems

To solve `Ax = b` for `x`, use `np.linalg.solve(A, b)`. It is faster and
numerically more stable than computing `np.linalg.inv(A) @ b` — computing
a full inverse does unnecessary extra work and amplifies floating-point
error. **Prefer `solve` over `inv` whenever you just need `x`.**

`np.linalg.det(A)` computes the determinant. A matrix with `det(A) == 0`
is **singular** — it has no unique inverse, and `np.linalg.solve` will
raise a `LinAlgError` for it.

That said, not every LAPACK build raises reliably for a singular matrix —
some just hand back `nan`/`inf` values instead of erroring. `np.isfinite(x)`
is the elementwise check for exactly this: it returns `False` wherever a
value is `nan` or `inf`, and `True` everywhere else, so `np.all(np.isfinite(x))`
tells you in one line whether an entire array/result is "clean" (no
`nan`/`inf` anywhere).
"""
    ),
    code(
        """
A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])

x = np.linalg.solve(A, b)
print("solution x:", x)
print("check A @ x == b:", np.allclose(A @ x, b))
print("det(A):", np.linalg.det(A))

singular = np.array([[1.0, 2.0], [2.0, 4.0]])   # second row = 2 * first row
print("det(singular):", np.linalg.det(singular))
try:
    np.linalg.solve(singular, np.array([1.0, 2.0]))
except np.linalg.LinAlgError as e:
    print("LinAlgError:", e)
"""
    ),
]

lesson_cells += exercise_cells(
    "3.1",
    "Solve or report singular",
    """
Write `solve_or_none(A, b)` that returns the solution vector `x` to
`Ax = b` using `np.linalg.solve`, or returns `None` if `A` is singular.
Catch `LinAlgError` — but also treat a result containing `nan`/`inf` as
singular: depending on the exact LAPACK build, `np.linalg.solve` doesn't
always *raise* for a singular matrix, it sometimes just returns garbage
values instead, so a robust solution checks both.
""",
    """
def solve_or_none(A, b):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])
result = solve_or_none(A, b)
print("solve_or_none(A, b) ->")
print(result)

ok_basic = result is not None and np.allclose(A @ result, b)

singular = np.array([[1.0, 2.0], [2.0, 4.0]])
singular_result = solve_or_none(singular, np.array([1.0, 2.0]))
print()
print("solve_or_none(singular_matrix, b) ->", singular_result)

_passed = ok_basic and singular_result is None

if not _passed:
    print()
    print("Expected: a vector x with A @ x ≈ b for the first call, and None for the singular matrix")
""",
    "Wrap `np.linalg.solve(A, b)` in a `try/except np.linalg.LinAlgError` "
    "and return `None` in the `except` branch — then also check "
    "`np.all(np.isfinite(x))` on whatever it returns, since a singular "
    "matrix doesn't always raise.",
    """
def solve_or_none(A, b):
    try:
        x = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return None
    return x if np.all(np.isfinite(x)) else None
""",
)

lesson_cells += exercise_cells(
    "3.2",
    "Is it singular?",
    """
Write `is_singular(A, tol=1e-10)` that returns `True` if the square matrix
`A` is singular (its determinant is within `tol` of zero), `False`
otherwise.
""",
    """
def is_singular(A, tol=1e-10):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
result_1 = is_singular(np.array([[1.0, 2.0], [2.0, 4.0]]))
result_2 = is_singular(np.array([[3.0, 1.0], [1.0, 2.0]]))
print("is_singular(singular_matrix) ->", result_1)
print("is_singular(regular_matrix)  ->", result_2)

_passed = bool(result_1) and not bool(result_2)

if not _passed:
    print()
    print("Expected: True for the singular matrix, False for the regular one")
""",
    "Compute `np.linalg.det(A)` and compare `abs(det)` against `tol`.",
    """
def is_singular(A, tol=1e-10):
    return abs(np.linalg.det(A)) < tol
""",
)

# ---------------------------------------------------------------------------
# Lesson 4
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 4 — Eigenvalues & Eigenvectors

For a square matrix `A`, an **eigenvector** `v` is a (nonzero) vector whose
direction doesn't change when `A` is applied to it — only its length
scales, by a factor called the **eigenvalue** `λ`:

```
A @ v == λ * v
```

`np.linalg.eig(A)` returns `(eigenvalues, eigenvectors)`, where
`eigenvectors[:, i]` is the eigenvector for `eigenvalues[i]`.

For non-square matrices there's no eigendecomposition, but there is an
analogous, even more general tool: the **Singular Value Decomposition**
(`np.linalg.svd`), which factors *any* matrix into rotation/scaling
components — useful for things like dimensionality reduction, but outside
the scope of this lesson's exercises.
"""
    ),
    code(
        """
A = np.array([[2.0, 0.0], [0.0, 3.0]])
eigenvalues, eigenvectors = np.linalg.eig(A)
print("eigenvalues: ", eigenvalues)
print("eigenvectors:\\n", eigenvectors)

v0 = eigenvectors[:, 0]
lam0 = eigenvalues[0]
print("A @ v0:   ", A @ v0)
print("lam0 * v0:", lam0 * v0)
print("match:", np.allclose(A @ v0, lam0 * v0))
"""
    ),
]

lesson_cells += exercise_cells(
    "4.1",
    "Verify an eigenpair",
    """
Write `is_eigenpair(A, v, lam, tol=1e-8)` that returns `True` if
`A @ v` is within `tol` of `lam * v` (elementwise, via `np.allclose`),
`False` otherwise.
""",
    """
def is_eigenpair(A, v, lam, tol=1e-8):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
A = np.array([[2.0, 0.0], [0.0, 3.0]])
eigenvalues, eigenvectors = np.linalg.eig(A)

result_1 = is_eigenpair(A, eigenvectors[:, 0], eigenvalues[0])
print("is_eigenpair(A, eigenvectors[:, 0], eigenvalues[0]) ->")
print(result_1)

result_2 = is_eigenpair(A, eigenvectors[:, 1], eigenvalues[1])
result_3 = is_eigenpair(A, eigenvectors[:, 0], eigenvalues[1])
print("is_eigenpair(A, eigenvectors[:, 1], eigenvalues[1]) ->", result_2)
print("is_eigenpair(A, eigenvectors[:, 0], eigenvalues[1]) (mismatched) ->", result_3)

_passed = bool(result_1) and bool(result_2) and not result_3

if not _passed:
    print()
    print("Expected: True, True, False")
""",
    "`np.allclose(A @ v, lam * v, atol=tol)`.",
    """
def is_eigenpair(A, v, lam, tol=1e-8):
    return np.allclose(A @ v, lam * v, atol=tol)
""",
)

lesson_cells += exercise_cells(
    "4.2",
    "Dominant eigenvalue",
    """
Write `dominant_eigenvalue(A)` that returns the eigenvalue of `A` with the
largest absolute value, as a real float (eigenvalues from `np.linalg.eig`
come back as complex numbers even when the imaginary part is zero — use
`.real` after picking the right one, or take `abs()` for comparison and
return the original real part).
""",
    """
def dominant_eigenvalue(A):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
A = np.array([[2.0, 0.0], [0.0, 3.0]])
result = dominant_eigenvalue(A)
print("dominant_eigenvalue(A) ->")
print(result)

expected = 3.0
_passed = np.allclose(result, expected) and (isinstance(result, float) or np.isrealobj(result))

if not _passed:
    print()
    print("Expected:")
    print(expected)
""",
    "Get `eigenvalues` from `np.linalg.eig(A)`, use `np.argmax(np.abs(eigenvalues))` "
    "to find the index of the largest-magnitude one, then take `.real`.",
    """
def dominant_eigenvalue(A):
    eigenvalues, _ = np.linalg.eig(A)
    idx = np.argmax(np.abs(eigenvalues))
    return eigenvalues[idx].real
""",
)

# ---------------------------------------------------------------------------
# Lesson 5
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 5 — Random Number Generation with the Generator API

Modern NumPy code should create an explicit `Generator` instead of using
the legacy global functions (`np.random.seed`, `np.random.rand`, ...):

```python
rng = np.random.default_rng(seed=42)
```

A `Generator` gives you **reproducibility** (same seed -> same sequence)
*and* **independent streams** (two `default_rng()` calls never silently
share or clobber global state, which matters once you have multiple
pieces of code sampling randomness at once). The most common methods:

| Method | Produces |
|---|---|
| `rng.random(size)` | floats uniform in `[0, 1)` |
| `rng.integers(low, high, size)` | integers in `[low, high)` |
| `rng.normal(loc, scale, size)` | samples from a normal distribution |
| `rng.choice(a, size, replace=...)` | random samples from an array |

For `rng.choice`, `replace=True` (the default) can pick the same element
more than once; `replace=False` samples without repeats, like dealing
cards from a deck instead of rolling the same die repeatedly.
"""
    ),
    code(
        """
rng = np.random.default_rng(seed=42)
print(rng.random(3))
print(rng.integers(0, 10, size=5))
print(rng.normal(loc=0.0, scale=1.0, size=3))

# same seed -> same sequence, every time
rng_a = np.random.default_rng(seed=7)
rng_b = np.random.default_rng(seed=7)
print(np.array_equal(rng_a.random(5), rng_b.random(5)))

samples = np.random.default_rng(0).normal(size=10_000)
plt.hist(samples, bins=30)
plt.title("10,000 samples from a standard normal distribution")
plt.show()
"""
    ),
]

lesson_cells += exercise_cells(
    "5.1",
    "Reproducible dice rolls",
    """
Write `roll_dice(n_rolls, seed)` that returns an array of `n_rolls`
simulated six-sided die rolls (integers `1`-`6` inclusive), using
`np.random.default_rng(seed)`. The same `seed` must always produce the
same sequence.
""",
    """
def roll_dice(n_rolls, seed):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
rolls = roll_dice(1000, seed=1)
print("roll_dice(1000, seed=1) -> (first 20 of 1000)")
print(rolls[:20])

ok_shape = rolls.shape == (1000,)
ok_range = rolls.min() >= 1 and rolls.max() <= 6
ok_reproducible = np.array_equal(roll_dice(10, seed=5), roll_dice(10, seed=5))

_passed = ok_shape and ok_range and ok_reproducible

if not _passed:
    print()
    print("Expected: shape (1000,), every value in 1..6, and the same seed always giving the same rolls")
    print(f"(shape={rolls.shape}, min={rolls.min()}, max={rolls.max()}, reproducible={ok_reproducible})")
""",
    "`np.random.default_rng(seed).integers(1, 7, size=n_rolls)` — remember "
    "`integers`'s upper bound is exclusive, so use `7` to include `6`.",
    """
def roll_dice(n_rolls, seed):
    rng = np.random.default_rng(seed)
    return rng.integers(1, 7, size=n_rolls)
""",
)

lesson_cells += exercise_cells(
    "5.2",
    "Shuffle without replacement",
    """
Write `random_sample_no_replace(arr, k, seed)` that returns `k` elements
randomly chosen from `arr` *without* replacement (no duplicates), using
`rng.choice` with the right arguments.
""",
    """
def random_sample_no_replace(arr, k, seed):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
arr = np.arange(20)
result = random_sample_no_replace(arr, 5, seed=3)
print("random_sample_no_replace(np.arange(20), 5, seed=3) ->")
print(result)

ok_shape = result.shape == (5,)
ok_unique = len(set(result.tolist())) == 5
ok_subset = np.all(np.isin(result, arr))

_passed = ok_shape and ok_unique and ok_subset

if not _passed:
    print()
    print("Expected: 5 unique values, all drawn from the original array")
    print(f"(shape={result.shape}, unique={ok_unique}, subset={ok_subset})")
""",
    "`np.random.default_rng(seed).choice(arr, size=k, replace=False)`.",
    """
def random_sample_no_replace(arr, k, seed):
    rng = np.random.default_rng(seed)
    return rng.choice(arr, size=k, replace=False)
""",
)

# ---------------------------------------------------------------------------
# Lesson 6
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## Lesson 6 — Simulation Case Study: Monte Carlo Estimate of π

Here's a classic way to estimate π without any trigonometry: scatter
random points uniformly inside a `2x2` square centered at the origin, and
check what fraction land inside the unit circle inscribed in that square.

The area of the circle is `π * r²  = π` (since `r = 1`), and the area of
the square is `2 * 2 = 4`. So:

```
fraction inside circle ≈ π / 4   =>   π ≈ 4 * fraction inside circle
```

The whole "check what fraction land inside the circle" step is just
**boolean indexing** from Module 2 — no loop needed: generate `x` and `y`
coordinate arrays, build the mask `x**2 + y**2 <= 1`, and take its mean
(since a boolean array's mean IS the fraction of `True` values).
"""
    ),
    code(
        """
rng = np.random.default_rng(seed=0)
n = 100_000
x = rng.uniform(-1, 1, size=n)
y = rng.uniform(-1, 1, size=n)

inside = x**2 + y**2 <= 1
pi_estimate = 4 * inside.mean()
print("pi estimate:", pi_estimate)
print("true pi:    ", np.pi)

plt.figure(figsize=(4, 4))
plt.scatter(x[inside][:2000], y[inside][:2000], s=1, label="inside")
plt.scatter(x[~inside][:2000], y[~inside][:2000], s=1, label="outside")
plt.gca().set_aspect("equal")
plt.legend()
plt.title(f"Monte Carlo π ≈ {pi_estimate:.4f}")
plt.show()
"""
    ),
]

lesson_cells += exercise_cells(
    "6.1",
    "estimate_pi(n_samples, seed)",
    """
Write `estimate_pi(n_samples, seed)` that runs the Monte Carlo procedure
above: sample `n_samples` uniform `(x, y)` points in `[-1, 1] x [-1, 1]`
using `np.random.default_rng(seed)`, and return `4 * (fraction of points
with x**2 + y**2 <= 1)` as a float. Use vectorized operations only — no
Python loop over the samples.
""",
    """
def estimate_pi(n_samples, seed):
    # YOUR CODE HERE
    raise NotImplementedError
""",
    """
# With 200,000 samples and this fixed seed, the estimate is reliably
# within 0.02 of the true value — verified when writing this check.
result = estimate_pi(200_000, seed=42)
print("estimate_pi(200_000, seed=42) ->")
print(result)
print("true pi:", np.pi)

ok_close = abs(result - np.pi) < 0.02
ok_reproducible = estimate_pi(1000, seed=1) == estimate_pi(1000, seed=1)

_passed = ok_close and ok_reproducible

if not _passed:
    print()
    print(f"Expected: a value within 0.02 of {np.pi}, and the same seed always giving the same estimate")
""",
    "Reuse the exact pattern from the example above: `rng.uniform(-1, 1, "
    "size=n_samples)` for `x` and `y`, build the `inside` mask, return "
    "`4 * inside.mean()`.",
    """
def estimate_pi(n_samples, seed):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, size=n_samples)
    y = rng.uniform(-1, 1, size=n_samples)
    inside = x**2 + y**2 <= 1
    return 4 * inside.mean()
""",
)

# ---------------------------------------------------------------------------
# Wrap-up
# ---------------------------------------------------------------------------
lesson_cells += [
    md(
        """
## 🎯 Key Takeaways

- `np.dot`/`@` on vectors gives a scalar; `np.linalg.norm` gives length;
  cosine similarity measures direction regardless of magnitude.
- `@` on 2-D arrays is true matrix multiplication (`(m,n) @ (n,p) ->
  (m,p)`) — completely different from elementwise `*`, which needs
  matching/broadcastable shapes.
- Solve `Ax = b` with `np.linalg.solve`, not by inverting `A` — it's
  faster and more numerically stable. A zero determinant means `A` is
  singular and has no unique solution.
- `np.linalg.eig` gives eigenvalues/eigenvectors satisfying `A @ v == λ *
  v`; `np.linalg.svd` generalizes the idea to non-square matrices.
- Use `np.random.default_rng(seed)` for reproducible, independent random
  streams — never the legacy global `np.random.seed`/`rand` functions.
- Random sampling + vectorized boolean indexing (Module 2) is enough to
  build real simulations, like estimating π with Monte Carlo.

Next up: **Module 6 — Performance, I/O & Mini-Projects**, where you'll
learn how memory layout affects speed, how to save/load arrays, and put
everything from this course together in a few capstone exercises.
"""
    )
]

nb = build_notebook(TITLE, FILENAME, intro_cells, lesson_cells)
save_notebook(nb, FILENAME)
print(f"Wrote {FILENAME} with {len(nb['cells'])} cells.")
