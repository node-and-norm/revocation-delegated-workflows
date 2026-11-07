# Exact scripted inputs/outputs verification · 7 November 2026

Baseline: PR #5 head `3b12e0700e36c304a4ae5a1ef7276ec18f57bffe`.

## Source and coverage

The v0.3 pilot archive is pinned to SHA-256 `b088613324c731e900e71317be725a8f2a8002d22a29bc40dcc4670ffb68f3c9`. It contains eight worker snapshots: four framework cases, each at pause/resume. They contain sixteen recorded StateScriptModel invocations, each with role/input/output fields. Four direct-reference cases have no framework worker/model snapshots; they are not silently treated as lost model transcripts.

The notebook extracts unchanged source JSON substrings, with member digest, JSON pointer, UTF-8 byte interval and fragment digest. It does not use json.dumps to reconstruct displayed input/output fragments. Escaping and whitespace within the selected JSON span are preserved. These are serialized experiment records, not in-memory objects, provider wire payloads, live-model outputs or a complete collection of research/design conversations.

The source-code appendix verifies four preserved stage archives, inventories actual code/log members, and displays exact source-line bytes from a selected text file. It never imports or executes that code. File counts include copies and tests; they do not count unique programs or prove complete execution history. Historical commands in the request-to-fence run manifest remain explicitly post-collection records, not independent attestation.

## Checks

- Eighteen notebook cells, eight executable, completed with the restricted sequential runner. Saved examples include exact role, complete input array, output, pause/resume outputs, stage inventory and source excerpt.
- Nine new tests cover phase/case coverage, all 48 role/input/output fragments, empty output content plus tool calls, Unicode/escaped pointers, malformed/duplicate-key rejection, absent-record handling, changed-archive rejection, preserved source bytes and notebook links/limits.
- All 68 notebook tests pass locally. All five notebook restricted replays pass (7, 18, 10, 5 and 8 code cells). Independent review is recorded separately in the PR.
- Canonical archives and study records remain unchanged. This reader performs no extraction, database mutation, model call, workflow, email or denied Temporal operation.

## Limits

This is not independent human validation, current publisher-policy verification, a new experiment, public release, GitHub CI result, actual GitHub/Jupyter render inspection or a Jupyter-kernel run. Model call groups are preserved, not promoted into global chronological order. Repeated messages in resumed inputs are not counted as additional earlier calls. Missing fields or snapshots are not invented. Empty stderr is not a success verdict.

The default uses only scripted fixture content, including a reserved example.invalid recipient and non-production authority identifiers. Private source locators stay in the private repository. A public release requires separate review of identifiers, rights, claims and AI disclosure.

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py notebooks/04_exact_scripted_inputs_outputs.ipynb
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s notebooks/tests -v
sha256sum -c SHA256SUMS
```
