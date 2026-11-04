# Temporal protocol reconciliation and acceptance checklist

Mark Julius Banasihan · 4 November 2026 UTC

Status: AI-assisted read-only artifact/source review; no independent human validation. This note changes no code or historical draft and runs no test. It neither retries the denied socket operation nor authorizes execution.

## Current interpretation

The six-cell plan remains a proposed native-interface conformance study. The implementation candidate has four passing schema-only tests and a blocked bridge-control attempt. It has no executed native Workflow/Activity result. Runtime installation and server health are a separate setup achievement.

The evidence-view intervention preserves underlying records and removes a derived application envelope. Its supported purpose is packaging/reconstruction and deterministic assertion support. It does not evaluate unavailable completion evidence, reviewer performance or review-time savings.

## Version and source precedence

| Record | Use now | Limitation |
|---|---|---|
| temporal_protocol_20261103/PROTOCOL_REVIEWED_DRAFT_v02.md | Historical corrected draft | Earlier wording is preserved, not silently promoted over later clarification |
| temporal_protocol_20261103/PROTOCOL_DRAFT.md, section 13 | Explains the later interpretation and points to the concrete contract | Its original pending archive/runtime statements describe drafting time |
| temporal_protocol_20261103/STATUS_EVIDENCE_CONTRACT_v01.md | Governs the proposed six-cell matrix, orthogonal evidence fields and packaging views | No frozen runtime-conformance result; observed outcome mappings remain open |
| temporal_protocol_20261103/STATUS_EVIDENCE_CONTRACT_v01_reviewed_snapshot.md and DESIGN_CHANGELOG.md | Show corrections, including no-effect categories and packaging scope | Earliest drafts were edited in place; byte-complete drafting history is not claimed |
| temporal_runtime_qualification_20261104/QUALIFICATION_SUMMARY.md and provenance/runtime-manifest.json | Later runtime setup state: SDK 1.25.0, CLI 1.10.0, reported Server 1.32.2, Node 24.22.1, package lock and health check | Supersedes the earlier “runtime unpinned” status only for the recorded setup. No native workflow qualification follows |
| temporal_qualification_20261104/BRIDGE_LIFECYCLE_SPEC_v01.md | Proposed Q0-Q4 qualification sequence and bridge/lifecycle assumptions | Qualification is separate from six-cell measurement; historical-effect C4 coverage remains to be explicitly mapped |
| temporal_methods_review_20261104.md | Independent AI-assisted source review of unchecked success, different observation cuts and historical enum discrepancy; later clarification identifies current draft as already corrected | Prospective source-derived findings, no native execution or human validation |
| temporal_qualification_20261104/review/BRIDGE_REVIEW_v01.md | Source-review findings and partial-attempt assessment | Permission to attempt qualification is not an empirical pass |
| temporal_qualification_20261104/STATUS.md, logs/q1_schema.txt, logs/q2.txt | Latest recorded execution boundary: four schema methods passed; Q2 socket EPERM before dispatch, then cleanup BrokenPipe; two escalated commands denied before execution | Proposed corrections in those denied commands were not applied; no native run or measured collection |

The archive/gateway verification recorded in STATUS.md resolves the earlier materialization prerequisite. It does not resolve bridge conformance. The current source folder remains a development candidate; source snapshots have historical value and do not establish execution.

## Exact mapping decisions still needed

