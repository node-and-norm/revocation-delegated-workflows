# Consolidated proposed Temporal checker specification v0.2

4 November 2026 UTC. AI-assisted methods specification, not implementation, executed test, qualified instrument or measured result. No denied socket operation, candidate patch or alternative execution route was attempted. This specification does not authorize those actions. The historical gateway remains unchanged.

## Provenance and controlling scope

Reviewed merged commit `5ceceb4b0f30e8c0608b641d71785a6ce2317c8a` through the GitHub connector. Controlling reconciliation: `docs/research-records/v0.1/sources/reconciliation.md`, Git blob `d551cd58ba5309c12b95b102abfd3adb7a5c9ea5`. URL: https://github.com/node-and-norm/revocation-delegated-workflows/blob/5ceceb4b0f30e8c0608b641d71785a6ce2317c8a/docs/research-records/v0.1/sources/reconciliation.md . [`SOURCE_RECONCILIATION.md`](../temporal_checker_spec_20261104/SOURCE_RECONCILIATION.md) is a locally reconstructed text copy for reading, not a byte-identical repository export.

Local source files in `temporal_qualification_20261104/source/` were rehashed and matched the reconciliation's native_runner, supervisor, bridge, workflows and gateway hashes. Earlier source analysis is preserved in `temporal_methods_review_20261104.md`. The contract remains `temporal_protocol_20261103/STATUS_EVIDENCE_CONTRACT_v01.md`; no new native outcome mapping is inferred here.

## Cross-review and preservation

This new document consolidates the [original acceptance specification](../temporal_checker_spec_20261104/CHECKER_ACCEPTANCE_SPEC.md) and [independent checker design](../temporal_checker_design_20261104/INDEPENDENT_CHECKER_DESIGN.md), plus their exchanged AI-assisted reviews on 4 November 2026. The designer’s [cross-review](../temporal_checker_design_20261104/CROSS_REVIEW.md) and [erratum](../temporal_checker_design_20261104/ERRATA_v01.md) were read and incorporated. Merged-commit retrieval was performed by the acceptance-spec reviewer; the designer’s historical provenance is not represented as an independent current-commit verification. Both originals remain unchanged and are identified in SOURCE_PROVENANCE.json. This is a proposed successor for review, not a frozen replacement or human-approved protocol. Scope is documentation only. Case expectations below are proposed fixture semantics, never retrospective claims about execution.

Changes: case-conditional treatment rules; explicit C1/C4 freeze decisions; identity-mutation versus valid synthetic renaming; measured inclusion independent of assertion correctness; stronger capture stability; explicit cleanup gate; bounded interpretation of post-cut changes; lossless native identifiers; pagination/completeness evidence; schema migration; semantic-versus-provenance mutation groups.

## Independence and inputs

The checker consumes immutable saved artifacts, never drives the Worker, bridge, gateway or controller, and never uses `ok`, exit zero or summary prose as an oracle. It recomputes findings from raw exported Temporal history, instrumented events, bridge records, the captured SQLite database, effective configuration, source/runtime manifest, protocol version, caller-view allowlist and cut manifest. Local records are trusted fixture evidence, not authenticated provider certificates. A matching hash proves identity of bytes only.

Decode native integer identifiers losslessly and validate enum meanings against the pinned native schema, not merely a runner-generated mapping. Require a declared complete history prefix with pagination/completeness evidence and final included event ID; contiguous event IDs alone do not prove completeness. Parse source records under declared versions. Freeze one vocabulary for no-effect/no-fence/no-request/no-observation and explicit version migrations; do not silently normalize ambiguous absence.

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

Measured-case inclusion is a distinct, predeclared decision based on valid treatment and evidence adequate for the target analysis, never on whether the proposed method made correct assertions or achieved a favorable outcome. Unsupported assertions and adverse sink/native facts are scored outcomes, not automatic exclusion reasons. If instrument validity is compromised, retain the attempted case and exact reason under predeclared invalid/unresolved rules; never silently drop it. An expected unsupported assertion in a synthetic negative fixture means the checker passes that fixture if it correctly detects it. Do not require a fixture's input claims all to be supported. Retain the denominator of all attempted cases, analysis-eligible cases, invalid cases and unresolved cases separately.

## Acceptance rules

