# Independent Temporal evidence checker: source-derived draft

4 November 2026. Separate design artifact. No code, tests, sockets, Workflow execution, transport mocks or experiments were run for this draft. No existing candidate or historical artifact was modified. This is not a failure-capture patch or an execution-authorization proposal.

## Scope and source basis

Check deterministic fixture consistency, expected sink effects, scoped temporal ordering, native outcome correspondence, coordinated observation cuts and caller-visible assertion support. Do not certify authentication, arbitrary descendants, global cessation or production reliability.

Inspected local sources:
- `temporal_protocol_20261103/PROTOCOL_DRAFT.md` and `STATUS_EVIDENCE_CONTRACT_v01.md`.
- `temporal_qualification_20261104/source/{gateway.py,workflows.ts,native_runner.cjs,supervisor.py}` and `STATUS.md`.
- `temporal_methods_review_20261104.md`.
- `repo_revocation_pilot_remote_verification_20261103/final_extracted/revocation-delegated-workflows-main/integration/v0.3/checker.py` and local `verification.json`.

The local verification record reports remote commit `381ce4526e4fa177ce5b10640983213b59becd21`, archive `b088613324c731e900e71317be725a8f2a8002d22a29bc40dcc4670ffb68f3c9`, 67 manifest checks and 42 byte-identical historical files. These are inspected prior records, not verification newly performed here. Current remote state was not queried.

The historical checker provides useful independent ledger/transcript checks. Its eight direct/framework cases are not Temporal qualification. Reuse its concepts, not its runner-supplied truth flags or fixed event sequence without a separately frozen Temporal schedule.

## Immediate conclusions

1. `ok:true` in native or supervisor output means, at most, that its collection path reached that statement. It cannot be a qualification input: Workflow catches Activity errors, runner permits failed/canceled/completed Activity terminals, and supervisor does not assert expected effects or revoked-denial cause.
2. Current `supervisor_precleanup.json` is written after waiting for Node exit on the successful path. Node shuts its Worker down before exit. That snapshot is not certified pre-Worker-cleanup. A later snapshot cannot retroactively repair a missing primary cut.
3. An exact native outcome mapping must be established in separately authorized qualification, reviewed and frozen. Documentation allows a set of native outcomes; that is not permission for the checker to accept any outcome indiscriminately.
4. The current mutable protocol includes the no-effect category, unlike an older preserved snapshot. Additional vocabulary disagreement remains: `not_applicable_no_fence` versus `no_fence_in_complete_window`, and `not_applicable_no_event` versus `no_request`/`no_observation`. Freeze one schema and an explicit migration; never silently normalize an ambiguous absence.

## 1. Independent inputs and outputs

The checker is a read-only offline consumer. It must not import runner, Workflow, bridge or gateway modules, connect to Temporal, create sockets, or execute candidate code. A future implementation should use plain parsed records and read-only SQLite with an explicit consistent read transaction. The manifest identifies every input by bytes/hash and lists expected schema versions; hashes establish fixture identity, not authenticity.

Inputs:
- Frozen design manifest: cell, identities, operation ID, ordinary Activity mode/options, runtime/source pins, expected sink semantics, exact native mapping version and view allowlists.
- Raw native history export for a specified Workflow run, with pagination/completeness receipt, final included event ID and capture identity. Never infer complete history merely from contiguous IDs.
- Workflow-side settlement record and held-open observation evidence; Activity and Worker instrumentation, with their own scopes.
- Sink tables `authority`, `grants`, `tickets`, `events`, `effects` captured in one read transaction, transaction high-water mark and completeness boundary.
- Controller/bridge records linking release sends and receives, request/response IDs, authority receipts and cut acknowledgments.
- Raw caller assertions and exact per-view file allowlists; projection generated separately from privileged adjudication.

Each result has four independent dimensions:
- `collection`: complete / incomplete / conflicting.
- `treatment`: valid / invalid / unresolved, with rule failures.
- `conformance`: pass / fail / unresolved / not_evaluated.
- `assertion_support`: supported / unsupported / unresolved, per assertion and view.