1. **Native terminal event to intended treatment.** native_runner.cjs lines 43-57 accept a linked completed, failed or canceled terminal event, rejecting timeout. This checks cardinality/linkage but does not require a schedule-specific native disposition. Before acceptance, define the expected tuple for each mode and behavior: Activity cancellation observed, Workflow-side promise outcome, server terminal type and sink disposition. A correctly reported unexpected failure is diagnostic evidence, not a successful treatment.
2. **Workflow completion to Activity success.** workflows.ts lines 18-28 catches an Activity failure and returns state after the hold. The Workflow can therefore complete while the Activity failed or was canceled. Use exact separate fields; never map overall completion to successful protected work.
3. **Instrumentation to settlement.** native_runner.cjs lines 20, 27 and 33 distinguish finally instrumentation from the inbound interceptor's settlement record, but the runner waits on the finally flag. Require explicit presence/linkage of the interceptor observation when claiming Worker settlement. Neither record alone is a native terminal event or broad cessation proof.
4. **Run/attempt/effect identity.** The native chain checks scheduledEventId and attempt 1 (lines 48-55). Acceptance must also reconcile recorded Workflow/run IDs, Activity identity and the exact bridge request/operation/ledger key. The single-fixture bridge request ID is locally supplied correlation, not authentication or an ID echoed by the historical gateway.
5. **Behavior selection.** supervisor.py lines 35-50 treats every non-cooperative value as continuation and fences only the literal continue_fenced. Declare and check the accepted behavior/mode values before a case can satisfy a named treatment. A mistyped label must not silently become an unfenced control.
6. **Primary and cleanup outcomes.** native_runner.cjs lines 64-66 writes native_result.ok before Worker shutdown and only logs a shutdown error. supervisor.py lines 57-62 can preserve ok=true while adding a final snapshot_error. Acceptance needs separate primary-observation, evidence-completeness and cleanup fields; an overall pass must account for all required fields. These are static potential inconsistencies, not observed native failures.
7. **Failure observation cut.** native_runner.cjs line 65 exports failure history before its Worker shutdown at line 66. supervisor.py captures its final/precleanup sink snapshot after Node exits or fails (lines 53-64). Those records therefore need not describe the same precleanup cut. The filename supervisor_precleanup means before supervisor cleanup, not before all Worker cleanup. Require coordinated native-history and sink capture at an explicit causal barrier before any cleanup, or label these records as different-cut diagnostics and prohibit them from supporting primary no-effect or cessation claims. Do not use cross-process timestamps to manufacture a shared cut.
8. **Qualification-to-measurement mapping.** C1 cooperative cancellation and C4 historical effect belong to protocol qualification. The Q0-Q4 bridge plan explicitly covers cooperative/native continuation but does not clearly instantiate C4. Record its coverage or explicit deferral. Q2 live/fenced gateway controls are not measured K1/K2 cells by relabeling.

9. **Unchecked sink-success path.** The native Activity returns the bridge response without grading its sink disposition; the Workflow can return that value or a recorded failure; the runner can emit ok=true after release. supervisor.py lines 55-57 then snapshots SQLite and sets ok=true without checking expected effect count, attempt count, denial reason or transaction order. A transport-successful response with the wrong sink outcome could therefore satisfy these existing success flags. Before acceptance, a separate artifact checker must inspect raw ledger rows and linked requests, verify the schedule-specific effect/denial expectations and causal ordering, and grade independently of runner ok flags. The Q2 control script's two explicit outcome assertions do not supply this missing native-case check.

## Acceptance checklist

Every item has one of: satisfied by cited evidence, unsatisfied, unobserved, or not applicable with a reason. Missing evidence never becomes an implicit pass.

| Gate | Required acceptance evidence | Current state |
|---|---|---|
| Authorization and environment | Approved bounded operation and a permitted execution path; no workaround around denied access | Socket correction/rerun remains stopped following two denials |
| Reuse and runtime | Exact source hashes, unchanged gateway, resolved dependencies and actual runtime manifest for the attempted run | Historical reuse and setup recorded; bridge/native run manifest absent |
| Actor separation | Spawned child-only bridge, closed privileged copies, fixed binding, no controller routing or direct sink writes | Source-reviewed; transport conformance unobserved |
| Q1 transport | Creation failure, partial send, response timeout/receive failure, truncation/size, one dispatch/no retry, finite cleanup | Four schema tests only; transport mock coverage incomplete |
| Q2 positive controls | Valid live effect and exact revoked denial in independently inspected sink rows, with normal bounded cleanup | No control pass; EPERM before dispatch and cleanup error |
| Causal treatment | Activity started before cancellation; actual cancellation observation before continuation; fence transaction before fenced attempt | Native observations absent |
| Lifecycle | Activity outside shield, hold entered, matching release succeeds before timeout, actual native history retained | Source-reviewed; runtime unobserved |
| Native mapping | One linked schedule/start/terminal/attempt; exact expected tuple for mode/behavior; unexpected failures preserved | Proposed checks exist; expected mapping and execution unqualified |
| Effect accounting | Independent raw-ledger checks of attempt/effect counts, exact denial reason, valid pre-existing grant/admission, fence/effect transaction order, explicit no-effect/no-fence categories | Native candidate stores sink rows without grading these expectations; independent native-case checker remains outstanding |
| Evidence support | Each assertion cites allowed evidence; underlying records and packaging intervention remain explicit | Contract only; envelopes/allowlists not qualified |
| Failure preservation | Primary error, coordinated history/sink observation cut before all cleanup, secondary cleanup errors, uncertain dispatch and final process states separately retained | Initial attempt exposed capture/cleanup gaps; native failure history and supervisor snapshot are not yet proven to share a cut. Different-cut snapshots are diagnostic only for primary no-effect/cessation claims |
| Final classification | Primary treatment validity, evidence completeness and cleanup accounted separately; no success inferred from exit zero alone | Additional static flag inconsistencies identified above |
| Independent review | Corrected candidate and actual records checked before measured-study decision | Source reviews available; no native records to review |

