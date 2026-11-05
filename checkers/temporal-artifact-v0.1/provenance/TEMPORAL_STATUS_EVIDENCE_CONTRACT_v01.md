# Proposed status and evidence contract

Research owner: Mark Julius Banasihan. Date: 3 November 2026. Design only; no implementation or execution. Read alongside PROTOCOL_DRAFT.md. This contract specifies a proposed application projection. It does not change native Temporal guarantees.

## Source pin and interpretation

The official TypeScript SDK release page identifies v1.25.0 with commit efafd16ef4533da24029277bd72caf564c7aa007. The following file was directly read through the cloud browser at that commit:

https://github.com/temporalio/sdk-typescript/blob/efafd16ef4533da24029277bd72caf564c7aa007/packages/common/src/activity-options.ts

Its ActivityCancellationType definition distinguishes request propagation and when the Workflow-side Activity promise reports cancellation. TRY_CANCEL can report before delivery assurance. WAIT_CANCELLATION_COMPLETED waits for final execution, including success, failure or cancellation. Heartbeats deliver cancellation notifications. Its ordinary Activity retry option specifies maximumAttempts=1 for zero retries. The source documents TRY_CANCEL as the default; the study sets the mode explicitly. The ordinary Activity contract is used; LocalActivity retry semantics differ and are excluded.

This pins the inspected contract declaration and comments. It does not pin the complete runtime or establish implementation conformance. Server/CLI, Node, package resolution/integrity, underlying SDK/Core behavior, and cancellation/result handling still require qualification and freeze.

A web-cached raw-main response had different default text. The directly inspected release-pinned source agrees with the live API docs. No claim of a current vendor documentation defect follows from the cached response.

## Proposed application envelope

Each envelope contains schema_version, case_id, workflow_id, run_id, activity_id, activity_attempt, operation_id, authority_scope, observation_cut_id, native_mode and a list of assertions. Each assertion contains a field, value, evidence_refs, observer, and scope. IDs provide fixture correlation, not authentication.

| Field | Supported values | Required evidence | Insufficient evidence |
|---|---|---|---|
| cancellation_request | not_requested, response_received, error, unresolved | Actual external-client call record | Controller intention alone |
| activity_call | pending, settled_with_recorded_result, settled_with_recorded_failure, unresolved | Workflow-observed promise outcome | External cancel response |
| activity_execution | last_instrumented_point, worker_invocation_settled, native_terminal_record, unresolved | Each named observer's own linked record | Renaming one final log as proof of all code cessation |
| workflow_execution | running, exact_terminal_status, unresolved | Native Workflow history/result for same run | Activity outcome alone |
| fence | confirmed_for_fixture_scope, unresolved | Current sink receipt cross-checked against trusted ledger | Any Temporal cancellation status |
| effect_existence | present, absent_with_complete_bounded_evidence, unresolved | Bounded sink evidence for exact operation and observation cut | Activity return or missing log alone |
| fence_existence | present, absent_with_complete_bounded_evidence, unresolved | Bounded sink evidence | Missing caller receipt alone |
| effect_order_vs_fence | before, after, not_applicable_no_effect, no_fence_in_complete_window, unresolved | Sink transaction sequence and completeness | Cross-process timestamp comparison |
| effect_order_vs_request | before, after, not_applicable_no_effect, no_request, unresolved | Explicit causal barriers and linked events | Wall-clock ordering alone |
| effect_order_vs_observed_cancellation | before, after, not_applicable_no_effect, no_observation, unresolved | Activity observation plus causal release chain | Heartbeat emission alone |

The application envelope can aggregate observations without upgrading their strength. Conflicting records yield unresolved plus conflict references. A field without qualifying evidence remains unresolved. No aggregate “safely stopped” field is defined.

## Evidence views and baseline

The competent baseline receives the same native observations, source-linked checklist and ordinary sink-status lookup as the proposed projection. WAIT plus native outcome and sink lookup is the strong native comparison. Equal access includes identities, observation cut, completeness assumptions and review budget.

This evidence-view exercise tests deterministic assertion support and reconstruction from differently packaged records. It does not test loss of underlying completion evidence. No reviewer performance, time-saving, decision-quality or human-usefulness claim is measured.

