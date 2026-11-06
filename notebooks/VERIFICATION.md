# Workbench 01 verification

6 November 2026 UTC. Private draft; AI-assisted implementation and separate AI-assisted review. No independent human validation is claimed.

## Verified locally

| Check | Result and scope |
| --- | --- |
| Notebook format | Pass against the official Jupyter nbformat 4.5 JSON schema (`jupyter/nbformat`, schema blob `670bbd35f343f0d1324b8e6056ba42420f7ec6aa`) using the already available JSON Schema validator. No package installed. |
| Fresh-process execution | All 18 code cells completed, in order, from a fresh namespace. The runner blocked socket creation, subprocess launch and file mutation during cell execution. Two repeated runs reproduced the exact saved notebook bytes. |
| Saved notebook SHA-256 | `cdc32d305eab86092edab4fdc4139ca4bb72a9d6bb5d42ad4c5668410eb22a38` |
| New workbench regressions | 39 passing test methods: selection/reset/invalid inputs, counterexample abstention, source hashes, missing/changed inputs, ambiguous ZIP members, JSON duplicates, unsafe paths, summary/raw mismatch, event/effect identity, barrier consistency, copy isolation, excerpts, HTML escaping, SVG structure and dated status overlay. |
| Existing artifact-only checker | 115 project test methods and 26 separately authored regression tests passed on a fresh replay of the unchanged package. These overlap in behavior and are not independent research observations. |
| Input integrity | All 76 pinned input files and all ten original source snapshot hashes match; twelve exact saved raw JSON records reconcile with the selected fields of the retained summary. |
| Visual review | All four saved SVG diagrams rendered locally with installed librsvg and their actual pixels inspected: workflow, S2, S4 and S5. Clear hierarchy, readable labels, no clipped/overlapping content; full text fallbacks and unique SVG accessibility labels checked. HTML tables checked structurally and escaped for source text. |
| Links | All relative notebook links resolve to retained or added repository files. Historical source links use the verified baseline commit below. |
| Preservation | All 677 baseline Git blobs were materialized and verified. Among original files, only root `README.md` navigation and root `SHA256SUMS` are intentionally changed. The other 675 original blobs, including archives, historical results, glossary, registry, source manifests and checker package, remain byte-identical. |

Baseline commit: `6a2d6b19e18df28e2a8e69ee45830a5f9b94f26c`. Root `SHA256SUMS` covers the final candidate files, excluding itself. The unchanged checker's own checksum manifest and reviewed-code checksum manifest also pass.

## Verification limits

- **No actual Jupyter-kernel run was performed.** `nbformat`, `nbclient`, `ipykernel` and `jupyter_client` were unavailable. Rather than install packages or start sockets, the explicit fresh-process runner executed the notebook's Python cells and captured their real rich/text outputs. It is not presented as nbclient, a clean Jupyter kernel, or a hostile-code sandbox.
- **GitHub's rendered notebook UI was not exercised.** The notebook conforms to the official format, has saved HTML/SVG/plain-text outputs, and local diagram rendering passed. These checks do not establish identical styling on every GitHub, Jupyter or mobile client.
- Historical experiment code, framework Workers, bridges and socket-based qualification were not run. The historical raw SQLite stores and full historical grading logic were not independently regraded. This notebook checks only the selected saved JSON facts it uses.
- Tests and visual/source review were AI-assisted. A separate reviewer does not imply independent human validation, statistical reliability or measured reviewer benefit.
- No dependency was installed, no model/API or Jev call was made, no live MCP research tool was used, no historical archive was altered, and no previously denied operation was retried.

## Reproduce the relevant checks

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s notebooks/tests -v
sha256sum -c SHA256SUMS
```

From `checkers/temporal-artifact-v0.1`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python review/test_independent_review.py
sha256sum -c SHA256SUMS
sha256sum -c review/REVIEWED_CODE_SHA256SUMS
```

No schema download or optional renderer is needed for the standard-library execution and regression commands above. Do not interpret checker process exit 0 as native qualification or a scientific pass.

## Review changes resolved

The separate review led to a dated Nov 5 prototype overlay over the Nov 4 registry; no-fence N/A displays instead of conditional zero counts; validation of plotted barrier fields and effect/event identity; deep copies for inspection APIs; exact wording for free-text locator checks and selected consistency checks; unique SVG accessibility labels; explicit default-S2 narrative; and a shorter main reading path with full source tables moved to the appendix.

The course adaptation and team-use guide distinguish working functions from proposed capabilities. Mark leads, alfred coordinates, SORA/MIRA/TRACE are AI-assisted responsibilities assigned as needed, and future roles remain unassigned. Live model/provider/Jev integrations remain deferred.