Known adverse facts survive incomplete collection. For example, one committed wrong-epoch effect remains a failure even if the history export is incomplete; incompleteness does not erase it. Missing evidence is unresolved rather than a false pass. A run is eligible to qualify only with complete, nonconflicting evidence, valid treatment, pinned mapping, all required checks passed and no unsupported assertions. Cleanup status is reported separately and never upgrades a primary verdict.

## 2. Sink oracle

Never use `behavior`, `revoked`, `prior` or summary `ok` fields from execution records to choose expected truth. Select expectations from the frozen cell manifest; cross-check actual treatment independently.

For every capture:
1. Parse event data strictly, reject duplicate keys/IDs, missing required fields and unknown schema versions. Validate sequence uniqueness and expected bootstrap origin. Contiguity is a consistency condition, not completeness proof.
2. Verify exact authority root, active flag and epoch. Verify parent-child grant lineage, owner, scope, delegation rights and ticket binding. Expected initial epoch is 7; a valid fence transitions it to 8 and inactive. These are fixture conventions, not generalized provider guarantees.
3. Match each `receipt` to exactly one result by request ID and transaction ordering. Gateway uses one serialized transaction per request; require receipt then its corresponding terminal with no unrelated interleaving. A missing terminal is incomplete, not a denied attempt.
4. Count execute receipts by operation identity, plus all unexpected execute receipts. An effect count alone cannot detect replay or denied extra attempts. Fixed-scope uniqueness cannot stand in for unique attempt identity.
5. Require effect rows and `effect` events to be a bijection using `event_seq`. Check request attribution, payload, effect key, root and epoch. Also reject an effect event with no row or an orphan row.
6. For fenced continuation require exactly one matching `denied` result with reason `revoked`. Wrong grant, invalid ticket, bridge timeout, missing response or any other denial cannot satisfy this oracle.
7. Verify fence receipt against trusted ledger and authority transition. Existing gateway responses do not bind root/epoch/request as a provider certificate. Preserve one fixed scope / one outstanding request limitation.
8. Verify outcome against the table below and report both attempt disposition and effect existence. A bridge response can be uncertain while the ledger still proves an effect.

| Cells | Execute attempts | Revoked denials | Effect rows | Fence |
|---|---:|---:|---:|---|
| M1 TRY continuation, M2 WAIT continuation | 1 | 0 | 1 | absent in complete window |
| M3 TRY fenced, M4 WAIT fenced | 1 | 1 | 0 | committed before execute receipt |
| K1 live, no cancellation | 1 | 0 | 1 | absent in complete window |
| K2 fenced, no cancellation | 1 | 1 | 0 | committed before execute receipt |
| C1 cooperative, each mode | 0 | 0 | 0 | absent in complete window |
| C4 historical, each mode | 1 historical, 0 later | 0 | 1 preserved | absent in complete window |

The proposed exact zero-attempt C1 and no-later-attempt C4 schedules need freeze approval; protocol prose currently says no C1 attempt is required rather than strictly forbidding one. Do not impose this stricter design retrospectively.

## 3. Native oracle

Use the release-pinned native schema, not magic integers as semantic names. Verify exported enum mapping against that schema, not just the runner's own map. Decode protobuf integer IDs losslessly; reject truncated/coerced identifiers.

Bind Workflow ID + run ID + namespace (where present) + Activity ID + scheduled-event ID + started-event ID + attempt. Check terminal scheduled/started linkage, worker context linkage and exactly one ordinary Activity attempt. Reject Local Activities, extra schedules/starts, retries, continue-as-new or run substitution outside the frozen design. Account explicitly for event types that legitimately omit a started link; do not fabricate it.

Check effective mode, maximumAttempts=1, heartbeats and timeouts from independent source/config pins and relevant native options. Some options may not appear in history: absence of a history field is not proof of correct configuration.

Record separately:
- External client's cancel invocation and response.
- Workflow-side Activity promise resolution or rejection, exact decoded result/error and relevant cause chain.
- Activity's cancellation-observation record.
- Last Activity instrumentation point.
- Worker invocation settlement.
- Native Activity terminal event.
- Native Workflow status and result, including actual observation release.