A01 Identity: validate the applicable case mode and behavior against explicit allowlists. Match operation ID, authority scope, capture ID and protocol/runtime versions. For native cells also match Workflow ID/run ID, Activity ID, scheduled event, start event and attempt; sink-only controls do not acquire invented native identities. The frozen manifest declares applicability rather than treating missing native fields in sink-only controls as failures. A case label cannot override raw evidence. Use the correct scheduled/start reference fields present in the pinned event schema; do not invent absent fields.

A02 Native lifecycle applies only to native cells, not sink-only K controls: require one ordinary Activity schedule/start/terminal chain and attempt 1 for eligible native cases, matching effective options. Explicitly check retry policy, timeout and cancellation mode. Record both Workflow promise settlement and actual server disposition. The expected mode/behavior tuple remains a reviewed qualification output; until defined, record the actual tuple but do not accept a guessed mapping.

A03 Treatment is case-conditional. M1–M4 require positive Activity-start and cancellation-observation evidence, not heartbeat emission alone, followed by the correlated continuation release, receiver observation, dispatch and execute receipt. M3/M4 additionally require revocation commit and receipt before release and execute. C1 requires started Activity and observed cancellation followed by the separately frozen cooperative outcome; its exact execute-attempt rule remains an unresolved decision. K1/K2 are no-cancellation sink controls: do not require cancellation observation or a cancellable Workflow lifecycle unless their frozen architecture explicitly includes one; require positive setup and complete evidence of no cancellation within the declared window. C4 requires effect commit before the cancellation-request anchor and preservation afterward; it must not inherit M1–M4's post-observation continuation rule. C4 later-attempt and native-outcome details remain unresolved. For native cases that use the observation hold, reject early Workflow closure, hold timeout and mismatched release. Freeze exact request-invocation versus request-response anchors. Baseline and proposed projection receive the same intended schedule and evidence budget.

A04 Authorization setup: inspect bootstrap, grant and admission records and their ordering before the protected attempt. Validate the fixed actor, grant, ticket, scope, root and epoch according to the unchanged gateway contract. A denial caused by wrong ticket, wrong actor or invalid grant is not a successful revoked-authority control. The known fixed-root/epoch and single-outstanding-operation limits remain explicit.

A05 Sink accounting: count execute `receipt` events, not all gateway receipts. Require each committed receipt to have exactly one corresponding terminal result, with no unrelated interleaving inside the gateway transaction, and validate result-to-receipt linkage as well. Link each execute to its terminal result through request ID and transaction/event ordering under the fixture's single-operation assumption. Inspect effects separately and require a bijection between effects rows and effect events using `effects.event_seq`; check both directions. Compare payload/scope/root/epoch and reject orphan, duplicated or inconsistent rows. A summary count of one is insufficient.

A06 Proposed sink expectations, not established results: M1/M2 unfenced continuation proposes exactly one execute attempt and matching effect; M3/M4 fenced continuation proposes exactly one attempt, exact revoked denial, zero effects and preceding revocation. K1 requires exactly one execute attempt and one matching effect, with no fence or cancellation in the declared complete window. K2 requires exactly one execute attempt, one exact revoked denial and zero effects, with a committed fence before execute and no cancellation in the declared complete window. Both require their own control identity, valid authorization setup and observed records; prior Q2 records cannot be renamed measured cells. C1 proposes zero effects, while an exact zero-attempt requirement is a stricter proposed schedule awaiting approval and freeze because current prose says an attempt is not required rather than expressly forbidden. C4 proposes preservation of one pre-request effect; the proposed zero-later-attempt requirement and complete coverage must be decided and frozen separately. Pending decisions produce unresolved applicability/mapping, not retrospective failures of historical records. No current case qualifies through these prose expectations alone.

A07 Ordering: use sink event sequences within the committed ledger and linked causal barriers across processes. Distinguish no effect, no fence, no cancellation request, and unresolved. Wall-clock proximity does not establish causality. Detect cycles or contradictory order relations; do not resolve them using timestamps.

