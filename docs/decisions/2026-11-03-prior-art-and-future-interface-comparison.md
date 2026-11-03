# Prior art and a possible future interface comparison

Date: 2026-11-03 UTC  
Research owner: Mark Julius Banasihan  
Status: source review and proposed design. No Temporal integration or experiment has been run for this comparison.

## Current evidence

The [completed request-to-fence study](2026-11-03-request-to-fence-interface-study.md) records 12 fixed cases in a trusted local instrument. Its caller separately observes acceptance and completion while the evaluator inspects the local fence and effect ledger. S4 and S5 share an unconfirmed caller state with different sink outcomes. This is a bounded interface/conformance result. The current evidence establishes no novel revocation principle, production failure or vendor defect.

## Verified overlap and interface contracts

Sources were read on 2026-11-03. Paper statements below are author-reported; reviewing a paper does not independently reproduce its results. Live documentation is not a pinned SDK implementation.

| Source | Documented contribution or behavior | Consequence for this study |
| --- | --- | --- |
| [Permission to Retry, v1](https://arxiv.org/html/2610.31916v1), abstract and contribution boundary | Separates checkpoint state, dispatch permission, effect evidence and reconciliation authority. Reports a finite conformance campaign on LangGraph and Temporal with a hidden provider effect ledger. | Native workflow integration and separation of authority from effect evidence already have close precedent. Our smaller interface study needs a clearly bounded applied purpose. |
| [Root-scoped quiescence, v1](https://arxiv.org/html/2609.21284v1), sections 1.2, 2 and 5 | Separates actuation from evidence; combines local fences with coverage and channel accounting. Missing evidence remains indeterminate. Local closure alone does not establish a complete cross-provider cut. | Acceptance, fencing and evidence delivery are established distinctions. Our single-sink result supplies no global quiescence certificate or distributed closure proof. |
| [Temporal cancellation and termination](https://docs.temporal.io/encyclopedia/workflow/cancellation-and-termination), cancellation behavior | Workflow cancellation is cooperative, permitting application cleanup and a chosen closing status. Termination closes the Workflow Execution immediately without running cleanup. | Define the native operation precisely before comparing it with an authority fence. Workflow lifecycle status and protected-effect authorization have different contracts. |
| [Temporal TypeScript ActivityCancellationType](https://typescript.temporal.io/api/namespaces/common#activitycancellationtype) | ABANDON reports cancellation without propagation. TRY_CANCEL propagates a request and reports to the caller immediately, without delivery assurance. WAIT_CANCELLATION_COMPLETED waits for the Activity's final completion, failure or cancellation; receiving cancellation requires heartbeats. TRY_CANCEL is the documented default. | Include the waiting mode as a strong native baseline. An early caller response in TRY_CANCEL is documented behavior. A heartbeat delay or ignored request can prolong the waiting mode. |

A completed Activity result would need an explicit mapping to the protected effect and its authoritative record. The documentation review alone establishes no provider-side fence, rollback guarantee, or absence of application-level controls. That mapping is a proposed research obligation.

## Proposed bounded comparison

Before implementation, pin the Temporal server, SDK and worker versions and choose one SDK consistently. Define one synthetic protected operation and one effect ledger, preserving the current trusted-host assumptions. Record distinct events for request submission, native acknowledgement, Activity disposition, fence installation, effect commitment and caller-visible completion.

Compare competent native configurations under matched workloads and evidence access: immediate request reporting and waiting for Activity completion, each with clearly specified heartbeat/cooperation behavior. Keep a separate reference path for local authority enforcement. A fence-enhanced configuration adds an application control; its extra guarantee and cost must be attributed to that control. A cancellation-only arm has a narrower contract and should be graded accordingly.

The smallest useful question is whether a documented adapter can preserve these status distinctions in the final caller response under a few predefined schedules, including a pre-fence effect and an unavailable completion message. Measure contract violations and unjustified positive claims separately from expected uncertainty. Avoid treating a deliberately withheld message as natural network-loss evidence.

## Contribution gate and stopping criteria

Prospective users are engineers integrating human withdrawal into durable enterprise workflows and reviewers interpreting the resulting records. Practical utility would require a reproducible adapter contract or evidence check that resolves an actual integration ambiguity beyond a careful reading of native documentation.

Strong competing explanations are that native waiting semantics plus an ordinary source-linked checklist already answer the question, or that any apparent benefit comes entirely from adding the local fence. Correct findings under either explanation are useful. They would reject a claim of a new control mechanism or justify stopping further integration work.

Proceed only after documenting the exact unanswered question, source-pinned contract, matched baseline and permitted execution scope. This note authorizes no new integration, model call, external service, recruitment or publication. Existing experiments and historical artifacts remain unchanged.
