# Proposed Temporal interface design

Date: 2026-11-03 UTC  
Research owner: Mark Julius Banasihan  
Status: reviewed design package. No implementation, lifecycle qualification or Temporal experiment has been executed for this protocol.

## Decision and scope

Preserve the reviewed design and its correction history for a subsequent qualification decision. The active execution-grounded revocation study and its historical results remain unchanged. The proposed comparison concerns native Activity cancellation observations and a separate protected local sink's authority fence. Controller-installed fencing must retain its own attribution.

The recommended measured scope is six cells: C2 and C3 across two native modes, plus two sink controls. C1 and C4 remain proposed qualification coverage. The strong baseline includes WAIT_CANCELLATION_COMPLETED, the actual native outcome and a separate sink lookup with equal evidence access. The proposed application projection concerns deterministic support for status assertions. No human review-time, decision-quality or productivity benefit has been demonstrated.

## Preserved design evidence

- [Current protocol draft](../review/TEMPORAL_INTERFACE_PROTOCOL_DRAFT_20261103.md)
- [Proposed status and evidence contract](../review/TEMPORAL_STATUS_EVIDENCE_CONTRACT_v01.md)
- [Design changes and preservation limits](../review/TEMPORAL_INTERFACE_DESIGN_CHANGELOG_20261103.md)
- [Complete design archive, including two predecessor snapshots](../../archives/temporal_interface_design_20261103.zip)

Readable copies preserve the source bytes. Their internal filenames refer to the extracted package layout. The archive contains five design files and their original checksum manifest; all five entries verified at preservation. Its SHA-256 is `c60413cf61dd6bb8715782e5c240673e39fa733667661636b7ebf821046db261`.

The earliest working drafts were edited before immutable copies existed. The changelog records their defects and corrections; byte-complete early drafting history is unavailable. The preserved protocol v02 and earlier status-contract snapshot retain the available predecessors.

## Review and unresolved gates

Separate AI-assisted design review prompted explicit no-fence/no-effect states, distinctions among last instrumentation, worker settlement and native terminal records, and a precise completion-envelope boundary. Coordinated fixture consistency checks provide no authentication guarantee. Later corrections distinguish equally available evidence presented differently from genuinely unavailable evidence. The final conceptual review reports those corrections present. This is design review, with no independent human validation or runtime result.

The source contract was inspected at TypeScript SDK v1.25.0 commit `efafd16ef4533da24029277bd72caf564c7aa007`. This pins a declaration and its comments. Server/CLI, Node, complete package resolution, SDK/Core behavior, lifecycle mechanics, outcome mapping and envelope freeze remain open. Historical archive materialization and verification are also prerequisites to any reuse. A source declaration alone establishes no implementation conformance.

## Contribution and next decision

The [prior-art comparison](2026-11-03-prior-art-and-future-interface-comparison.md) records existing work on authority, recovery and root-scoped quiescence. A possible contribution remains a bounded integration or status-adapter exercise. Native cooperative cancellation and local effect fencing have different contracts; no vendor defect or new general principle is claimed.

A qualification decision must specify the exact runtime, lifecycle gates, assertion schema, evidence access, strong baseline and criteria for stopping. No execution permission is created by preserving this draft. [Workbook v0.9](../traceability/Revocation_AI_Use_and_Research_Decision_Traceability_v0.9.xlsx) records the proposed design and presentation corrections. Earlier workbook v0.8 remains unchanged. Public release, website changes and external sharing retain their separate approval boundaries.
