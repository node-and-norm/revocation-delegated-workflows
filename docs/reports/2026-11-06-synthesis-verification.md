# Synthesis and reader route verification

6 November 2026 · Local review candidate only

## Scope

Adds a dated current-study synthesis and an eight-cell Markdown-only reader notebook. Root and notebook README navigation link to those additions. The report is the current canonical narrative for this candidate; the 00 notebook is a dated summary and reading route. It is not an automatically synchronized duplicate report. Update their shared factual assertions together when the account changes.

The source baseline is draft PR #3, commit `20e782df7c32e05821b1fbad92d521fd45e4509d`, verified open and draft through GitHub metadata on 6 November. No remote write or merge occurred.

## Checks performed

- Parsed the new notebook as nbformat 4.5 JSON with eight unique Markdown cells and no code cells. No kernel is required by the reader route. This structural check is not an official schema validation or a renderer test.
- Checked all relative paths in the new report and notebook, root README and notebook README against the candidate tree. Anchors and external-link destinations were not revalidated in this pass.
- Checked the twelve-case count and twelve checker passes against the preserved measured summary; read the study, later-stages and existing verification records for scope and status reconciliation.
- Re-ran all 39 existing workbench regression methods: PASS.
- Re-ran the original 18 code cells through the existing restricted fresh-process sequential runner: PASS. Expected output SHA-256 remained `cdc32d305eab86092edab4fdc4139ca4bb72a9d6bb5d42ad4c5668410eb22a38`. This is not an actual Jupyter-kernel run.
- Verified every pre-existing file remains byte-identical except root README, notebook README and the regenerated root checksum manifest. No original record, archive, code, test, status overlay or notebook 01 changed.
- Regenerated and checked the root SHA256SUMS manifest for the final candidate. Checksums establish byte integrity, not correctness or authenticity.

## Limits

No new scientific observations were generated. The historical experiment, native Temporal bridge, worker lifecycle and socket operations were not run. No model/provider calls, recruitment, package installation or publication occurred. The existing 115 checker and 26 independent-regression counts are historical reported checks, not rerun in this documentation-only change.

The new route uses ordinary Markdown with short sections and small tables, avoiding custom styles, widgets or network assets. Its actual rendering in GitHub and Jupyter was not tested. The 01 notebook's existing rendering/kernel limits remain open. Preparation and checks are AI-assisted and do not establish independent human validation or reader benefit.

## Review refinements

The reader route distinguishes the draft workbench from the merged artifact checker and names Temporal and reviewer feasibility as optional parallel branches. The synthesis states the single-outstanding-request and fixture-correlation limits. Notebook navigation now starts with 00, then explores 01. Relative links, preservation checks, the 39 workbench regressions and the unchanged 18-cell output were rechecked after these edits.
