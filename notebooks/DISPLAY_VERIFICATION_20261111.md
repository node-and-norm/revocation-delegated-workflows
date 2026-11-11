# Revocation report verification — 11 November 2026

Private local verification. No repository edit/push, model call, study experiment, Temporal action, or publication performed.

## Identity
- GitHub notebook viewer observed main at `10e3388720cd5caa0b50326cda73cebfff83ed95`.
- Report blob `920710bab1158c57a8e2d7f4716d6410bd373108` matches local `book_navigation_20261107/RESEARCH_STUDY.ipynb`.
- Imported `core.py`, `presentation.py`, `__init__.py`, and input manifest independently matched connector-returned Git blob IDs from that commit.
- Execution reads pinned saved artifacts, verifies 76 input-file digests and 10 source snapshots, then reconciles 12 records. No native experimental runtime executes.

## Actual GitHub preview
Signed-in GitHub preview opened successfully. Narrative and saved HTML tables render, including 12 saved cases, six effects, six revoked denials, eight fenced cases and zero post-fence effects in those cases.

A real SVG display defect was observed in the six-stage workflow diagram: non-ASCII arrows and bullets appear as literal UTF-8 byte escape strings (`\xe2\x86\x92`, etc.). These strings crowd the cards and hard-stop line. Source SVG has correct Unicode, so this is not evidence corruption. The viewer also exposes an extraneous `b'` text fragment in accessibility output. A source-compatible renderer workaround needs separate verification before claiming repair. All notebook figures and browser themes have not been exhaustively checked.

## Execution
- Read notebook code and imported core/presentation code before running. Code uses local file reads and in-memory ZIP reads; no network requests, process launches or evidence writes.
- Installed standard Jupyter dependencies from package registry into isolated `/tmp` environment; no repository dependency changes.
- Actual nbclient/Jupyter kernel launch attempted: Python 3.12, nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.4.0, jupyter-client 8.10.0, IPython 9.18.1.
- Kernel failed before cells ran: local network-interface discovery returned EPERM; pyzmq aborted with `Operation not permitted (src/ip_resolver.cpp:542)`; nbclient reported `RuntimeError: Kernel died before replying to kernel_info`. Cleanup also raised AssertionError. This is an environment blocker, not a notebook-cell test failure. No success claimed; no restriction bypass attempted.
- Existing guarded fresh-process sequential Python runner: all seven report cells PASS; output SHA-256 `596a7f0b8fb0cc5816c876703c224704c41e9dc27e4e47212e564ae6c3c44705`.
- Existing 70 notebook regression tests PASS.

These are AI-assisted artifact checks, not independent human validation or new scientific evidence. The unverified gate remains an actual Jupyter-kernel Run All in an environment permitting its local messaging transport. Logs: `kernel.log`, `tests.log`; harness: `run_check.py` in this directory.

## Proposed display repair
Serialize SVG MIME outputs as ASCII XML character references. XML parsing confirms identical text and elements; narrative, code-cell sources and non-SVG outputs are unchanged. Regenerated only report/workbench saved outputs. All 72 notebook tests pass, including two new encoding regressions. Actual GitHub branch preview verification remains to be recorded after upload; not yet a main-branch repair.