A08 Cut: the proposed primary native cut occurs while Workflow is held, before observationRelease and before Worker cleanup. Collect native Activity terminal and Worker settlement separately, and account for all relevant in-flight dispatches. Require evidence of a stable interval across captures, not just matching cut IDs/acknowledgments. Bind each source to its boundary (Temporal event ID, ledger sequence, instrumentation position); do not imply simultaneous global atomicity. Capture all SQLite tables within one explicit read transaction. Persist the primary bundle/certificate, then release Workflow; final Workflow outcome is necessarily later and separately scoped. The same cut contract must specify what applies to mode-independent sink controls. If stability or a required boundary is unproved, preserve separate source boundaries and return unresolved for cross-cut and completeness conclusions. Failure paths need not manufacture a success-shaped cut. Post-cut changes trigger investigation and may contradict a no-outstanding-work claim, but do not alone prove mutation during the earlier bounded capture interval. Invalidate that interval only with evidence contradicting its defined stability claim. Cleanup records cannot retroactively complete primary evidence. The offline checker validates saved capture records under trusted-fixture assumptions; it cannot detect every omitted commit, fabricated certificate or dishonest producer. A late effect from the same previously pending dispatch may contradict a no-pending-work certificate; a separate newly authorized operation after the interval does not retroactively falsify it.

A09 Cleanup: preserve initial error, uncertain dispatch, shutdown errors and forced termination separately. Missing capture acknowledgment, Worker shutdown error, nonzero child exit or forced cleanup prevents an overall qualification pass under the current finite-cleanup plan. Never rewrite previously saved primary records. Hash/content differences between primary and cleanup are reported, not merged away.

A10 Caller support: classify each assertion using only the selected view's explicit file/field allowlist. Privileged checker access does not authorize caller access. Effect absence requires complete bounded sink evidence for that operation/cut. Missing receipt alone proves neither fence absence nor presence. Grade `fence` confirmation and `fence_existence` separately against their field-specific contract requirements: confirmation requires the current sink receipt cross-checked with the trusted ledger; qualifying permitted bounded sink evidence can support existence even when confirmation remains unresolved. Lack of receipt does not erase that independent evidence, and ledger-supported existence must not be upgraded to receipt-backed confirmation. Unknown native evidence means unresolved, not no effect. Unsupported positive assertions fail support grading even when hidden truth happens to agree. Keep the reference factual classification (for example unresolved fence state) separate from assertion support (a positive confirmation claim is unsupported). A correctly stated unresolved result is not an unsupported positive claim.

A11 Packaging comparison: View A includes the derived envelope; View B removes that envelope while retaining the same predeclared underlying evidence. Baseline and proposed projection have equal evidence and review budget. Source-linked reconstruction in View B may reproduce all conclusions and is a valid result. The intervention does not model actual loss of completion evidence or measure human efficiency. A revealing path/name or duplicate envelope must not leak a withheld object; legitimate reconstruction from permitted raw evidence is not leakage.

A12 Freeze: exact code, checker, test vectors, source/runtime versions, accepted native tuples, allowlists, case mapping and cut contract must be reviewed and frozen before measured collection. Unexpected qualification tuples trigger investigation and a versioned decision, not post-hoc alteration of measured expectations. Each measured case has an explicit inclusion/exclusion reason. A novel post-freeze native outcome must remain in the attempt record and be scored/investigated under the predeclared rules; stop collection when required, but never revise mappings or exclusion rules to erase an unfavorable observation. Any new mapping belongs to a new version that preserves the original result.

## Prospective test vectors, not executed tests

All vectors below are specifications. They may later be represented as synthetic saved artifacts, clearly marked synthetic. They do not count as native runs or observations. Correlated mutations must change related summaries and records consistently where possible, so tests exercise semantics rather than only stale hashes.

