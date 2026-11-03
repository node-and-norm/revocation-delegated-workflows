# Native cancellation and local authority fencing

Status: design draft, 3 November 2026. No Temporal implementation or experiment has been performed for this protocol. Execution requires an independently reviewed and version-pinned protocol. Research lead: Mark Julius Banasihan.

## 1. Research question

Which observations from a native Temporal Activity cancellation interface justify a caller's statements about Activity completion, and which additional observations justify a statement that one protected local sink rejects a withdrawn authority?

The study concerns correspondence between a documented native interface and a deliberately narrow local effect contract. It does not evaluate autonomous-model behavior, cognition, production reliability, global cessation, or institutional effectiveness.

## 2. Existing foundation and reuse boundary

The preceding Node & Norm request-to-fence study used a synthetic withdrawal caller, one fixed authority, and an atomic local sink. Its saved report describes twelve fixed direct/framework cases, source qualification, and a same-host reproduction. The private repository README and decision notes were read through its authenticated browser view on 3 November 2026 at approximately 23:39 UTC. The visible main head was bb7ca40, consistent with the supplied full identifier bb7ca4083c33bd7f8768309df445fbac0b8d261a. The prior-art note was last changed at d0c4e9524a42386593d9d6c68c12e7866daaa5f8; the completed-study decision at 0e2a442bfd61471e4af0b8d78c98366981e8822d. The archive itself has not been downloaded or hash-verified in this workspace. Before implementation, materialize the canonical repository archive, verify its published hash, inspect its enforcement contract and preserve its bytes unchanged. Any adapter changes need a new version and a record of the reason. The existing decision explicitly limits request correlation to one fixed scope and one outstanding request: its underlying gateway does not validate request root/epoch fields or echo the request identifier. Preserve that limitation; a fixture-generated receipt is not a cryptographically bound provider certificate.

Temporal cancellation is a separate operation from installing that sink's authority fence. The experiment must keep both events independently visible. A controller-installed fence must be attributed to the controller. No automatic linkage between cancellation and fencing is assumed.

## 3. Primary-source contract

The current TypeScript API defines TRY_CANCEL as reporting cancellation to the calling Workflow without waiting for assurance of delivery to the Activity. WAIT_CANCELLATION_COMPLETED is the strong comparison: it waits for the Activity's final execution state. That final state can be success, failure, or cancellation. Activity heartbeats enable cancellation notification. These are cooperative-cancellation semantics.

The caller in the ActivityCancellationType documentation is the Workflow, not necessarily the external client invoking WorkflowHandle.cancel(). These two observation boundaries receive separate fields throughout this study.

Sources inspected 3 November 2026:
- https://typescript.temporal.io/api/namespaces/common#activitycancellationtype
- https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination
- https://typescript.temporal.io/api/classes/testing.TestWorkflowEnvironment#createLocal

At freeze, record the exact SDK, CLI/server, Node and OS versions; save documentation snapshots or commit-pinned source references, package lock/integrity values, download hashes, and license notices. A live documentation URL alone is insufficient to identify the evaluated contract.

## 4. Minimal architecture

One local Temporal server, one Worker, one Workflow and one ordinary heartbeating Activity. Use the full local test server, not time-skipping evidence for delivery or elapsed-time claims. One inert local sink stores an effect and authority epoch under a single transaction. No external service, credential, cloud account, language model, participant, or real communication is involved.

A separate controller exposes deterministic barriers to the Activity and installs the optional fence. The controller records orchestration facts. A sink ledger records authoritative effect/fence ordering. Temporal history records native events. An external client records its actual cancel response and eventual Workflow result. The Activity records cancellation observation and its own attempt/final-instrumented events. All records include stable, explicit correlation IDs.

The controller can inspect privileged records to schedule releases. The evaluated caller cannot. Each caller status must identify the exact observation that caused its transition. This is a trusted-process information-boundary design; it is not a security-isolation claim.

### Workflow lifecycle control

Keep the Workflow alive through a separately recorded observation-complete release in both native modes. The release belongs to test orchestration and conveys no privileged sink facts to the evaluated caller. Qualification must establish the exact pinned SDK mechanism for a cancellation-shielded observation/cleanup scope, including timeout behavior. Workflow termination is excluded from the measured treatment. Early Workflow closure can alter cancellation delivery and therefore invalidates a case intended to compare the Activity modes. Record Activity call settlement separately from the Activity’s last instrumented event and eventual Workflow closure. Until this lifecycle is qualified, the matrix is a design proposal.

## 5. Fixed factors and proposed matrix

Two native modes: TRY_CANCEL and WAIT_CANCELLATION_COMPLETED. For each mode run these four schedules in fresh Workflow, server namespace or task queue, and sink state:

| Schedule | Controlled ordering | Fence | Expected sink fact | Native interpretation target |
|---|---|---|---|---|
| C1 cooperative | Activity is ready; request cancellation; Activity observes cancellation before effect release and exits cooperatively | Absent | Zero effects; no sink attempt required | Compare Workflow-side reported cancellation with worker-side settlement and native terminal history |
| C2 bounded noncooperative | Activity is ready; cancellation observed; Activity deliberately continues once, attempts inert effect, then exits | Absent | Exactly one permitted effect | Reporting cancellation alone does not establish absence of an effect; waiting observes the final state according to pinned SDK behavior |
| C3 fenced continuation | Same bounded continuation as C2; fence commits before effect barrier release | Present | Exactly one denied attempt and zero effects | Separate native final state from independently enforced sink protection |
| C4 historical effect | Effect commits; then cancellation request is accepted; Activity terminates under the controlled contract | Absent | Exactly one earlier effect, preserved | Cancellation/completion must not erase history or imply rollback |

The table defines eight qualification cells. The recommended measured target is C2/C3 across the two native modes, plus two mode-independent sink controls: live authorized effect without cancellation (one effect), and preinstalled fence without cancellation (one denied attempt, zero effects). Six proposed measured cells; C1 remains a cancellation-delivery qualification and C4 a historical-effect qualification. Preserve all ten qualification outcomes separately. Do not count these deliberately selected cells as independent statistical samples. Advancing C4 into measured collection requires an explicit reason recorded before freeze.

C2/C3 use a fixed, bounded continuation to represent software that receives cancellation but completes an already prepared action. They are controlled behavior, not a discovered defect, sabotage, or an autonomous model decision. C1 verifies that cancellation can work in this setup. C4 establishes a history distinction and does not measure rollback.

The exact native exception/result mapping remains a qualification question. Do not invent an expected TypeScript error type from documentation shorthand. Before freeze, inspect the pinned SDK sources and run a separately labeled qualification to specify expected Workflow-side outcomes. A discrepancy must be investigated before measurement.

## 6. Ordering and observation

Required events: Activity started/ready; external cancel invocation/response; Workflow cancellation observation; Activity cancellation observation; Activity call settled in Workflow; Activity last instrumented event and worker-side invocation settlement; fence committed; effect attempted and committed/denied; Workflow terminal event; observation end.

No cross-process wall-clock subtraction establishes authoritative order. Establish order through explicit causal barriers, request/response links, Temporal history sequence, and the sink transaction sequence. Preserve wall clocks as diagnostics only. A controller send is not receiver receipt. Heartbeat emission is not proof cancellation was observed.

A local effect cannot be inferred solely from an Activity return value. A terminal Workflow state cannot be inferred solely from cancel() returning. An Activity call rejected in a Workflow cannot by itself establish Activity code cessation under TRY_CANCEL.

Operationally, a final Activity log proves only that the instrumented point was reached. Record worker-side invocation settlement and the server’s terminal Activity history event separately; neither a final log nor Workflow-side cancellation rejection is renamed “code stopped.” Any claim of execution cessation needs its explicitly scoped observable and its residual limitations.

Use a declared finite observation window and record timeout as unresolved. No inference of cessation from silence. Capture cleanup after the observation cut separately. The test must ensure cleanup cannot contaminate primary results; never treat final cleanup as proof that the intended cancellation path succeeded.

## 7. Caller classifications and strong baseline

Maintain separate fields:
- Request: not_requested / response_received / error / unresolved.
- Activity: running_observed / final_state_supported / unresolved, with exact supported final state and evidence.
- Workflow: its actual terminal status or unresolved.
- Local authority: fence_confirmed / unresolved, identified by an authorized fence receipt, never inferred from cancellation alone.
- Effect existence: present / absent_with_complete_bounded_evidence / unresolved.
- Fence existence within the observation window: present / absent_with_complete_bounded_evidence / unresolved.
- Effect order relative to the fence: before / after / not_applicable_no_effect / not_applicable_no_fence / unresolved.
- Effect order relative to cancellation request and Activity cancellation observation: before / after / not_applicable_no_effect / not_applicable_no_event / unresolved, with each anchor recorded separately.

These orthogonal fields can represent an authorized effect after a cancellation observation without any fence, as well as a prior effect with no subsequent fence. A single before-fence/after-fence enum would misclassify those histories.

The strong native baseline includes WAIT_CANCELLATION_COMPLETED, the actual native outcome, and an ordinary separate sink-status lookup with the same evidence budget as any proposed adapter. An adapter receives no extra hidden facts simply because it has a richer response schema.

For evidence delivery, derive two explicitly labeled caller views from each eligible case: the complete permitted response and the same view with exactly one named application-facing completion envelope withheld. These are controlled evidence projections from one run, not additional executions or natural network-loss observations. This envelope is a proposed adapter record, not the client cancel response, native Activity terminal event, Workflow result or sink-fence receipt. Before freeze, define its schema and source-event mapping, the exact field or message removed and establish that no duplicate field or revealing case name leaks it. The ordinary baseline and adapter receive identical projections. Evaluate which status distinctions each preserves. A later dedicated transport test would require its own scope.

