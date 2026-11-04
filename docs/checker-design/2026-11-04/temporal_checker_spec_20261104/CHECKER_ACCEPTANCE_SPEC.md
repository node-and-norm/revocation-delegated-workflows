# Proposed independent Temporal artifact checker

4 November 2026 UTC. AI-assisted methods specification, not implementation, executed test, qualified instrument or measured result. No denied socket operation, candidate patch or alternative execution route was attempted. This specification does not authorize those actions. The historical gateway remains unchanged.

## Provenance and controlling scope

Reviewed merged commit `5ceceb4b0f30e8c0608b641d71785a6ce2317c8a` through the GitHub connector. Controlling reconciliation: `docs/research-records/v0.1/sources/reconciliation.md`, Git blob `d551cd58ba5309c12b95b102abfd3adb7a5c9ea5`. URL: https://github.com/node-and-norm/revocation-delegated-workflows/blob/5ceceb4b0f30e8c0608b641d71785a6ce2317c8a/docs/research-records/v0.1/sources/reconciliation.md . `SOURCE_RECONCILIATION.md` is a locally reconstructed text copy for reading, not a byte-identical repository export.

Local source files in `temporal_qualification_20261104/source/` were rehashed and matched the reconciliation's native_runner, supervisor, bridge, workflows and gateway hashes. Earlier source analysis is preserved in `temporal_methods_review_20261104.md`. The contract remains `temporal_protocol_20261103/STATUS_EVIDENCE_CONTRACT_v01.md`; no new native outcome mapping is inferred here.

## Independence and inputs

The checker consumes immutable saved artifacts, never drives the Worker, bridge, gateway or controller, and never uses `ok`, exit zero or summary prose as an oracle. It recomputes findings from raw exported Temporal history, instrumented events, bridge records, the captured SQLite database, effective configuration, source/runtime manifest, protocol version, caller-view allowlist and cut manifest. Local records are trusted fixture evidence, not authenticated provider certificates. A matching hash proves identity of bytes only.

Parsing must fail closed on duplicate JSON keys, unsupported schema, duplicate logical identifiers, missing referenced files, unresolved references, malformed/truncated records, or unsafe paths outside the case root. Such problems prevent acceptance but do not erase separately established positive facts. Do not repair input records silently. Unknown fields may be preserved as uninterpreted data; they cannot satisfy a required assertion.

## Result model

For every requirement emit one of `satisfied`, `unsatisfied`, `unobserved`, or `not_applicable`, plus evidence references and explanation. `not_applicable` requires a declared case-specific reason and cannot be chosen to excuse a required control.

Return separate dimensions:

1. Artifact integrity/completeness.
2. Intended treatment validity, including causal schedule and valid authorization setup.
3. Native observed tuple: cancellation observation, Workflow promise outcome, Worker interceptor observation, native Activity terminal type and Workflow terminal type. Keep missing values unresolved.
4. Sink facts: execute attempts, effects, denial reasons, fence existence and authoritative ordering.
5. Caller-supported assertions for each permitted view.
6. Primary-cut validity and cleanup outcome.
7. Eligibility for qualification acceptance and, separately, measured inclusion.

A single Boolean is optional convenience only, derived after all dimensions are retained. Qualification acceptance requires every applicable mandatory gate satisfied, all mappings reviewed, and cleanup acceptable. Any unsatisfied gate blocks acceptance; any unobserved required gate prevents acceptance. Do not label all failures a security failure. A valid record of an unexpected error is diagnostic evidence, not treatment success. A confirmed effect remains confirmed even if cleanup failed; the run can nevertheless be ineligible. Qualification and measured denominators are never pooled.

## Acceptance rules

A01 Identity: validate case mode and behavior against explicit allowlists. Match Workflow ID/run ID, Activity ID, scheduled event, start event, attempt, operation ID, authority scope, capture ID and protocol/runtime versions. A case label cannot override raw evidence. Use the correct scheduled/start reference fields present in the pinned event schema; do not invent absent fields.

