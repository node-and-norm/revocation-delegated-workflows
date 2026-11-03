# Design record, 3 November 2026

Research owner: Mark Julius Banasihan. This file records protocol preparation, not experimental execution.

## Initial design

Prepared a ten-cell candidate: eight native-mode/schedule combinations and two sink controls. The design distinguishes client cancellation response, Workflow-side Activity settlement, Activity process behavior, sink effect/fence ordering and eventual Workflow closure.

## Source checks

Read the current official Temporal TypeScript cancellation-mode contract and cancellation/termination documentation. Read closest prior-work papers as source evidence. Read the private repository's current README, prior-art decision and completed request-to-fence decision through the authenticated browser. Its visible head was bb7ca40. The archive has not been materialized or byte-verified in this workspace.

## Review-informed corrections before freeze

1. Added an explicit Workflow lifecycle qualification gate. An early Workflow close can itself change cancellation delivery, confounding the intended native-mode comparison.
2. Made the strong baseline WAIT_CANCELLATION_COMPLETED plus actual native outcome and a separate sink lookup with identical evidence access.
3. Separated controlled withholding of caller completion evidence from actual transport failure. Derived views are not additional experimental runs.
4. Preserved the existing gateway's fixed-scope correlation limit: it does not validate root/epoch request fields or echo request IDs.
5. Kept exact Activity exception/result mapping unresolved until pinned source inspection and separately approved qualification.

## Open design decision

The ten-cell matrix may be larger than the smallest useful status-adapter exercise. Independent AI-assisted review is assessing whether to reduce it and whether an ordinary conservative projection plus sink lookup already supplies the useful result. No claim of added research utility has passed this gate.

## Execution boundary

No SDK installation, implementation, qualification run, experiment, repository edit, publication, live model call or external communication was performed for this draft. Parent approval of a reviewed scope is needed before advancing beyond design.

## Independent artifact review and revision

The separate AI-assisted reviewer read the actual draft and found four issues: the original history enum could not represent effects when no fence existed; a final Activity log did not prove code termination; fixture mutations risked implying absent authentication guarantees; and the withheld completion receipt was ambiguous. The revised draft separates existence and ordering fields, distinguishes last instrumentation/worker settlement/server terminal history, labels mutation checks as trusted-fixture consistency, and defines the withheld object as a proposed application-facing envelope requiring a frozen schema.

The recommended measured scope is reduced to C2/C3 across both modes plus two sink controls, six cells. C1 and C4 remain qualification coverage. Exact source pins, lifecycle mechanics, envelope schema and qualified outcome mapping remain prerequisites. This is a reviewed design revision, not approval to run.

## Source-pinned contract

Inspected official v1.25.0 source declaration at efafd16ef4533da24029277bd72caf564c7aa007 through the cloud browser. Cached raw-main default text differed; the pinned source agreed with current API documentation. Explicit modes avoid reliance on defaults. Added a separate proposed status/evidence contract with six-cell expectations, evidence-view definitions and checker obligations.

## Preservation limitation

The earliest working drafts were revised in place before immutable local copies were created. Their defects and revisions are documented here, but no claim of byte-complete preservation of those early drafting versions is made. PROTOCOL_REVIEWED_DRAFT_v02.md preserves the corrected six-cell protocol before the later source-pin addendum. Subsequent revisions must retain their predecessors.

## Final narrow review

The reviewer identified a shift from unavailable completion evidence to differently packaged but equally available evidence. The contract now labels that intervention explicitly and confines its output to deterministic assertion support. It establishes no human review-time or decision-quality benefit. Added not_applicable_no_effect to ordering fields so denied cases are representable. The prior contract version is preserved as STATUS_EVIDENCE_CONTRACT_v01_reviewed_snapshot.md. The reviewed design remains unexecuted.
