# Guided notebooks

**Begin with [the complete study report](../RESEARCH_STUDY.ipynb)**: question, method, findings, limitations, roadmap and completion gates in one readable notebook. Use 01 below for deeper interactive evidence exploration; 00 is an optional short navigation route.

# Revocation evidence workbench

Optional short route: [00 · Start here](00_start_here.ipynb), a Markdown-only reading route into the [dated synthesis](../docs/reports/2026-11-06-current-study-synthesis.md) and executable workbench below. It has no code cells and requires no kernel.

Then explore [01 · When is withdrawal actually established?](01_revocation_evidence_workbench.ipynb).

This private, source-linked notebook is an executable review surface, not a live research agent. It loads the existing glossary, registry and source manifest; verifies pinned input bytes; reads twelve saved historical JSON records; reconciles selected fields; supports case and claim inspection; tests three explicit overclaims; and generates a bounded brief and audit. It also calls the existing artifact-only checker on one separate, clearly synthetic bundle.

## Read or run

**GitHub:** open the notebook. The committed outputs are a saved preview of the default selection, not live controls. Navigation, tables and diagrams do not require JavaScript or a widget server. Code cells expose the selectors and exact computation behind the output.

**Existing Jupyter environment:** use Python 3.10 or later, open the notebook from this complete repository, then choose Restart Kernel and Run All. No additional packages, model keys or network are needed by the notebook. The notebook itself is read-only, including bytecode suppression. Do not run an install command just to read it.

**Plain Python verification, no installation:** from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s notebooks/tests -v
```

The first command runs every code cell in a fresh sequential Python process, captures the actual explicit `show()`/`print()` output, and rejects socket creation, subprocesses and file mutation during cell execution. This is a small verification runner, **not a Jupyter kernel or nbclient**. That distinction is recorded in notebook metadata. The default command changes no files. To intentionally refresh the derived notebook's saved outputs after review, add `--write`.

This runner is a regression guard for this trusted notebook, not a general hostile-code sandbox. Ordinary Jupyter execution does not install the runner's audit guard. The implemented notebook contains no network, process-launch or evidence-write operation.

## Controls and boundaries

- `Scope(paths=..., schedules=...)` selects a matrix slice. `Scope()` resets. Unknown, duplicate or empty selections fail visibly. All twelve raw/summary records are reconciled before filtering.
- `CASE_PATH` and `CASE_SCHEDULE` independently select a case diagram and source trace. S4/S5 contrast uses that path and fixed schedules, regardless of the matrix filter.
- `CLAIM_QUERY` is a case-insensitive literal registry filter. An empty string resets to all ten records; no hits imply no conclusion.
- `SOURCE_KEY`, `START_LINE` and `LINE_COUNT` select a verbatim excerpt. Free-text source section locators are preserved but not parsed as machine-verifiable addresses.
- The full selected record is in `selected_case`; original registry/glossary objects, source bytes, input receipts, derived rows, audit and the synthetic report remain accessible. Display filters are not access controls or blinded packets.

There are no interactive controls on GitHub. Changing a Python control locally requires rerunning it and downstream cells. No callback, background service or persistent state is claimed.

## Files and evidence classes

| File | Purpose |
| --- | --- |
| `01_revocation_evidence_workbench.ipynb` | Main review surface, saved outputs and explicit code |
| `workbench/core.py` | Bounded input gate, reconciliation, selection, queries and brief |
| `workbench/presentation.py` | HTML/SVG views with text fallbacks, no external assets |
| `workbench/input_manifest.json` | All 76 input paths and full SHA-256 values |
| `workbench/status_overlay.json` | Dated interpretation of Nov 4 registry vs Nov 5 prototype; originals unchanged |
| `tests/test_workbench.py` | Selection, input, consistency, rendering and abstention regressions |
| `tools/run_notebook.py` | Read-only, fresh-process execution and optional saved-output refresh |
| `VERIFICATION.md` | Exact checks performed and remaining verification limits |

Source hashes bind bytes, not authorship, authenticity, execution or scientific truth. Reconciliation checks the saved JSON fields displayed here and their consistency with the summary. It does not rerun the historical experiment, independently regrade the full instrument or reopen historical SQLite databases. The separate synthetic checker example does not establish native Temporal qualification.

The original registry is preserved as of 2026-11-04. Its outstanding-checker statement is paired with the later 2026-11-05 artifact-only prototype record; the native qualification remains blocked. No original source, archive, empirical result, registry or glossary is rewritten.

## Course and team adaptation

The [LangChain full-agent notebook](https://github.com/langchain-ai/deep_research_from_scratch/blob/main/notebooks/5_full_agent.ipynb), [architecture module](https://github.com/langchain-ai/deep_research_from_scratch/blob/main/src/deep_research_from_scratch/research_agent_full.py) and user-supplied course overview slides informed the visible progression, not any revocation finding. The notebook maps course stages to working local counterparts and labels missing live capabilities. No course code or artwork is copied into this repository.

Mark leads; alfred coordinates. SORA, MIRA and TRACE are AI-assisted review responsibilities assigned as needed, not connected or persistently running notebook agents. Future roles remain unassigned. Future model/provider or Jev routing would require separate approved implementation and evaluation, including abstention and policy enforcement outside model confidence. No provider, model, Jev or MCP call is made here.

This is a private draft for review. It does not authorize a native experiment, retry a denied operation, publish the study, merge a PR or deploy a system.


## Guided study report · 7 November edition

Start with [RESEARCH_STUDY.ipynb](../RESEARCH_STUDY.ipynb) at the repository root for the complete reader-facing narrative and saved evidence views. Then use 01 for deeper exploration. Raw records and implementation remain in their native formats.

Verify without a Jupyter server or experiment:

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py RESEARCH_STUDY.ipynb
```

This fresh-process verification is not a Jupyter-kernel run. See [report verification](STUDY_REPORT_VERIFICATION.md).

## 02 · Traceability and AI disclosure

[Open the workbook explorer](02_traceability_and_disclosure.ipynb). It reads all six sheets and seven named tables directly from the pinned v0.11 XLSX using Python standard-library XML/ZIP support. It does not edit the workbook or verify current publisher policies. GitHub shows saved output; selectors work when rerun in Jupyter.

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py notebooks/02_traceability_and_disclosure.ipynb
```

[Verification and limits](TRACEABILITY_VERIFICATION.md).

## 03 · Methods and reproduction

[Read the methods chapter](03_methods_and_reproduction.ipynb). Five read-only code cells inspect the preserved archive, source freeze, historical run manifest and selected case. Study-running commands remain external reference instructions, not executable notebook cells.

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py notebooks/03_methods_and_reproduction.ipynb
```

[Verification and limits](METHODS_VERIFICATION.md).

## 04 · Exact experimental inputs, outputs and code

[Open the source trace reader](04_exact_scripted_inputs_outputs.ipynb). Select any available v0.3 framework case/phase and inspect exact role/input/output JSON spans with byte provenance. An appendix inventories early-stage archives and displays source code without executing it. It does not reconstruct missing research conversations.

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py notebooks/04_exact_scripted_inputs_outputs.ipynb
```

[Verification and limits](PROMPT_TRACES_VERIFICATION.md).