A02 Native lifecycle: require one ordinary Activity schedule/start/terminal chain and attempt 1 for eligible native cases, matching effective options. Explicitly check retry policy, timeout and cancellation mode. Record both Workflow promise settlement and actual server disposition. The expected mode/behavior tuple remains a reviewed qualification output; until defined, record the actual tuple but do not accept a guessed mapping.

A03 Treatment: require positive Activity-start and cancellation-observation evidence, not heartbeat emission alone. Check causal links from observation to continuation release to execute. For fenced continuation, require revocation commit before release and execute receipt. Reject early Workflow closure, hold timeout or mismatched release. The two modes must receive the same intended continuation schedule without hidden differences in sink evidence.

A04 Authorization setup: inspect bootstrap, grant and admission records and their ordering before the protected attempt. Validate the fixed actor, grant, ticket, scope, root and epoch according to the unchanged gateway contract. A denial caused by wrong ticket, wrong actor or invalid grant is not a successful revoked-authority control. The known fixed-root/epoch and single-outstanding-operation limits remain explicit.

A05 Sink accounting: count execute `receipt` events, not all gateway receipts. Link each execute to its terminal result through request ID and transaction/event ordering under the fixture's single-operation assumption. Inspect effects separately and join `effects.event_seq` to the corresponding `effect` event. Compare payload/scope/root/epoch and reject orphan, duplicated or inconsistent rows. A summary count of one is insufficient.

A06 Expected sink outcomes: cooperative qualification requires zero execute attempts and zero effects; unfenced continuation requires exactly one execute attempt and one matching effect; fenced continuation requires exactly one attempt, one exact `revoked` denial, zero effects and the preceding revocation. K1/K2 no-cancellation controls require their own case identities, positive authorization setup and observation records. Prior Q2 records cannot be renamed measured cells. C4 historical-effect qualification needs explicit additional coverage: effect before cancellation request, preserved afterward; it remains unexecuted and not implemented here.

A07 Ordering: use sink event sequences within the committed ledger and linked causal barriers across processes. Distinguish no effect, no fence, no cancellation request, and unresolved. Wall-clock proximity does not establish causality. Detect cycles or contradictory order relations; do not resolve them using timestamps.

A08 Cut: require a declared causal capture protocol before Worker cleanup. Bind each source to its own boundary (Temporal event ID, ledger sequence, instrumentation position) and one cut identity; do not imply simultaneous global atomicity. Capture all SQLite tables within one read transaction to avoid mixed-commit snapshots. If producers can still mutate the relevant state and no valid boundary is established, do not accept absence/completeness conclusions. Post-cleanup snapshots remain diagnostic and cannot retroactively complete primary evidence.

A09 Cleanup: preserve initial error, uncertain dispatch, shutdown errors and forced termination separately. Missing capture acknowledgment, Worker shutdown error, nonzero child exit or forced cleanup prevents an overall qualification pass under the current finite-cleanup plan. Never rewrite previously saved primary records. Hash/content differences between primary and cleanup are reported, not merged away.

A10 Caller support: classify each assertion using only the selected view's explicit file/field allowlist. Privileged checker access does not authorize caller access. Effect absence requires complete bounded sink evidence for that operation/cut. Missing fence receipt means caller uncertainty, not no fence. Unknown native evidence means unresolved, not no effect. Unsupported assertions fail even when hidden truth happens to agree.

A11 Packaging comparison: View A includes the derived envelope; View B removes that envelope while retaining the same predeclared underlying evidence. Baseline and proposed projection have equal evidence and review budget. Source-linked reconstruction in View B may reproduce all conclusions and is a valid result. The intervention does not model actual loss of completion evidence or measure human efficiency. A revealing path/name or duplicate envelope must not leak a withheld object; legitimate reconstruction from permitted raw evidence is not leakage.

A12 Freeze: exact code, checker, test vectors, source/runtime versions, accepted native tuples, allowlists, case mapping and cut contract must be reviewed and frozen before measured collection. Unexpected qualification tuples trigger investigation and a versioned decision, not post-hoc alteration of measured expectations. Each measured case has an explicit inclusion/exclusion reason.

