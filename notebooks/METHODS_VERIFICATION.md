# Methods chapter verification · 7 November 2026

Baseline main: `9ebf2730613b50f09af4cc8811ed65c9588e5360`. The new chapter is a read-only explanation and archive view, not a reproduction run.

## Scope

Notebook 03 contains 16 cells, five executable. It distinguishes earlier pending protocol wording from the v02 source freeze, post-collection command manifest, measured records and later reviews. It displays actual frozen-file digests, reported commands/environment, selected case members and the original saved checker verdict. It exposes the correction log unchanged and explains future reproduction requirements without providing executable study-running cells.

The source archive is pinned to SHA-256 `adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c`. The reader verifies all twelve frozen-file digests and the manifest's freeze/runner/checker bindings. It reads ZIP members in memory, opens no SQLite connection and never imports or runs archived source. The historical checker verdict is explicitly a stored report, not a new artifact-check result.

## Checks

Seven new tests cover freeze and manifest binding, all twelve case inventories, four historical verdict categories, exact excerpts and bad selectors, changed-archive rejection, absence of archived-code execution calls, and notebook links/outputs/limitations. Existing notebook tests remain in the suite. Final totals and independent review are recorded with the draft PR.

The five code cells pass the existing restricted fresh-process runner with network, subprocess and file mutation blocked during cell execution. This is not a Jupyter-kernel run. Source integrity checks do not establish independent execution attestation, exact historical timing, authenticated provenance or claim correctness.

## Limits and preservation

No source record, ZIP, workbook, original result or study implementation was changed. No installation, workflow, Temporal socket attempt, model call, publication or human evaluation occurred. Prior same-host reproduction and archived mutation tests are described with their original scopes; none were rerun here. Actual GitHub/Jupyter display remains unverified; GitHub shows saved outputs and Jupyter reruns apply selectors.

AI assisted preparation and testing. Separate AI-assisted review, when recorded, is not independent human validation. The archive, historical absolute paths and private locators remain within the private research record.

```sh
PYTHONDONTWRITEBYTECODE=1 python notebooks/tools/run_notebook.py notebooks/03_methods_and_reproduction.ipynb
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s notebooks/tests -v
sha256sum -c SHA256SUMS
```
