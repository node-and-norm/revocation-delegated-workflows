# Bounded integration-conformance pilot v0.3

This is an independent synthetic adaptation of the official LangChain supervisor/subagent tutorial, not an upstream default, security defect, deployed email system, autonomous model study or novel revocation mechanism. No model API calls or external email/calendar operations occur. All effects are inert rows in a local SQLite sink.

## Reproduce

The compact repository view omits raw evidence. Before running its tests, extract `archives/revocation_integration_pilot_v03_20261103.zip` into the repository root. Alternatively, extract that archive into an empty directory and use it as a standalone package. It contains the raw qualification evidence required by the tests and the byte-identical historical gateway dependency. Extraction does not overwrite the repository root README; packaging guidance is named `PILOT_PACKAGE_README.md`.

Use CPython 3.12 on Linux x86_64 (the captured wheel lock is platform-specific). From `integration/v0.3` inside either extracted layout:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --index-url https://pypi.org/simple --require-hashes -r requirements.hashed.txt
.venv/bin/python -m pip check
.venv/bin/python -c 'import json; from workflow import run_baseline; print(json.dumps(run_baseline()))'
.venv/bin/python -m unittest -v test_instrument
.venv/bin/python runner.py --qualification --output evidence/restart_reproduction
.venv/bin/python runner.py --output evidence/measured_reproduction
.venv/bin/python checker.py evidence/measured_reproduction
```

Output directories must not already exist. The historical gateway import requires this directory to remain at `integration/v0.3` beneath the repository containing `qualification/v0.2/gateway.py`. The venv and downloaded wheel cache are not part of the compact source/evidence archive. For offline installation using the optional separately retained wheelhouse, add `--no-index --find-links wheelhouse` instead of `--index-url`.

## What is integrated

The actual installed `create_agent` machinery executes supervisor -> manage_email tool -> email create_agent -> HumanInTheLoopMiddleware -> send_email synthetic sink. The tutorial's calendar branch is omitted. `invoke` replaces the presentation-oriented event-stream loop; actual native interrupt objects and Command resume maps are retained. Prompts are synthetic and exact-result-oriented. Models are our `BaseChatModel` subclasses whose outputs are pure functions of persisted message history, not upstream mutable-index fake models. They never instantiate a provider client. LangSmith tracing is explicitly disabled.

Baseline uses the tutorial's top-level InMemorySaver, no authority adapter, and one harmless recorder. The durable adaptation switches only top-level storage to SqliteSaver. A spawned worker exits after the interrupt; another freshly spawned worker rebuilds agent/model objects and restores the same thread/checkpoint and pending interrupt before approval. The subagent's pending tool state is restored through native nested execution. This is graceful process replacement at a committed interrupt, not arbitrary crash recovery.

The unchanged v0.2 gateway is a separate live process. Its pipe endpoints bind callers to parentP/childC/controller. Trusted setup delegates parent-0 to child-1 and prepares ticket-1. Trusted constants rebind identity/grant/ticket/operation after restart, while checkpoint arguments are checked against the immutable synthetic action. This scopes the test to the adapter, not arbitrary grant transport or hostile worker isolation. Authority lives outside the workflow checkpoint database. The gateway's unconditional CREATE bootstrap is not restart-qualified and it never restarts within a run.

Direct reference and framework paths use the identical adapter and final commit_fenced gateway policy. An optional historical effect is injected by the controller through the same child endpoint before revocation; it is not counted as native framework execution. On resume, revoked authority is checked before duplicate lookup, preserving historical semantics. Local atomic sink commit and revocation share one authoritative order; remote admission/receiver contracts are out of scope.

## Evidence

- `PROTOCOL.md`, `evidence/protocol_freeze.json`, and `evidence/precollection_source_hashes.json`: before-collection protocol and source snapshot.
- `sources/`: exact Git-blob-verified pinned tutorial and reference code. Upstream test helper is read-only reference, not executed.
- `requirements.lock`, `requirements.hashed.txt`, `evidence/environment.json`, `evidence/wheels.json`, `licenses/`: exact environment, official PyPI wheel hashes and bundled license texts. `pip_check.log` confirms dependency consistency. `source_comparison.json` compares installed HITL bytes to pinned source.
- `evidence/baseline_attempt*`: baseline qualification, including failed serialization attempt and correction.
- `evidence/restart_qualification01`: native durable restart qualification, separate from measured collection.
- `evidence/instrument_tests*`, `reviewer_counterexamples_initial.json`, `reviewer_tests_precollection.log`: complete qualification/correction trail.
- `evidence/measured01`: eight fixed runs, each with raw JSON record, read-only-observed sink database, and (framework) durable checkpoint database and worker records.
- `evidence/measured01_summary.json`: independent checker results, with operation outcome separate from attempt disposition.
- `evidence/historical_preservation.json`: every preexisting snapshot file remained byte-identical.

## Corrections preserved

1. Baseline attempt 01 executed but JSON serialization could not encode native Interrupt dataclasses. Added dataclass serialization; attempt 02 captures the successful baseline. This was instrumentation, not a measured revocation failure.
2. Review required failure evidence persisted before assertions, read-only SQLite observation, explicit controller rebinding disclosure, and no-fence prior/live classification as authorized_effect.
3. Reviewer demonstrated two initial checker false passes: malformed delegation scope and malformed admission grant. The checker now compares the complete independent expected event transcript, terminal results, controller evidence and sink effect rows. Original counterexamples and hashes remain preserved.
4. The post-fence mutation fixture initially omitted a newly required controller revocation field, producing unresolved instead of post_fence_effect. Corrected the fabricated negative fixture; failed test log retained. This was not a measured run.
5. Added required nonempty checkpoint/interrupt provenance, exact worker binding and tool-request agreement tests before collection.

## Limits

One deterministic operation and eight fixed schedules establish bounded conformance only. No stochastic generalization, adversarial model behavior, user-data access, live mail, remote-service races, gateway restart, machine crash, network partition, permission-system completeness or novelty is claimed. The independent reviewer is another AI worker, not human validation. The synthetic parent/controller and local process environment are trusted. Missing evidence is unresolved rather than safe. Existing related work already covers recovery/effect semantics; this pilot supplies an explicit integration feasibility artifact under a stronger local atomic sink contract, not outperformance evidence.
