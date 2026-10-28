// Student progress lives only in the browser's localStorage — no accounts, no
// backend, consistent with this being a free static site. It's lost if the
// student switches browser/device, which is an accepted tradeoff for that.
const PROGRESS_KEY = "numpy-course:progress:v1";
const DRAFT_KEY_PREFIX = "numpy-course:draft:";
export const PROGRESS_EVENT = "numpy-course:progress-changed";

interface ProgressState {
  completedExercises: string[];
}

function readState(): ProgressState {
  try {
    const raw = localStorage.getItem(PROGRESS_KEY);
    if (!raw) return { completedExercises: [] };
    const parsed = JSON.parse(raw);
    return { completedExercises: Array.isArray(parsed.completedExercises) ? parsed.completedExercises : [] };
  } catch {
    return { completedExercises: [] };
  }
}

function writeState(state: ProgressState) {
  try {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(state));
  } catch {
    // localStorage unavailable (private mode, blocked, etc.) — fail silently.
  }
}

export function isExerciseDone(exerciseId: string): boolean {
  return readState().completedExercises.includes(exerciseId);
}

export function markExerciseDone(exerciseId: string): void {
  const state = readState();
  if (!state.completedExercises.includes(exerciseId)) {
    state.completedExercises.push(exerciseId);
    writeState(state);
  }
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(PROGRESS_EVENT));
  }
}

export function isLessonDone(exerciseIds: string[]): boolean {
  if (exerciseIds.length === 0) return false;
  const state = readState();
  return exerciseIds.every((id) => state.completedExercises.includes(id));
}

export function getCompletedCount(): number {
  return readState().completedExercises.length;
}

export function saveDraft(exerciseId: string, code: string): void {
  try {
    localStorage.setItem(DRAFT_KEY_PREFIX + exerciseId, code);
  } catch {
    // ignore
  }
}

export function loadDraft(exerciseId: string): string | null {
  try {
    return localStorage.getItem(DRAFT_KEY_PREFIX + exerciseId);
  } catch {
    return null;
  }
}