These observations need not be identical. TRY_CANCEL promise rejection need not equal server-side Activity cancellation. Resolve only expected combinations listed in the separately qualified native mapping. Any unlisted tuple is unresolved and blocks freeze/measurement pending investigation. A terminal timeout or early Workflow closure is an invalid treatment for the proposed continuation comparison even if sink effects match. Worker settlement alone is not a native terminal event. Neither proves unrestricted code cessation.

## 4. Causal order and observation cut

Build a directed evidence graph. Accepted edges arise from ordered events within one trustworthy stream, explicit request/response correlation, receiver-acknowledged barriers, native event links and committed sink sequence. Wall clocks are diagnostics only. Reject graph cycles and incompatible identities. Infer `before`/`after` only from a path; if neither path exists, return unresolved even if timestamps appear ordered.

For M1–M4 require cancellation observed -> controller receives matching observation acknowledgment -> matching effect release -> Activity receives that release -> execute dispatch -> sink receipt. For M3/M4 additionally require committed fence -> controller receives fence receipt -> effect release. A controller send or marker filename alone is not a receiver acknowledgment; marker content must correlate to the exact case/cut. Request invocation and response are different anchors and must not be collapsed.

Primary-cut proposal, not implemented:
1. Predesignate `cut_id` and finite boundary; hold Workflow open in its shielded observation scope.
2. Collect native Activity terminal and Worker settlement as separate records. Establish no remaining authorized fixture dispatch at the cut, including bridge in-flight inventory; an idle snapshot alone is insufficient.
3. Coordinator requests a cut. Sink produces a consistent read snapshot with high-water sequence. Native observer exports a complete history prefix and Workflow-held status for the same run. Each reports its own capture boundary and acknowledges the cut. Preserve exact causal links and cut IDs.
4. Coordinator certifies a common stable interval only if relevant Activity/sink mutations are excluded throughout both captures. This is a coordinated quiescent cut, not an atomic snapshot across Temporal and SQLite. If stability is not established, report separate observation boundaries and unresolved cross-cut conclusions.
5. Persist the complete primary bundle and cut certificate before `observationRelease` and before Worker shutdown. Release and shutdown acknowledgments must causally follow certification. Final Workflow outcome is a later, separately labeled observation.
6. Preserve post-cut/cleanup ledger changes and histories separately; no rewriting of primary snapshots. Any unexpected primary-relevant post-cut change invalidates the claimed stable interval and triggers investigation.

Failure path: if settlement/terminal/cut acknowledgment is absent, preserve whatever exists with its actual boundary. Do not force a success-shaped cut, infer no effect from silence, or use cleanup-produced settlement as the treatment result. The current native runner and supervisor cannot satisfy this certification without future authorized design/implementation work.

Ordering category precedence: require complete evidence before absence claims. If effect absent with complete bounded evidence, return `not_applicable_no_effect`; if effect present and fence absent with complete evidence, return `no_fence_in_complete_window`; if both present, derive order; otherwise unresolved. Use analogous distinct `no_request` and `no_observation` categories. An observed effect can still be reported present with incomplete evidence, but not as exactly one total effect.

## 5. Caller support and baseline

Derive views from one immutable bundle, not new runs. View A includes permitted envelope; View B removes only the entire envelope. Both retain the same frozen underlying records. Check filename, metadata, case-label and duplicate-field leakage against exact allowlists. A neutral case ID must not reveal expected treatment.

The privileged oracle and view-local support checker are separate interfaces. A caller assertion needs qualifying evidence reachable within its own allowlist and consistent with its scope. It receives no credit for guessing a hidden true fact. Evidence hashes/refs outside the view do not make hidden bytes visible. Sink fields cannot appear in a view lacking authorized sink evidence. Baseline and proposed projection have identical evidence access and review budget. Matching conclusions are a valid negative finding about incremental packaging value.

## 6. Deterministic fixture suite plan

All planned fixtures below are authored synthetic records, not results. Their native mapping is explicitly provisional until qualification; fixtures can test rule logic without qualifying Temporal.

Positive bases: six measured-cell records plus C1 and C4 in both modes, with canonical identities, correlated event streams and complete cut certificates. Also prepare a legally incomplete fixture whose correct result is unresolved rather than pass. Pin fixture bytes and expected per-rule outputs independently of candidate summaries.