A later accepted qualification result would support instrument readiness only within its declared coverage. Measured collection needs a separately frozen case mapping and decision. No novelty, general reliability or AGI-control conclusion is implied.

## Primary contract references already inspected

- Temporal SDK cancellation contract: https://github.com/temporalio/sdk-typescript/blob/efafd16ef4533da24029277bd72caf564c7aa007/packages/common/src/activity-options.ts
- Temporal cancellation scopes: https://github.com/temporalio/sdk-typescript/blob/efafd16ef4533da24029277bd72caf564c7aa007/packages/workflow/src/cancellation-scope.ts

The source-pinned contract distinguishes request propagation, Workflow-side reporting and Activity final state. The local implementation must be evaluated against that contract without equating cancellation with application authority fencing. This reconciliation uses previously inspected sources and current local artifacts; it makes no new current-vendor or live-service claim.

## Independent review correction

On 4 November 2026 at approximately 18:10 UTC, the parent relayed an independent AI-assisted review finding: native failure history precedes Worker shutdown, while the supervisor sink snapshot can follow Node exit. This revision adds the shared observation-cut requirement and explicitly limits different-cut snapshots. The preceding draft is preserved as RECONCILIATION_AND_ACCEPTANCE_pre_review.md (SHA256 1626d419f74b0be5eebdfe9eb144da69b2361460bd5db106131a160b5744634e). This is a documentation correction from source review. No code was changed, execution attempted or runtime behavior established.

## Reviewed candidate identity and remaining methods work

The source hashes below bind the files inspected for this reconciliation. They identify bytes, not execution authenticity or correctness. Historical reviews may cover earlier versions; their dates and explicit version claims remain separate.

- source/native_runner.cjs: 7dfb0f28bf7a842cd0a6985015d00d8dca0b3004f0440ac6fee68a42ebf045af
- source/supervisor.py: cb610697cfd3d196516c223841bbb86ce4da4fa5599f57dd85820fd9de3379c7
- source/bridge.py: bd0789354e8a53aa115db6a07e8a8437ba8a8a479ddd83ff47de717a92871084
- source/workflows.ts: 3a90ebeb1ea37a5b285388b9f6acec31b6c5931d1057a630a789460e9c926e46
- source/gateway.py: 98445edd61af21bc5c740053f8a93f6c179e4c5efa7b28dd7363e779b8f059a9
- source/qualify_bridge_controls.py: 1b14ad6cfe441c4d7880d424e8352df41a8ec5dbe5f6731ab0b192ecc2a04ba4
- source/test_bridge.py: 98aebaa268c22d569b216df18625a350204b807b61f076a94143aa5dbe1692e8

Before any qualification acceptance, close three separate methods gaps: the remaining Q1 transport/failure mocks, frozen caller-view file allowlists with duplicate-leakage checks, and an independent native-case artifact checker. The checker must distinguish wrong denial causes and invalid authorization setup from successful prevention, and retain unresolved or invalid-treatment classifications. None is established by this reconciliation.

The parent also relayed a second independent AI-assisted methods review requesting the concrete sink-success path and stronger evidence checks. Those requests are incorporated here. This parent-relayed review is a source for the correction, not independent empirical validation. The exact artifact was subsequently read and verified at temporal_methods_review_20261104.md. Its clarification confirms that the missing no-effect category belongs to the preserved v02 snapshot; the current PROTOCOL_DRAFT.md already contains it. The historical snapshot remains unchanged.
