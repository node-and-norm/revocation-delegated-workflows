# Artifact-only Temporal checker prototype

5 November 2026 UTC. Private draft for review. This repository update preserves the delivered v0.1 package after its local implementation and separate AI-assisted review. Native Temporal qualification remains blocked.

## Read and reproduce

- [Prototype README](../../../checkers/temporal-artifact-v0.1/README.md): CLI, Python API and interpretation.
- [Implementation report](../../../checkers/temporal-artifact-v0.1/docs/IMPLEMENTATION_REPORT.md), [limitations](../../../checkers/temporal-artifact-v0.1/docs/LIMITATIONS.md), [schema and allowlist](../../../checkers/temporal-artifact-v0.1/docs/SCHEMA_AND_ALLOWLIST.md), and [test traceability](../../../checkers/temporal-artifact-v0.1/docs/TEST_TRACEABILITY.md).
- [Final AI-assisted review](../../../checkers/temporal-artifact-v0.1/review/FINAL_REVIEW.md), [exact reviewed code hashes](../../../checkers/temporal-artifact-v0.1/review/REVIEWED_CODE_SHA256SUMS), and [review verification](../../../checkers/temporal-artifact-v0.1/review/FINAL_REVIEW_VERIFICATION.json).
- [Original delivered archive](../../../archives/Node_and_Norm_Temporal_Artifact_Checker_Prototype_v01_20261105.zip) and [repository import record](IMPORT_RECORD.json).
- Fresh pre-import test replay logs: [115 project tests](project_test_replay.txt) and [26 independent regressions](independent_test_replay.txt).

From `checkers/temporal-artifact-v0.1`, use Python 3.10 or newer:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python review/test_independent_review.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m temporal_checker fixtures/case_001
sha256sum -c SHA256SUMS
sha256sum -c review/REVIEWED_CODE_SHA256SUMS
```

These commands only inspect or construct local artifacts. They do not start Temporal, a Worker, the historical gateway, a bridge, or a network socket. Tests use temporary synthetic fixtures. No package installation is required. Checker exit 0 means a report was generated, not that scientific or native qualification passed.

## What passed and what remains open

The fresh archive replay passed 115 project test methods and 26 separately authored regression tests. The delivered review additionally records repeated deterministic checks and byte preservation across ten synthetic configurations. These checks overlap in behavior and must not be added into independent observations or experimental replication. The A/B views share a reference helper. Their equality is a packaging/scoring check, not evidence of comparative benefit or an independent native baseline.

The measured-plan-shaped fixture subset has 94 planned field opportunities per view, with 89 correct determinate and five justified unresolved fixture outputs. These are synthetic expectations, not measured accuracy estimates. Every supported bundle remains unqualified for native execution.

Production export/adapters, independently persisted runtime phase registries, observed native outcome mappings, calibrated numerical deadlines and full measurement readiness remain open. The saved Q2 database inspection establishes only the saved bytes and counts; it does not upgrade the failed historical control or establish bounded absence of effects.

## Preservation and chronology

All 536 files in the delivered archive are copied byte-for-byte into the prototype directory, retaining its original SHA256SUMS and exact-byte review manifest. The archive itself is also preserved byte-for-byte. The package statements that no repository was changed describe its completed pre-publication implementation/review stage. This import record documents the subsequent draft-PR update without rewriting those historical statements.

The prior design package, source contracts, failed runtime evidence, historical empirical records and prior review files are unchanged. Only the root README navigation and root checksum manifest are updated among the existing files. The earlier design's proposed fixtures and unresolved questions retain their historical status; the synthetic implementation does not retrospectively execute or qualify them.

AI assisted implementation, testing, review and repository preparation. The separately authored review is not independent human validation. This update does not authorize native execution, retry a denied operation, merge the draft, or authorize public release or deployment.