T01 Conditional proposed cooperative fixture: valid start/cancel observation, no execute/effect, reviewed native tuple, valid cut and normal cleanup -> required gates satisfied only after zero-attempt C1 is approved/frozen. Until then retain the unresolved schedule decision.
T02 Positive unfenced continuation fixture -> one linked effect, no fence in complete window, valid treatment.
T03 Positive fenced continuation fixture -> one exact revoked denial, zero effects, fence-before-attempt, valid treatment.
T04 Bridge failure caught by Workflow, completed Workflow and `ok:true` summaries, no effect -> no qualification acceptance despite zero exit.
T05 Fenced fixture with invalid-ticket denial and zero effects -> denial fact retained, intended treatment unsatisfied; not credited as fence protection.
T06 One effect in summary but missing actual effect row, or orphan effect_seq -> accounting unsatisfied.
T07 Duplicate execute receipt plus one effect and one duplicate outcome -> attempt-count gate unsatisfied even though effect count is one.
T08a Break linkage or violate the frozen case binding across request/run/attempt records, including internally consistent substitution incompatible with that binding -> linkage/binding unsatisfied. T08b Consistently rename opaque identifiers across a freshly authored synthetic fixture and its manifest without changing scope, causal links or frozen semantic bindings -> equivalent semantic verdict. Do not rename real native evidence or treat semantic equivalence as historical authenticity.
T09 Remove cancellation observation while retaining heartbeats -> causal treatment unobserved, not cooperative pass.
T10 Change behavior to misspelled continue_fenced value -> configuration rejected; no fallback to unfenced treatment.
T11 Missing/reversed revocation and release relation -> effect/fence facts retained where supported, intended fenced schedule unsatisfied or unobserved.
T12 Expected tuple undefined, or unexpected native failure with valid history -> tuple recorded, qualification unresolved/unsatisfied pending investigation, never invented pass.
T13 Effect appears only during Worker cleanup -> primary cut cannot borrow cleanup evidence; record separate phase-specific facts and investigate any no-outstanding-work claim. Do not infer the earlier capture interval itself was unstable without supporting evidence.
T14 Missing cut acknowledgment or mixed history/sink cuts -> primary completeness unobserved; no primary absence/cessation claim.
T15 Concurrent commit between table reads -> reject mixed snapshot; a transactional capture must retain a consistent pre- or post-commit state. This is a planned capture test, not a claimed checker ability to infer every undetectable race.
T16 Normal primary result followed by shutdown error -> primary facts retained, cleanup gate unsatisfied, overall acceptance blocked.
T17 Truncated history, duplicate JSON keys, or missing allowlist file -> completeness/parser gate fails closed.
T18 Hidden true fence with no permitted caller evidence -> privileged fence fact present; caller reference fence classification unresolved. A caller’s positive confirmation assertion is unsupported, while a correctly qualified unresolved report is not that unsupported claim.
T19 Remove derived envelope only, retain complete permitted raw evidence -> baseline may reconstruct the same conclusions; do not manufacture a benefit.
T20 Leak envelope contents through filename or alternate duplicate record -> view-isolation gate unsatisfied; legitimate raw-evidence reconstruction remains allowed.
T21 Conditional C4 fixture: effect before the declared request anchor remains in later ledger -> the same effect is present at the two observed cuts. Uninterrupted persistence or absence of every intervening mutation requires the complete ledger/boundary contract; do not infer it merely from two snapshots. Any exact no-later-attempt condition remains pending freeze.
T22 Relabel qualification record as measured K1 -> provenance/phase gate unsatisfied.

Keep original-manifest tampering tests separate from semantic mutations with freshly pinned synthetic manifests, so a semantic defect is not detected only by stale hashes. Record exact per-rule expected outputs and require each vector to reach its intended rule.

Metamorphic properties for later synthetic checker tests: removing supporting evidence cannot create a stronger supported claim; adding irrelevant files cannot improve support; permuting independent record serialization does not change causal conclusions; wrong claims cannot pass merely because hidden truth matches; cleanup evidence cannot repair an absent primary cut; consistently renamed opaque IDs preserve semantic conclusions only in newly authored synthetic fixtures where every scoped mapping and frozen semantic binding stays valid; real evidence identity/authenticity is not preserved by renaming. Exceptions such as newly detected contradiction must be represented explicitly rather than weakening these rules silently.

## Current status and next dependency

This specification closes no runtime gate. It makes the outstanding independent-checker obligations implementable and reviewable. Native mappings, capture instrumentation, transport mocks, C4 coverage and execution permission remain separate dependencies. The two earlier denials remain in force for the denied operation; there was no retry or route change in preparing this document. A future implementation should begin as a separately reviewed artifact-only checker, without importing or executing the gateway/Worker candidate.

## Additional nonredundant synthetic test requirements

