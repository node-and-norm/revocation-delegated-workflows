# Temporal artifact checker

**Status: artifact-only synthetic checker under development, not a qualified native instrument.** This project implements parts of proposal v0.3 against the explicitly versioned `synthetic-artifact-0.1` schema. A synthetic test pass is not native Temporal qualification, experimental measurement, or a production readiness claim.

The checker reads saved local files. It does not start Temporal, a Worker, a gateway, a bridge or controller, make socket connections, retry denied operations, or edit historical archives. Synthetic fixtures and newly generated reports are separate from historical evidence.

## Run without installation

Python 3.10 or newer is required. Runtime and tests use the standard library; no third-party runtime dependencies are needed. From this project directory:

```sh
PYTHONPATH=src python -m temporal_checker /path/to/saved/case
PYTHONPATH=src python -m temporal_checker /path/to/saved/case --output reports/case-report.json
PYTHONPATH=src python -m unittest discover -s tests -v
```

The CLI prints deterministic, sorted JSON. `--output` also writes that same report to a **new** file outside the input case directory. Its parent directory must exist. Existing files, output symlinks and output paths resolving inside the case directory are rejected. This prevents report generation from overwriting evidence. Use a new report filename for another run. No installation is needed; optional packaging metadata uses setuptools as its build backend.

Exit status:

- **0:** report generation succeeded, including reports with unsatisfied, unobserved or not-applicable requirements.
- **2:** argument, input-path, report-generation or output-write error. Details go to stderr. Artifact defects that the checker can represent appear in the JSON report instead of changing exit status.

**Exit 0 is not a scientific pass.** Inspect requirement statuses and reasons, phase-specific results, availability, caller scoring, and limitations. Native qualification remains false for synthetic evidence.

## Inputs and outputs

A case directory contains a registry and its declared inputs using `synthetic-artifact-0.1`. The loader checks closed schemas, registered byte lengths and SHA256 hashes, paths, identities and references. Hashes bind bytes; they do not authenticate producers. The supported format is defined by `src/temporal_checker/schema.py`, `artifacts.py` and the synthetic fixtures. This is not an adapter for arbitrary historical or production Temporal exports.

The report keeps artifact integrity, setup/schedule conformance, phase-specific native observations, sink accounting, capture sufficiency, caller support, cleanup and analysis eligibility separate. Phase P1 cannot use P2/P3 evidence; P2 may use permitted earlier records. Positive sink facts are not replaced by a favorable overall label, and unexpected outcomes are not automatically excluded.

Caller scoring uses ten fields for M1–M4 at each of P1 and P2, and seven non-lifecycle fields for K1/K2 at P1: **94 planned field opportunities per view**, not 94 independent observations. It reports six disjoint categories, determinate-claim support rate, conclusive coverage, required-output completion and missingness. Always-unresolved output earns zero conclusive coverage when references are decidable. Zero determinate claims yields an undefined (`null`) support rate. Missing input is not a caller omission. A/B pairing is not additional experimental replication.

## Python API

```python
from temporal_checker.engine import check_bundle
report = check_bundle("/path/to/saved/case")
```

The scoring-only API is `score_assertions(required_fields, reference, claims, context)` in `temporal_checker.scoring`. Production integration uses `context["strict_refs"] = True` with structured source references. The reference answer must be supported entirely by permitted evidence, not privileged truth. All extra cited references must also be permitted. The exact native terminal tuple remains report data; `exact_terminal_status` is only a contract discriminator.

See [limitations](docs/LIMITATIONS.md) before interpreting any result. The proposal and preserved source contracts are in `provenance/`; implementation does not retroactively change those records.

## Delivered validation package

- [Implementation report](docs/IMPLEMENTATION_REPORT.md)
- [Independent AI-assisted review](review/FINAL_REVIEW.md)
- [Test traceability and remaining coverage](docs/TEST_TRACEABILITY.md)
- [Synthetic schema and exact allowlist](docs/SCHEMA_AND_ALLOWLIST.md)
- `fixtures/catalog.json`: ten saved synthetic configurations and explicit expected outputs.
- `reports/unit_tests_final.txt`: 115 passing project tests.
- `review/final_test_results.txt`: 26 passing independent regressions.

Try a delivered fixture with `PYTHONPATH=src python -m temporal_checker fixtures/case_001`. To rerun the separately authored review harness, use `PYTHONPATH=src python review/test_independent_review.py`.
