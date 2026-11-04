# Independent methods review: proposed Temporal qualification

Review date: 4 November 2026 UTC. Scope: read-only, source-derived independent AI-assisted review. No observed native run, source modification, test execution, experiment, alternate environment or access bypass. This separate review artifact was authorized after the review; it does not change the candidate, tests or protocol.

The following preserves the reviewer’s final report verbatim.

Read-only review found three remaining issues beyond socket creation, EOF handling and missing transport mocks. No files changed and no experiments run.

1. **A native qualification can report success despite a failed Activity or wrong sink outcome.**
   - `temporal_qualification_20261104/source/workflows.ts:18–20` catches all Activity errors.
   - `source/native_runner.cjs:43–64` accepts completion, failure or cancellation, rejects only timeout, and writes `ok:true` after observation release.
   - `source/supervisor.py:53–57` checks process exit, snapshots SQLite and declares success without asserting the expected effect or revoked denial.
   - Example source-derived path: a continuation Activity encounters a bridge error; Workflow catches it; native history records failure; observation release succeeds; teardown is clean. Both success flags can remain true despite no expected effect.
   - **Action:** distinguish “records collected/lifecycle finished” from “qualification passed.” Independently verify expected sink rows, attempts and denial reason, and explicitly adjudicate the native mapping. Unexpected mappings must remain unresolved rather than qualify automatically. This is a prospective false-pass path, not an observed run failure.

2. **The purported precleanup sink record is not necessarily before Worker cleanup.**
   - `source/native_runner.cjs:65–66` exports failure history and then shuts down the Worker.
   - `source/supervisor.py:53,61–64` waits for Node exit before taking the sink snapshot named `supervisor_precleanup.json`.
   - Therefore the native-history cut and sink cut straddle Worker shutdown. A still-running Activity can settle or affect the sink during that intervening cleanup. “Precleanup” currently means before supervisor termination, not before all cleanup.
   - **Action:** establish a coordinated primary observation cut, preserve both native history and sink state at that cut before Worker shutdown, and label later activity/ledger changes cleanup-only. At minimum, expressly prevent these failure-path snapshots from supporting primary no-effect/cessation conclusions.

3. **Two supposedly related normative documents still disagree on no-effect classification.**
   - `temporal_protocol_20261103/PROTOCOL_REVIEWED_DRAFT_v02.md:80–81` lacks a no-effect ordering category.
   - `STATUS_EVIDENCE_CONTRACT_v01.md:30–32` correctly includes `not_applicable_no_effect`.
   - **Action:** reconcile the protocol with the contract and declare the authoritative version before freeze. Otherwise cooperative/fenced zero-effect cases cannot be classified consistently using the protocol enum.

**Methods assessment:** The revised evidence contract avoids the principal invalid comparison: it gives the ordinary baseline the same evidence, explicitly treats envelope removal as packaging rather than loss of underlying evidence, and disclaims reliability, human-efficiency and novelty claims. I found no additional basis for claiming an adapter advantage. The independent checker, caller-view allowlists and exact native outcome mapping remain unimplemented/unqualified gates, not results. The current partial-status document appropriately does not claim native qualification passed.

## Clarification after final-report preservation

The third finding is a preserved-snapshot/version-authority discrepancy, not an omission in the current mutable `PROTOCOL_DRAFT.md`. Subsequent direct inspection confirms that file’s lines 80–81 already include `not_applicable_no_effect`; the cited `PROTOCOL_REVIEWED_DRAFT_v02.md` snapshot does not. Preserve the historical snapshot unchanged. Before freeze, identify the controlling protocol and record the reviewed delta rather than claiming the current draft still needs the enum fix.

Short `source/` paths above are relative to `temporal_qualification_20261104/`; the short evidence-contract path is relative to `temporal_protocol_20261103/`. The statement “No files changed” describes review conduct before creation of this separately authorized report artifact.