T23 Reverse wall clocks while preserving causal edges -> same supported order.
T24 Favorable timestamps without a causal path -> unresolved order.
T25 Correct Activity ID with wrong run or schedule/start linkage -> invalid linkage, not an accepted native chain.
T26 Final instrumentation without Worker/native terminal -> only last-instrumented-point support.
T27 Missing bridge response with a committed ledger effect -> effect present; transport outcome independently uncertain.
T28 Fractional/coerced protobuf IDs or cyclic causal graph -> structural conflict, no acceptance.
T29 Complete no-effect finding with its completeness certificate removed -> reference absence becomes unresolved, not present.
T30 Invented fence receipt without trusted ledger transition -> unsupported fence confirmation.
T31 Unfavorable caller claim on otherwise valid evidence -> retain measured case and score unsupported assertion, never outcome-based exclusion.
T32 Novel native tuple after freeze -> preserve original outcome and apply predeclared investigation/stop rules; never rewrite mapping to remove it.

T33 K-control cardinality mutations: missing/extra execute, extra effect or extra denial must fail the declared K1/K2 oracle even if a summary claims control success.
T34 Missing fence receipt with permitted bounded ledger evidence of fence existence -> reference `fence_existence=present` may be supported, while receipt-backed `fence` confirmation remains unresolved. A caller assertion of receipt-backed confirmation is unsupported without its required receipt.

The independent design’s F01–F30 remain preserved as supplementary proposals, interpreted through its erratum and this consolidation. They are not additional empirical observations. Overlapping vectors must not inflate a case or test denominator.

## Case applicability matrix (proposed, not frozen)

| Family | Required causal facts | Inapplicable or unresolved requirements |
| --- | --- | --- |
| M1/M2 | Activity start; cancellation observed; correlated release received; one execute; native hold/cut/release | No fence in complete window; exact native tuple unresolved |
| M3/M4 | M1/M2 chain plus revocation commit/receipt before release and execute | Exact native tuple unresolved |
| K1 | Valid live authorization; exactly one execute attempt and one matching effect; no fence and no cancellation in complete window | Native lifecycle only if architecture includes it; no cancellation-observation requirement |
| K2 | Valid authorization before fence; revoke before execute; exactly one execute attempt, one revoked denial and zero effects; no cancellation in complete window | Native lifecycle only if architecture includes it |
| C1 | Activity start; cancellation observed; cooperative result; zero effects | Zero attempts is a proposed additional freeze decision |
| C4 | Historical effect before declared cancellation-request anchor; linked later observation | Later-attempt schedule, mapping and explicit coverage unresolved |

## Unresolved decision register

D01 Exact native mode/behavior tuples: requires permitted qualification, review and freeze; no mapping is asserted here.
D02 C1 precise attempt rule: zero attempts is proposed, not an existing retrospectively enforceable rule.
D03 C4 explicit qualification coverage, request anchor, later-attempt constraint and native mapping: proposed, not implemented.
D04 Cut architecture and certificate, stable-interval proof and sink-control applicability: proposed design, current candidate cannot satisfy it by filenames alone.
D05 Schema vocabulary/version migration and per-view file/field allowlists: must be frozen and reviewed.
D06 Analysis inclusion/exclusion and outcome scoring: must be predeclared without conditioning inclusion on favorable results or correct caller claims.
D07 Cleanup acceptance: current proposal requires normal finite cleanup for overall qualification; primary factual findings survive cleanup failure. Review this criterion before freeze.

## Review receipt

This artifact reconciles specification differences, not runtime behavior. No native test, transport mock or artifact-checker implementation has been executed. Source/hash/link checks are document-integrity work only. Remaining execution restrictions are unchanged. Designer CROSS_REVIEW.md and ERRATA_v01.md were incorporated. No claim of independent human validation or final designer endorsement of these consolidated bytes is made.

## Final source-review correction

The designer identified two remaining ambiguities on 4 November 2026: receipt-backed fence confirmation versus independently supported fence existence, and missing exact K1/K2 cardinalities. These were verified against STATUS_EVIDENCE_CONTRACT_v01.md lines 27–29 and 56–57,66–67, then corrected in A06, A10, the applicability matrix and proposed T33/T34. The prior consolidated version and its provenance/validation/checksums remain byte-preserved in `preserved_before_final_review/`. This is a specification correction only, not an experimental result.
