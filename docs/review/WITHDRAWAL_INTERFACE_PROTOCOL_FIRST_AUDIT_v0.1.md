# Protocol-first independent artifact audit

## Result

All 12 measured cases satisfy the implemented checks: 660 baseline assertions and 78 supplemental assertions, with no failures. These counts are checks, not independent experimental observations. All 15 baseline negative controls and 5 additional coordinated semantic controls are rejected. No collection was rerun, and no original archive/source/data was edited. No network calls were made.

On both paths:
- S0: one effect, no fence, caller IDLE.
- S1: fence before execute, revoked denial, no effect, caller confirmed before execution.
- S2: one effect before fence and retained afterward, caller confirmed only after completion delivery.
- S3: fence before execute, revoked denial, no effect, caller PENDING at execution and confirmed after completion delivery.
- S4: fence committed, revoked denial, no effect, caller unconfirmed at observation end because completion was withheld at relay.
- S5: one effect, no committed fence within recorded observation, caller unconfirmed.

## Independent implementation and provenance

The checker was written from frozen_candidate_v02/PROTOCOL.md and raw measured JSON/SQLite schemas and contents. No original checker, caller, relay, scheduler, gateway, workflow, summary or review implementation was read or imported before or after implementation. The only imported audit code is this newly authored checker. Inputs were selectively extracted from the archive into this new directory. SQLite opens use mode=ro and immutable=1. Baseline code and outputs were preserved unchanged when coordinated mutants and supplemental checks were added.

This is an independently authored AI-assisted artifact checker, on the same host, using the same study's recorded artifacts. It is not independent collection, independent implementation of the gateway security mechanism, human validation, or organizationally independent replication. JSON and database records can agree because they share provenance; their consistency does not establish authenticity against a malicious recorder.

## Implemented contract checks

Caller state is replayed from permitted caller inputs without importing the caller transition function and without using stored pass/fail flags. The resulting state is compared with recorded before/after/final states and separately with the frozen schedule. Envelope identity, root, epochs, status, scope, and actual response are checked. Input-field allowlists reject trace-visible privileged data.

Actual SQLite tables are compared to the stored final snapshot. Every outcome must have a prior matching committed receipt; there must be exactly one execute receipt and outcome, at most one revocation pair, and correct revocation content and request correlation. Effect rows must agree with effect events, must precede any fence, and must meet exact schedule counts. Authority state must agree with committed fence evidence. Child/parent grant, admitted ticket, owner, scope, and execute relationships are checked separately.

Barrier event histories must be monotone exact prefixes of SQLite events, with corresponding effect snapshots. Fence and execute barriers contain their committed outcomes. Terminal observation exactly agrees with the persisted database and final caller state. Schedule barrier ordering and caller knowledge at execution are checked.

Relay received responses must equal committed revocation outcomes; forwarded envelopes must equal caller inputs, and receipt must precede forwarding. Adapter request/response records must match committed execute records. Framework pause/resume records show distinct recorded PIDs, matching checkpoint references, persisted then consumed interrupts, and exact tool/final-assistant outcome propagation. All 12 raw worker JSON files exactly match their embedded copies.

## Negative controls

Baseline controls cover premature completion on acceptance; wrong root, withdrawn epoch, new epoch, request ID, status and gateway response; trace-visible privileged input; missing execute receipt; missing required effects in S0/S2/S5; inserted post-fence effect; dropped framework messages; and altered observation cutoff.

Some baseline database mutants are caught by both semantic checks and snapshot mismatch. The additional coordinated controls synchronize snapshots and barriers and still reject missing required effects, missing execute receipt, and an S2 effect moved after its fence. Results explicitly show snapshot equality passing, while semantic assertions fail. These are in-memory artifact mutations, not new measured executions or mutations to archived files.

## Limits and unsupported conclusions

- No runtime proof of caller access isolation. The field allowlist checks visible trace data only; static source review or execution instrumentation is required to rule out hidden filesystem/database access. This checker does not claim that test is satisfied.
- No inspection of actual framework checkpoint database contents. Checkpoint continuity and distinct PIDs are recorded evidence; they do not independently prove process behavior or resumed state authenticity.
- Protocol-specific expected states and schedule order are conformance assertions, not discovered causal effects. The caller replay and actual effect derivation remain separate from those schedule assertions.
- The frozen protocol fixes semantics but not every serialization detail. Exact event labels, JSON structure, record-copy equality, barrier names, worker structure, and numeric PID comparisons are representation-consistency checks learned from raw records, not additional protocol promises.
- The checker validates this complete fixture schema, not arbitrary malformed JSON. Missing structural keys may raise exceptions instead of returning a normalized failing verdict. It is not a production parser.
- No proof of arbitrary target binding at the unchanged gateway, genuine network loss, restart recovery, distributed closure, rollback, cessation of computation, exposure probability, production latency, novelty, or deployment readiness.
- No cryptographic signing, trusted timestamps, or independent witness establishes recording authenticity. SHA-256 preserves audit-file provenance only.

## Files and rerun

Run only the audit, without invoking study code:

    python independent_contract_audit/check_contract.py
    python independent_contract_audit/coordinated_mutants.py
    python independent_contract_audit/supplemental_checks.py

Outputs: results.json, coordinated_mutants.json, supplemental_results.json, and captured stdout files. SHA256SUMS.json records audit files and extracted inputs. INPUT_PROVENANCE.json verifies extracted inputs byte-for-byte against archive entries and records archive SHA-256.