Two derived views may be prepared from a saved run. View A contains the permitted application envelope. View B removes that entire envelope while retaining the same predeclared underlying native observations available at the cut. The removed object is not a native Workflow result, Activity terminal record or fence receipt. Each view's exact file allowlist must be frozen and checked for duplicate leakage before use. View B may retain enough underlying evidence for the ordinary baseline to reconstruct the same conclusion; that is a useful negative result about the envelope's incremental value. Removing raw evidence as well would be a different intervention and requires a separate specification.

The envelope includes a source reference to each assertion. The sink-backed fields are absent from any caller view that lacks authorized sink evidence. The privileged checker never supplies hidden answers to the caller projection.

## Expected measured matrix

All expectations below are proposed fixture expectations. Qualification determines exact native result/error mapping before freeze.

| Cell | Mode | Controlled continuation | Fence | Expected sink result | Permitted interpretation |
|---|---|---|---|---|---|
| M1 | TRY_CANCEL | One attempt after cancellation is observed | Absent | One effect | Early Workflow cancellation reporting does not imply no effect |
| M2 | WAIT_CANCELLATION_COMPLETED | Same continuation as M1 | Absent | One effect | Record actual native final state separately from effect |
| M3 | TRY_CANCEL | One attempt after cancellation observation and fence commit | Present | Revoked denial, zero effects | Protection attributed to sink enforcement |
| M4 | WAIT_CANCELLATION_COMPLETED | Same continuation as M3 | Present | Revoked denial, zero effects | Native outcome and fence-backed denial reported separately |
| K1 | Mode-independent control | One valid live attempt, no cancellation | Absent | One effect | Confirms useful work is possible |
| K2 | Mode-independent control | One attempt, no cancellation | Present | Revoked denial, zero effects | Confirms fence alone supplies the denial |

C1 cooperative cancellation delivery and C4 pre-existing effect preservation remain qualification checks. Six measured cells are not a reliability sample. Evidence projections do not increase that denominator.

## Checker obligations

1. Assert exact SDK mode/options, runtime identifiers and one ordinary Activity attempt; reject unintended retries.
2. Verify each relevant native event belongs to the same Workflow run and Activity attempt. Activity ID alone is insufficient.
3. Confirm cancellation observation precedes the controlled continuation release in M1-M4 using causal barriers.
4. Confirm the fence transaction precedes the sole sink attempt in M3/M4/K2. Confirm the corresponding denial cause.
5. Count actual sink rows and attempts, not summaries: M1/M2/K1 each have one effect; M3/M4/K2 each have one revoked denial and zero effects.
6. Keep Workflow lifetime open through the observation release. Record early closure as an invalid treatment, preserve its evidence and do not count it as a successful cancellation comparison.
7. Compare native Activity terminal history, Workflow-observed settlement and worker instrumentation without conflating their meanings. Flag disagreement for investigation.
8. Derive effect/fence/request ordering with explicit no-effect/no-fence/no-request categories. No timestamp-only causal judgment.
9. For every application assertion, check support against that view's file allowlist. Hidden ground-truth agreement alone earns no credit.
10. Verify observation cuts and completeness boundaries. Truncation or contradictory evidence produces unresolved.
11. Run mutations for unsupported positive claims, wrong linkage, omitted effect, invented fence, reordered effect, altered epoch and incomplete history. These detect fixture consistency errors, not cryptographic authenticity or security isolation.
12. Verify historical archives remain byte-identical and new outputs occupy a separate directory. Preserve failed controls and corrections.

## Practical decision

Proceed to a separate qualification proposal after the historical sink archive is retrieved and verified, the exact runtime is pinned, the cancellation-shielded lifecycle is specified, and the envelope/allowlists and checker obligations pass review. Qualification is development evidence, not measured collection.

Hold measured collection until all valid controls pass and expected native mappings are frozen. Stop expansion when ordinary WAIT plus source-linked sink lookup answers the practical question equally well and no additional deterministic integration check is identified. Human auditability or review-efficiency benefits would require a separate approved reviewer evaluation. A competent baseline matching the proposed method is a valid result. Novelty, production reliability and AGI readiness claims remain outside this protocol.

