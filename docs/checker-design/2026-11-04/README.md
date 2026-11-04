# Proposed Temporal checker design record

4 November 2026 UTC. Private, AI-assisted design and source review only. Native qualification remains blocked; no checker implementation, fixture execution, transport mock, native Workflow/Activity experiment or denied-operation retry is part of this package.

## Reading order

1. [Consolidated proposed specification v0.2](temporal_checker_consolidated_20261104/CONSOLIDATED_CHECKER_SPEC_v02.md): current proposed successor, not frozen or human-approved.
2. [Final source-review signoff](temporal_checker_consolidated_20261104/FINAL_SOURCE_REVIEW_SIGNOFF.md) and [final correction record](temporal_checker_consolidated_20261104/FINAL_REVIEW_CORRECTIONS.md): exact reviewed bytes and correction scope. Signoff is AI-assisted coherence review, not empirical qualification.
3. [Original independent design](temporal_checker_design_20261104/INDEPENDENT_CHECKER_DESIGN.md), [cross-review](temporal_checker_design_20261104/CROSS_REVIEW.md), and [erratum](temporal_checker_design_20261104/ERRATA_v01.md). Read the original with its erratum; do not condition measured-case inclusion on favorable caller assertions.
4. [Original acceptance specification](temporal_checker_spec_20261104/CHECKER_ACCEPTANCE_SPEC.md) and [reconstructed source reconciliation](temporal_checker_spec_20261104/SOURCE_RECONCILIATION.md). These retain antecedent wording; the latter is not a byte-identical repository export.
5. [Prior consolidated revision](temporal_checker_consolidated_20261104/preserved_before_final_review/CONSOLIDATED_CHECKER_SPEC_v02.md), retained unchanged with its original provenance, validation and checksums.

## Decisions still open

The consolidated register D01–D07 retains exact native outcome mappings, C1 attempt rule, C4 coverage and request anchor, coordinated-cut architecture, schema/view allowlists, predeclared inclusion/scoring and cleanup criteria as unresolved decisions. Proposed T01–T34 and supplementary F01–F30 are specifications, not executed tests or additional measured cases. The record does not change historical results, the unchanged gateway or execution restrictions.

## Preservation and source resolution

[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) maps all sixteen original local file labels to their repository paths and SHA-256 values. Twelve source files are byte-preserved. Four are explicit repository-facing derivatives: the final review receipt, correction record and provenance omit internal coordination wording/identifiers, and the consolidated checksum manifest is refreshed. Original and delivered hashes and transformations are recorded; originals remain private. Source labels beginning temporal_checker_* resolve from this package directory. The original acceptance-spec SHA256SUMS is checked from this package root; consolidated manifests are checked from their own directories. The package SHA256SUMS covers this delivered package except itself, and the root repository manifest includes all new files.

The historical prior consolidated snapshot retains five nonportable sibling Markdown links inherited when it was copied into preserved_before_final_review. They are not repaired in the preserved bytes; use the canonical links above. Its historical DOCUMENT_VALIDATION.json describes validation at drafting time, not present-path verification. Current consolidated specification and package-index links resolve.

Other historical local source labels are provenance, not public URLs or new live links. The controlling reconciliation is [the preserved repository record](../../research-records/v0.1/sources/reconciliation.md); its contract is [the preserved status/evidence contract](../../review/TEMPORAL_STATUS_EVIDENCE_CONTRACT_v01.md). Existing source/runtime archives retain the candidate and failed-attempt evidence. No private authorization exchange, message identifiers or unrelated conversation exports are newly copied here.

## AI-use trace

AI assisted the two original design/specification accounts, their source comparison, erratum, consolidation, final corrections and coherence review. The preserved cross-review distinguishes the designer's earlier local provenance from the acceptance-spec reviewer's later GitHub-verified merged head. The final signoff targets SHA256 5531671b0cea9423538a98ad0dcf0061476d85424e31bf1fbe1d37056770dcfc. Repository preparation checked source bytes, manifests and navigation only. No independent human validation, implementation correctness or native/runtime qualification is claimed. Existing AI disclosure workbooks remain unchanged.
