# Reproduction and interpretation

The recorded environment is CPython 3.12 on Linux x86_64. Exact package versions are in `measured01/RUN_MANIFEST.json`; historical dependency locks are in `frozen_candidate_v02/`. A compatible isolated environment with those packages is required. No provider credentials or model API are used. The scripted workflow disables tracing.

Inspect results without execution:

- `measured01/SUMMARY.json`: case-by-case classification.
- `measured01/checker.json`: independent checker results.
- `INDEPENDENT_REVIEW.md`: qualification review.
- `CORRECTIONS.md`: instrument defects and fixes.
- `measured01/*/S*/sink.sqlite`: authoritative local sink tables.
- Framework cases also retain worker and checkpoint records.

Verify saved cases using Python standard library only:

```sh
python frozen_candidate_v02/independent_checker.py measured01/direct/S*/record.json measured01/framework/S*/record.json
```

To reproduce the measured schedule with a compatible framework environment, choose two new output directories; existing directories are refused:

```sh
python frozen_candidate_v02/qualify_direct.py reproduced/direct direct --measured
python frozen_candidate_v02/qualify_direct.py reproduced/framework framework --measured
```

Create `reproduced` first. Invocation creates direct/framework child directories itself. Use qualification labels for instrument development; the `--measured` flag records collection kind and changes no execution logic. A fresh run is new local execution evidence and requires the operator's authorization.

The independent checker reads sink databases without writing. It does not rerun the workflow. Checkpoint-identity inspection is additionally documented by the reviewer.

The six schedules are deliberately controlled. Their timing does not estimate deployment delays or exposure probability. The caller's restricted observations differ from the evaluator's privileged access to sink and checkpoint databases. The same trusted host and controller operate all components; no hostile-process isolation or remote trust boundary is established.

The source freeze and command manifest support traceability. The command manifest was written after execution from the exact shell invocation and same-interpreter runtime metadata; it is not an independent execution attestation.
