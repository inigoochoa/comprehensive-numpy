import { useMemo, useState } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { githubLight } from "@uiw/codemirror-theme-github";
import exercises from "../data/exercises.json";
import { isExerciseDone, loadDraft, markExerciseDone, saveDraft } from "../lib/progress";
import { runInExercise } from "../lib/pyodide";
import { marked } from "marked";

type ExerciseData = {
  localId: string;
  title: string;
  problem: string;
  stub: string;
  check: string;
  hint: string;
  solution: string;
};

const exerciseDb = exercises as Record<string, ExerciseData>;

function toHtml(markdownText: string): string {
  return marked.parse(markdownText, { async: false }) as string;
}

export default function Exercise({ id }: { id: string }) {
  const data = exerciseDb[id];
  const [code, setCode] = useState(() => (data ? loadDraft(id) ?? data.stub : ""));
  const [status, setStatus] = useState<"idle" | "running" | "pass" | "fail">("idle");
  const [output, setOutput] = useState<string | null>(null);
  // Separate from `status` (which just reflects the last Run/Check result):
  // only Check Solution ever sets this, and it's what the "Completed" badge
  // and localStorage persistence track — Run Code never marks progress.
  const [completed, setCompleted] = useState(() => (data ? isExerciseDone(id) : false));

  const problemHtml = useMemo(() => (data ? toHtml(data.problem) : ""), [data]);
  const hintHtml = useMemo(() => (data ? toHtml(data.hint) : ""), [data]);

  if (!data) {
    return (
      <div className="exercise-card exercise-card--error">
        Unknown exercise id: <code>{id}</code>
      </div>
    );
  }

  // Both buttons run the student's code followed by the same check cell —
  // otherwise "Run Code" on a function definition prints nothing at all.
  // The check cell always prints the actual return value (never a literal
  // "PASS"/"FAIL"); correctness comes from the `_passed` variable it sets,
  // read straight out of the Python namespace, not parsed from the text.
  // Only "Check Solution" persists completion to localStorage.
  async function execute(markOnPass: boolean) {
    setStatus("running");
    saveDraft(id, code);
    try {
      const { output: result, passed } = await runInExercise(
        id,
        "import numpy as np\n" + code + "\n" + data.check
      );
      setOutput(result.trim());
      if (passed) {
        setStatus("pass");
        if (markOnPass) {
          markExerciseDone(id);
          setCompleted(true);
        }
      } else {
        setStatus("fail");
      }
    } catch (err) {
      setOutput(String(err));
      setStatus("fail");
    }
  }

  const handleRun = () => execute(false);
  const handleCheck = () => execute(true);

  function handleReset() {
    setCode(data.stub);
    setOutput(null);
    setStatus("idle");
    saveDraft(id, data.stub);
  }

  return (
    <div className="exercise-card" data-exercise-id={id}>
      <div className="exercise-card__header">
        <span className="exercise-card__badge">{data.localId}</span>
        <h4 className="exercise-card__title">{data.title}</h4>
        {completed && <span className="exercise-card__status exercise-card__status--pass">✓ Completed</span>}
      </div>

      <div
        className="exercise-card__problem"
        dangerouslySetInnerHTML={{ __html: problemHtml }}
      />

      <CodeMirror
        value={code}
        height="auto"
        minHeight="120px"
        theme={githubLight}
        extensions={[python()]}
        onChange={(value) => setCode(value)}
        className="exercise-card__editor"
      />

      <div className="exercise-card__actions">
        <button type="button" className="btn btn--ghost" onClick={handleReset} disabled={status === "running"}>
          Reset
        </button>
        <button type="button" className="btn btn--outline" onClick={handleRun} disabled={status === "running"}>
          ▶ Run Code
        </button>
        <button type="button" className="btn btn--primary" onClick={handleCheck} disabled={status === "running"}>
          ✓ Check Solution
        </button>
      </div>

      {output !== null && (
        <div
          className={
            "exercise-card__output " +
            (status === "pass"
              ? "exercise-card__output--pass"
              : status === "fail"
                ? "exercise-card__output--fail"
                : "")
          }
        >
          <pre>{output}</pre>
        </div>
      )}

      <details className="exercise-card__disclosure">
        <summary>💡 Hint</summary>
        <div dangerouslySetInnerHTML={{ __html: hintHtml }} />
      </details>

      <details className="exercise-card__disclosure">
        <summary>✅ Solution</summary>
        <pre className="exercise-card__solution">
          <code>{data.solution}</code>
        </pre>
      </details>
    </div>
  );
}
