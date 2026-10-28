// Loads Pyodide from the CDN (not bundled via npm — its wasm/data assets are too
// large and awkward for a Vite build to serve correctly) once per browser tab,
// cached on `window`, so navigating between lesson pages never re-downloads it.
declare global {
  interface Window {
    loadPyodide?: (opts: { indexURL: string }) => Promise<any>;
    __pyodidePromise?: Promise<any>;
  }
}

const PYODIDE_CDN = "https://cdn.jsdelivr.net/pyodide/v0.28.3/full/";

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });
}

export function getPyodide(): Promise<any> {
  if (typeof window === "undefined") {
    return Promise.reject(new Error("Pyodide can only load in the browser"));
  }
  if (!window.__pyodidePromise) {
    window.__pyodidePromise = (async () => {
      await loadScript(PYODIDE_CDN + "pyodide.js");
      const pyodide = await window.loadPyodide!({ indexURL: PYODIDE_CDN });
      await pyodide.loadPackage("numpy");
      return pyodide;
    })();
  }
  return window.__pyodidePromise;
}

const namespaces = new Map<string, any>();

/** Each exercise gets its own isolated Python namespace (so two exercises'
 * same-named helper functions never collide), reused across Run/Check clicks
 * for that one exercise so a student's state persists within it. */
function getNamespace(pyodide: any, exerciseId: string) {
  if (!namespaces.has(exerciseId)) {
    namespaces.set(exerciseId, pyodide.globals.get("dict")());
  }
  return namespaces.get(exerciseId);
}

export interface ExecutionResult {
  /** Everything the code printed to stdout (plus a trailing "⚠️ Error: ..."
   * line if it raised) — this is what the UI shows the student. */
  output: string;
  /** The check cell's own `_passed` variable, read directly out of the
   * executed namespace — never parsed from printed text, since check cells
   * no longer print a literal "PASS"/"FAIL" string (they print the actual
   * return value instead, StrataScratch-style). `null` when the source
   * didn't run a check cell (or raised before setting it) at all. */
  passed: boolean | null;
}

/** Run `source` (already prefixed with `import numpy as np`) in the exercise's
 * namespace and return what it printed plus its `_passed` status, if any. */
export async function runInExercise(exerciseId: string, source: string): Promise<ExecutionResult> {
  const pyodide = await getPyodide();
  const ns = getNamespace(pyodide, exerciseId);
  pyodide.globals.set("__ns", ns);
  pyodide.globals.set("__user_code", source);
  const resultJson = await pyodide.runPythonAsync(`
import io, contextlib, json
_buf = io.StringIO()
try:
    with contextlib.redirect_stdout(_buf):
        exec(__user_code, __ns)
except Exception as e:
    _buf.write(f"\\n⚠️ Error: {type(e).__name__}: {e}")
_passed_value = __ns.get("_passed", None)
json.dumps({"output": _buf.getvalue(), "passed": _passed_value if isinstance(_passed_value, bool) else None})
`);
  return JSON.parse(resultJson as string) as ExecutionResult;
}

/** Drop an exercise's namespace — used by the Reset button so a fresh run
 * doesn't see leftover state from a previous (possibly broken) attempt. */
export async function resetExercise(exerciseId: string) {
  namespaces.delete(exerciseId);
}