A conservative reference classifier uses only supplied evidence and returns unresolved when the required observation is missing. It is the baseline for any richer status projection. Never manufacture an 'accepted means done' product baseline. Missing facts are not failures of the native interface unless that interface explicitly promises them.

The privileged adjudicator may access all source records; it scores both actual history and the strongest conclusion justified to the caller. A lucky hidden-truth guess receives no credit.

## 8. Qualification and freeze gates

1. Independently review this design and the exact normative contract.
2. Pin versions and verify local runtime feasibility and license/redistribution terms.
3. Validate cancellation delivery/observation and exact native outcome mapping in separately labeled development runs.
4. Verify live and fenced controls; ensure retries are disabled or limited to one attempt and record all effective options. No automatic retry can create uncounted effects.
5. Validate barriers, IDs, caller evidence isolation, all failure-path record preservation and finite cleanup.
6. Independently implement or review the checker; it must inspect actual Temporal history and sink SQLite, not merely runner summaries.
7. Reject mutations: false completion receipt, wrong identity, missing effect, invented fence, effect reordered after fence, wrong authority epoch, truncated history, and caller statement unsupported by its visible evidence. Mutate related records consistently to test semantics beyond snapshot equality. Wrong-root/epoch and false-receipt controls test consistency against trusted fixture records. They do not establish authentication or provider-side validation absent from the historical gateway. Keep checker detection, fixture provenance and actual gateway enforcement separate.
8. Freeze code, dependencies, protocol, expected cell outcomes, checker and tests before measured collection. Preserve earlier defects and corrections.

Stop when a required contract remains ambiguous, a valid control fails, records are incomplete, or the caller receives privileged information. Report the blocker and preserve evidence. Changes after freeze require a new version and a clearly labeled new collection.

## 9. Outcomes and interpretation

Primary output is a case-level conformance table with source-backed claims, unsupported caller claims, expected effects/denials, timing classification and unresolved states. Report denominators and actual case identities. Do not report a statistical reliability rate from six designed measured cells. Count assertion/mutation tests as instrument checks rather than extra system observations.

The experiment can establish a bounded correspondence between a selected native API mode, the caller's evidence and a local effect contract. It cannot establish realistic incident frequency, distributed closure, arbitrary descendant stopping, or comparative model capability. Shared sink code limits independent enforcement comparison. Same-host execution limits portability claims.

## 10. Prior art and utility gate

Permission to Retry already evaluates authorization, effects, recovery and partial observations on native LangGraph and Temporal hosts: https://arxiv.org/html/2610.31916v1 . Root-scoped quiescence already separates accepted cancellation, sink fencing and broader closure evidence: https://arxiv.org/html/2609.21284v1 . Neither conceptual distinction is proposed as new here.

The provisional contribution is a small inspectable native-interface correspondence test with explicit caller-level evidence. Before expanding, establish whether it helps an engineer avoid a concrete unsupported status claim or verify an integration boundary beyond merely restating API documentation. A competent conservative classifier performing equally well may be the sufficient result. No novelty-oriented claim follows from adding Temporal.

## 11. Documentation and AI disclosure

Preserve source snapshots, qualification failures, corrections, all measured records, actual commands, runtime manifests, hashes, checker outputs and independent review. Record what AI produced and what was manually adjudicated. Separate AI-assisted review from human validation. Retain original workbook publisher-guidance access dates and check the chosen venue's current requirements before submission.

This draft was prepared with AI assistance from inspected official documentation and historical project context. Exact existing artifact reuse remains pending materialization. The draft is not frozen, implemented, tested, human-reviewed, or submitted. Separate AI-assisted design review is in progress; The independent AI-assisted artifact review identified four design defects before implementation: an incomplete history enum, overstrong code-termination wording, unclear receipt withholding, and an authentication implication in mutation checks. This revision addresses them and reduces the proposed measured target to six cells. Reviewer findings and any further revisions must be preserved before an implementation decision.

## 12. Repository source locators

- https://github.com/node-and-norm/revocation-delegated-workflows/blob/main/docs/decisions/2026-11-03-prior-art-and-future-interface-comparison.md
- https://github.com/node-and-norm/revocation-delegated-workflows/blob/main/docs/decisions/2026-11-03-request-to-fence-interface-study.md

These are private repository references, read in the authenticated browser. Inspection of a rendered decision note verifies its contents; it does not independently validate its historical measurements. Exact archived code reuse remains pending byte-level materialization and review.

## 13. Pinned declaration and concrete projection

STATUS_EVIDENCE_CONTRACT_v01.md supplies the inspected v1.25.0 source declaration pin, proposed envelope, exact derived-view intervention, six-cell matrix and checker obligations. Its view definition resolves the earlier draft's still-open withheld-message description. The runtime remains unpinned; source inspection is not execution conformance. PROTOCOL_REVIEWED_DRAFT_v02.md preserves the preceding corrected draft.

The final evidence-view definition preserves underlying records and changes packaging only. It therefore supersedes the earlier missing-receipt interpretation. The declared question remains native status/sink correspondence; the derivative check measures assertion support, with no review-time or reviewer-performance inference.
