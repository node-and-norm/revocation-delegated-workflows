# Guided study report verification · 7 November 2026

Private review update based on PR #3 head `81d1f9ad6af04a1ee85e2fdce74fed59f024d4cf`.

## Delivered

- Root `RESEARCH_STUDY.ipynb`: 21 cells, including 7 code cells. The report contains the question, method, saved-case matrix, S4/S5 diagrams, raw source trace, bounded interpretation, next steps, native qualification gaps and completion rules.
- Existing workbench remains the deeper exploratory view. Start-here and README link to the full report, not only the historical Markdown account.
- Shared tables explicitly pair carbon foreground with white/paper background; dark iris accents are restrained. This corrects a source-level contrast risk, not a confirmed failure in GitHub's renderer.
- Original study records, archived artifacts, historical synthesis and verification reports are unchanged. No experimental result or native qualification status changed.

## Checks performed

- All 7 report cells and all 18 workbench code cells completed using `notebooks/tools/run_notebook.py` in fresh sequential Python processes, with network, subprocess and file mutation blocked during cell execution. Saved rich outputs were regenerated from those executions.
- 44 unit tests passed: the existing 39 workbench tests plus 5 report tests covering narrative structure, explicit limitations, relative links, saved outputs and paired table colors.
- Notebook structure validated by the existing runner. Report relative links resolve locally. Table/diagram outputs retain plain-text fallbacks.
- The report reuses the existing source-validated workbench functions; it does not implement a second evidence parser or alter source facts.

## Not established

This is **not a Jupyter-kernel execution**, browser render test, GitHub CI result, human usability evaluation, new experiment, native Temporal qualification or public release. Intended GitHub and Jupyter light/dark display still need actual viewer inspection. Color declarations and saved MIME outputs do not establish how every renderer displays them.

## Recheck

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py RESEARCH_STUDY.ipynb
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py
PYTHONPATH=notebooks PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s notebooks/tests -v
sha256sum -c SHA256SUMS
```

The first two commands check without replacing saved outputs; `--write` updates only derived notebook output. Hash integrity is not authenticity or evidence of correctness. AI assisted this report and verification. Independent review, if performed, should be recorded separately rather than inferred from these tests.