| ID | Mutation or paired fixture | Required result |
|---|---|---|
| F01 | Set both runner `ok` fields true but remove expected M1 effect | sink mismatch; no pass |
| F02 | Activity fails, Workflow catches, cleanup succeeds | unlisted mapping/unexpected outcome; no automatic pass |
| F03 | Fenced denial reason changed to invalid_ticket | fail revoked-denial oracle |
| F04 | Add second execute attempt with duplicate result, leaving one row | fail attempt count |
| F05 | Row removed but effect event retained, and converse | fail row/event bijection |
| F06 | Consistently remove effect row and event from M1 | fail frozen expected outcome, even internally consistent |
| F07 | Invent fence receipt without ledger transition | fail fence support |
| F08 | Rewrite matching fence records to occur after attempt | fail treatment order |
| F09 | Wrong root/epoch consistently changed across payload records | fail frozen binding; no authentication claim |
| F10 | Correct Activity ID but wrong run/scheduled/start identity | fail native linkage |
| F11 | Second attempt or second schedule with same Activity ID | fail one-attempt rule |
| F12 | Native timeout plus desired sink effect | invalid treatment, not pass |
| F13 | Early Workflow terminal before cut release | invalid lifecycle |
| F14 | Primary sink snapshot after Worker shutdown | uncertified cut, no primary absence conclusion |
| F15 | Missing cut acknowledgment or incomplete native pagination | unresolved completeness |
| F16 | Add effect only during cleanup | preserve primary boundary; flag inconsistent stable-cut claim |
| F17 | Reverse wall clocks but preserve causal edges | same supported ordering |
| F18 | Favorable timestamps but remove causal link | unresolved order |
| F19 | Duplicate event IDs, fractional/coerced IDs, graph cycle | structural conflict; no pass |
| F20 | Cancellation response present, Activity observation missing | no delivered/observed-cancellation assertion |
| F21 | Final Activity log present, Worker/native terminal absent | only last-instrumented-point support |
| F22 | No effect with complete window; remove completeness certificate | absent -> unresolved |
| F23 | Hidden sink proves assertion, caller allowlist omits sink | unsupported caller assertion |
| F24 | Envelope removed, equivalent underlying records retained | baseline reconstructs same supported answer |
| F25 | Envelope copied into another visible file or revealing case label | view leakage, comparison invalid |
| F26 | Single unknown native outcome tuple | unresolved, never broad acceptance |
| F27 | C4 prior effect retained after cancellation | present/before request; no rollback assertion |
| F28 | Missing bridge response but committed ledger effect | effect present; transport outcome separately uncertain |
| F29 | Cleanup clean but collection truncated | cleanup success cannot upgrade evidence |
| F30 | Reorder unrelated independent events | verdict unchanged where causal constraints remain valid |

Add multi-record consistent mutations rather than only corrupting one byte. Test missing versus contradictory evidence separately. Ensure each negative fixture fails its intended rule, not merely a checksum gate; a fresh synthetic manifest can authorize changed bytes while the semantic oracle must still catch the defect. Hold original-manifest tampering tests as a distinct provenance group. Report fixture denominator separately from case denominator.

## 7. Freeze and stopping conditions

This design is complete when reviewed; it is not a request to execute. Before implementation or qualification: select controlling protocol/schema, resolve C1/C4 schedule precision, approve a cut design, review independent parser/oracle and authorize only the necessary next work. Before measurement: qualify transport/lifecycle, pin exact native mapping, pass positive/negative checker fixtures, verify equal view evidence and freeze all source artifacts.

Current blockers: native qualification not run; exact native mapping unknown; current primary-cut evidence insufficient; transport correction/rerun previously denied and remains unexecuted; no change to those restrictions is inferred from this draft. Source/design work remains separate and does not route around the denial.

No result supports comparative reliability, human review efficiency, novelty or stronger stopping guarantees. If ordinary WAIT plus the same source-linked sink lookup supports the same answer, preserve that negative result and stop expansion unless a concrete additional integration check is justified.