## Prospective test vectors, not executed tests

All vectors below are specifications. They may later be represented as synthetic saved artifacts, clearly marked synthetic. They do not count as native runs or observations. Correlated mutations must change related summaries and records consistently where possible, so tests exercise semantics rather than only stale hashes.

T01 Positive cooperative fixture: valid start/cancel observation, no execute/effect, reviewed native tuple, valid cut and normal cleanup -> all required gates satisfied.
T02 Positive unfenced continuation fixture -> one linked effect, no fence in complete window, valid treatment.
T03 Positive fenced continuation fixture -> one exact revoked denial, zero effects, fence-before-attempt, valid treatment.
T04 Bridge failure caught by Workflow, completed Workflow and `ok:true` summaries, no effect -> no qualification acceptance despite zero exit.
T05 Fenced fixture with invalid-ticket denial and zero effects -> denial fact retained, intended treatment unsatisfied; not credited as fence protection.
T06 One effect in summary but missing actual effect row, or orphan effect_seq -> accounting unsatisfied.
T07 Duplicate execute receipt plus one effect and one duplicate outcome -> attempt-count gate unsatisfied even though effect count is one.
T08 Consistently alter request/run/attempt mapping -> linkage unsatisfied without relying only on hash inequality.
T09 Remove cancellation observation while retaining heartbeats -> causal treatment unobserved, not cooperative pass.
T10 Change behavior to misspelled continue_fenced value -> configuration rejected; no fallback to unfenced treatment.
T11 Missing/reversed revocation and release relation -> effect/fence facts retained where supported, intended fenced schedule unsatisfied or unobserved.
T12 Expected tuple undefined, or unexpected native failure with valid history -> tuple recorded, qualification unresolved/unsatisfied pending investigation, never invented pass.
T13 Effect appears only during Worker cleanup -> primary cut cannot borrow cleanup evidence; record separate phase-specific facts.
T14 Missing cut acknowledgment or mixed history/sink cuts -> primary completeness unobserved; no primary absence/cessation claim.
T15 Concurrent commit between table reads -> reject mixed snapshot; a transactional capture must retain a consistent pre- or post-commit state. This is a planned capture test, not a claimed checker ability to infer every undetectable race.
T16 Normal primary result followed by shutdown error -> primary facts retained, cleanup gate unsatisfied, overall acceptance blocked.
T17 Truncated history, duplicate JSON keys, or missing allowlist file -> completeness/parser gate fails closed.
T18 Hidden true fence with no permitted caller evidence -> privileged fence fact present, caller fence assertion unresolved.
T19 Remove derived envelope only, retain complete permitted raw evidence -> baseline may reconstruct the same conclusions; do not manufacture a benefit.
T20 Leak envelope contents through filename or alternate duplicate record -> view-isolation gate unsatisfied; legitimate raw-evidence reconstruction remains allowed.
T21 C4 effect before request remains in final ledger -> preservation fact supported only with complete linked records; no rollback claim.
T22 Relabel qualification record as measured K1 -> provenance/phase gate unsatisfied.

Metamorphic properties for later checker tests: removing supporting evidence cannot create a stronger supported claim; adding irrelevant files cannot improve support; permuting independent record serialization does not change causal conclusions; wrong claims cannot pass merely because hidden truth matches; cleanup evidence cannot repair an absent primary cut; consistently renamed opaque IDs preserve conclusions only if every scoped mapping stays valid. Exceptions such as newly detected contradiction must be represented explicitly rather than weakening these rules silently.

## Current status and next dependency

This specification closes no runtime gate. It makes the outstanding independent-checker obligations implementable and reviewable. Native mappings, capture instrumentation, transport mocks, C4 coverage and execution permission remain separate dependencies. The two earlier denials remain in force for the denied operation; there was no retry or route change in preparing this document. A future implementation should begin as a separately reviewed artifact-only checker, without importing or executing the gateway/Worker candidate.
