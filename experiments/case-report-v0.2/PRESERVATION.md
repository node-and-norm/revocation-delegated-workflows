# Preservation record · 18 November 2026

This directory preserves the saved case-report candidate against specification commit `6eaf9b7e9ddb67f0e2fc25849ca031373805db57`, its actual implementation/review assignments and returns, and the separately approved 14 November check record. It remains unmerged experimental work, not a qualified instrument or release.

## Status and reading route

1. Read the [specification notebook](../../notebooks/spec_01_case_report_contract.ipynb), including its dated preservation update.
2. Read [the saved run result](approved_checks_001/RESULT.md) and [captured output](approved_checks_001/output.txt): one run, 19 test methods, exit 0, Python 3.12.14.
3. Inspect `case_report.py`, `test_case_report.py`, `REQUIREMENT_MAP.md`, and the assignment, correction and review records.

Earlier “not executed”, “not dispatched” and “prospective” wording in preserved sources and preparation records describes their authorship stage. The dated run record is the subsequent evidence. Source docstrings and extractor version were deliberately not modernized: the exact executed source bytes must remain identifiable. This is not 19 new empirical cases, independent human validation, or a CI pass.

## Custody and redaction

Original local files were left unchanged. Both original checksum manifests were checked successfully during preservation. Python implementation and test bytes are unchanged. The original archive was already preserved under `archives/withdrawal_interface_study_v01_20261103.zip`; it is not duplicated or modified here.

`SOURCE_SHA256SUMS` and `approved_checks_001_SHA256SUMS` remain the original local manifests, not manifests of redacted exports. `EXPORT_SHA256SUMS` identifies every exported file except itself. Redacted records have a visible header; their original hashes remain in the historical manifests. Do not expect original-manifest checks to succeed for redacted copies. Exact original copies remain locally, but local retention is not guaranteed. No full conversation export or unavailable model/runtime metadata is invented.

Redacted files:
- `ASSIGNMENT.txt`
- `CORRECTION_ASSIGNMENT_R1.txt`
- `REVIEW_ASSIGNMENT.txt`
- `approved_checks_001/command.txt`
- `approved_checks_001/input_sha256.txt`

Only workspace/private task locators were replaced. Task-relevant instructions and returned accounts were otherwise preserved, including their historical prohibitions. Redacted command text is a record, not an executable reproduction command. To reproduce later, use a verified repository archive path and obtain separate approval first.

## Limits and next decision

No candidate code, tests, imports, notebook cells, historical workflow, VM action or model-provider call was run for this preservation. Hashing and document serialization are preservation operations, not candidate validation. No generated case reports were saved by the original tests. A8a wrong-original-member extraction coverage, broad adversarial correctness, browser/Jupyter rendering, authenticity of local receipts, native Temporal qualification and human-reader benefit remain unestablished. Further tests and any merge require separate approval.

The repository is private; preservation does not authorize public release or change its access permissions. Historical archives and existing study observations are untouched.
