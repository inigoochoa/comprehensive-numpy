# Comprehensive NumPy — website

An Astro site that turns the course notebooks (in the repo root) into a
StrataScratch-style interactive course: read a lesson, run real NumPy code
in the browser (via [Pyodide](https://pyodide.org)), and get instant
pass/fail feedback — no backend, no accounts, no installs for visitors.

## How it's built

```
repo root
├── module_1_fundamentals.ipynb ... module_6_performance_projects.ipynb   ← source of truth
├── scripts/convert_notebooks.py                                          ← notebook → website converter
└── web/
    ├── src/content/lessons/module-N/*.mdx   ← generated lesson pages (do not hand-edit)
    ├── src/data/exercises.json              ← generated exercise data (do not hand-edit)
    ├── src/data/toc.json                    ← generated sidebar table of contents
    ├── src/components/Exercise.tsx          ← the interactive, Pyodide-powered exercise widget
    ├── src/lib/pyodide.ts                   ← loads Pyodide once, caches it on `window`
    ├── src/lib/progress.ts                  ← localStorage-only progress tracking
    └── src/pages/[...slug].astro            ← one route per generated lesson/overview page
```

**The notebooks are still the single source of truth.** To change lesson
content: edit `build_module_N.py` at the repo root, regenerate that
notebook, then re-run the converter:

```bash
cd ..                                  # repo root
python build_module_3.py               # regenerate the .ipynb
python validate_notebook.py module_3_operations_broadcasting.ipynb
python scripts/convert_notebooks.py    # regenerate web/src/content + web/src/data
```

## Local development

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # static output in dist/
npm run preview   # serve the production build locally
```

## Before you publish

1. **Colab links & GitHub button.** Every lesson's "Open in Colab" link and
   the landing page's "View on GitHub" button currently point at the
   placeholder `YOUR_GH_USERNAME/comprehensive-numpy`. Once this repo is
   pushed, either:
   - find-and-replace `YOUR_GH_USERNAME/comprehensive-numpy` across
     `src/pages/index.astro` and re-run `python scripts/convert_notebooks.py`
     (it writes the same placeholder into every lesson's frontmatter — edit
     `COLAB_REPO_PLACEHOLDER` in `scripts/convert_notebooks.py` first so it
     sticks across future regenerations), **or**
   - set it once in `scripts/convert_notebooks.py`'s `COLAB_REPO_PLACEHOLDER`
     constant and regenerate.
2. **Analytics (optional).** No analytics are enabled by default. If you
   want privacy-friendly pageview analytics, self-host
   [Umami](https://umami.is) (free, open-source) and drop its `<script>`
   tag into `src/layouts/BaseLayout.astro`'s `<head>`, where a comment
   marks the spot.
3. **`npm audit`.** This project currently shows some advisories against
   the installed Astro 5.18.2 (mostly dev-server/build-time issues — XSS in
   `define:vars`/spread-prop edge cases, an esbuild dev-server file-read
   bug, libvips CVEs in `sharp`'s image optimizer). None of them are
   runtime risks for site *visitors* once built to static HTML, but they do
   matter for whoever runs `npm run dev` / `npm run build`. The patched
   Astro release needs Node `>=22.23.4`; this project was built against
   Node 22.15.1, which is why it's pinned to Astro 5.18.2 instead. Once you
   upgrade Node, run `npm audit fix --force` to pick up the patched
   version (verify the build still passes afterward — it's a major bump).

## Deploying

Any static host works (the site is `output: "static"`). Point Vercel or
Netlify at this `web/` directory as the project root, with:

- Build command: `npm run build`
- Output directory: `dist`

No environment variables or server runtime required — Pyodide, the code
editor, and progress tracking are all client-side.
