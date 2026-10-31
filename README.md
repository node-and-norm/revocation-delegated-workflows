# Revocation in delegated workflows

Private Node & Norm research record for `node-and-norm/revocation-delegated-workflows`.

## Question and status

**Q1 only:** when authority is withdrawn, does the tested delegated workflow prevent a new protected effect from committing after the revocation fence? Evidence veracity (Q2) and oversight scaling (Q3) remain deferred.

The current result is **finite instrument qualification**, not a new research finding or general assurance result. The reviewed v0.2 implementation uses one root, one parent-to-child delegation edge, deterministic workers, a trusted gateway and a separate read-only observer on one host. It compares an intentionally seeded admission-only diagnostic arm with a commit-fenced arm. Revocation and protected effect insertion serialize in the same SQLite transaction domain.

- **18 case-arm fixtures:** nine schedules across two arms; all match declared expectations.
- **19 current unit tests** and **18 preserved legacy tests** pass. Direct invocation repeats the same 19 tests, not a second sample.
- Historical separate AI-assisted review records **349 semantic/database assertions** and **36 real-IPC assertions**. These overlap and are engineering checks, not independent research samples.
- Admission-only C1/C3 deliberately produce post-fence effects; commit-fenced C1/C3 deny them. C0/C2 preserve legitimate effects. Five negative-control schedules per arm require their exact denial cause. C3 retries one logical operation three times, not three independent trials.

Three v0.2 causal-treatment checker defects were found after initial apparent passes and corrected. A no-effect endpoint alone had accepted the wrong denial cause or broken delegation/preparation dependencies. The endpoint and treatment qualification are now separate. Earlier source, failed controls, corrections and counterexamples remain in the frozen archives. Four v0.1 checker blind spots and their regression history are retained there too; earlier runs must not be described as passing later controls.

## Next design step

[Design decision, 2026-10-31](docs/decisions/2026-10-31-checkpointed-workflow-candidate.md): assess a checkpointed LangGraph workflow to ask whether resumed or retried delegated work can create a new protected effect after durable authority revocation.  This is a candidate direction; a specific workflow and protocol remain to be selected, and no framework-based experiment has run.  The note records source rationale, comparison requirements, deferred alternatives and the distinction between an authorized intent and an external effect.  Historical qualification and traceability artifacts remain unchanged.

## Read and navigate

| Record | Location |
| --- | --- |
| Canonical executed v0.2 bounded protocol | [PROTOCOL.md](qualification/v0.2/PROTOCOL.md) |
| Current code, tests, scenarios and recorded final summary | [qualification/v0.2](qualification/v0.2/) |
| Broader research design (not full implementation conformance) | [Specification v0.1](docs/specification/Testing_Revocation_in_Delegated_Workflows_v0.1.docx) |
| Original separate AI-assisted review | [Review report](docs/review/REVIEW.md), [semantic assertions](docs/review/semantic_checks_final.json), [IPC assertions](docs/review/ipc_checks.json) |
| Original package explanation | [Historical package README](docs/review/ORIGINAL_PACKAGE_README.md) |
| AI-use and research-decision workbook | [Workbook v0.1](docs/traceability/Revocation_AI_Use_and_Research_Decision_Traceability_v0.1.xlsx) |
| Shared editable traceability data | [JSON](docs/traceability/revocation_traceability_content_v01.json) and [CSV tables](docs/traceability/) |
| Portable Obsidian-compatible research notebook | [Notebook ZIP v0.1](notebook/Revocation_Research_Notebook_v0.1.zip) |
| Complete frozen raw/source history | [v0.1 ZIP](archives/qualification_revocation_v01.zip), [v0.2 ZIP](archives/qualification_revocation_v02.zip) |
| Provenance and local staging verification | [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json), [STAGING_VERIFICATION.json](STAGING_VERIFICATION.json) |
| Integrity | [SHA256SUMS](SHA256SUMS) |

The compact runnable tree does not duplicate every historical run. Extract either ZIP into a separate directory to inspect its complete raw SQLite data, traces, exact source snapshots, logs, original manifests and counterexamples. Relative paths in the unchanged historical README/review refer to those original package/reviewer layouts, not this compact tree. The copied review reports are records, not runnable scripts; full historical review scripts and evidence are inside the v0.2 archive.

## Reproduce current qualification

Use an existing Python 3 installation with its standard-library `sqlite3` and multiprocessing support (verified here with Python 3.12). No packages, network access, model/API calls or installation are needed. From the repository root:

```sh
# Keep newly generated evidence outside this repository.
cd qualification/v0.2
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v
PYTHONDONTWRITEBYTECODE=1 python test_qualification.py
(cd legacy_v01 && PYTHONDONTWRITEBYTECODE=1 python -m unittest -v)
PYTHONDONTWRITEBYTECODE=1 python harness.py --output ../../../revocation-fresh-run
```

The output directory **must not already exist**; choose a new name for each rerun. Inspect its `results.json` (expected `QUALIFIED`, 18 cases), `runtime.json`, source snapshot, per-case JSON and SQLite files. `QUALIFIED` means the finite declared fixture expectations and causal treatment checks matched; deliberately seeded `VIOLATION` controls are detector successes, not safety passes. Missing/malformed/conflicting evidence is not evidence of safety. The harness has bounded IPC waits and preserves failed run output.

To check file integrity from the repository root on systems with `sha256sum`, run `sha256sum -c SHA256SUMS`. The manifest covers all delivered files except itself; it establishes byte integrity, not correctness or authenticity. Original archives retain their own manifests. [Staging verification](STAGING_VERIFICATION.json) records a fresh run outside the staging tree and confirms the six runnable source hashes match the reviewed final source.

## Limits, disclosure and release status

- **Assumed mediation, not hostile-worker confinement.** Gateway write code is separated from workers, but all processes share an OS user and accessible filesystem. Tokens are deterministic identifiers, not cryptographic credentials. Same-host observation is not tamper-proof; parent-child delivery is worker/harness evidence, not independently witnessed by the database observer.
- No AI agent/LLM, autonomous planning, AGI-control result, nested delegation, remote effect, regrant, crash-durability campaign, exhaustive concurrency exploration, population estimate or universal safety claim. Novelty remains unestablished; this is not a SOUNDGATE replication or a deployed-system vulnerability finding.
- AI assisted framing, literature/source analysis, code, tests, review and documentation. Separate model-assisted review is **not independent human validation**. The workbook distinguishes recorded human decisions from unrecorded human verification. No claim of exhaustive human review is made.
- **Private research upload authorized; public release is not authorized.** This repository introduces no open-source license grant, public website change, deployment or CI auto-run. No license file is supplied pending an explicit choice. Publication requires a separate review of claims, rights and private identifiers.
- The byte-preserved workbook, JSON/CSVs and notebook describe a *proposed* repository because that was true at their capture. The subsequent private repository authorization does not retroactively change those snapshots. The private repository was subsequently created at [node-and-norm/revocation-delegated-workflows](https://github.com/node-and-norm/revocation-delegated-workflows). This later status does not rewrite historical captures. Local staging verification is separate from remote upload verification.
- Traceability includes bounded, approved research-decision quotations and source locators. It is neither a complete conversation export nor an immutable audit. No separate chat exports, internal notes, tool prompts or unrelated personal records are included.
- Prior approval-evidence work is separate **private prior work**. Its repository, artifacts and public website are unchanged; this record does not invent a public link or transfer its results into Q1.

Qualification, review and bounded corrections are complete for this stage. Later experiments, public publication and claims beyond the declared protocol need a new explicit scope.
