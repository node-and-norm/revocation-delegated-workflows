# Revocation study current synthesis

6 November 2026 · Node & Norm · Private research draft

## The question and the answer so far

When a person asks a delegated workflow to stop, what evidence distinguishes receipt of that request, an effective withdrawal of authority, and confirmation visible to the person?

The completed local study shows why these events need separate records. A request can be accepted before the authority fence is installed. A fence can stop an effect while the caller still lacks confirmation. An earlier committed effect remains after withdrawal. These are established systems principles, examined here through a bounded, execution-grounded instrument rather than presented as a new general theory.

**Current position:** the twelve-case local study is complete within its stated scope. The Temporal comparison is not qualified. A synthetic artifact checker and a draft evidence workbench support further method development, but neither supplies missing native Temporal results or evidence of benefit to human reviewers.

Start with [the reader notebook](../../notebooks/00_start_here.ipynb), then explore [the existing evidence workbench](../../notebooks/01_revocation_evidence_workbench.ipynb). This synthesis reconciles the records below; it does not replace their protocols, original observations or historical versions.

## How to read the record

- **Observed:** a recorded execution result within the declared instrument and trust boundary.
- **Checked:** a test or artifact review, with the method and independence limits stated.
- **Proposed:** a design or future comparison, not an executed result.
- **Blocked or unresolved:** a requirement without the evidence needed to accept it.

Test counts, fixtures, derivative packets and study cases are different units. Do not pool them into one sample or treat model-assisted review as independent human validation.

## What is complete

### Local instrument qualification

The preserved v0.2 instrument uses one authority root, one delegation edge, scripted workers and a trusted local gateway. Revocation and protected effects serialize within one SQLite transaction domain. Eighteen case-arm fixtures compare an intentionally weak admission-only arm with a commit-fenced arm. The seeded failures and exact-denial controls help test whether the checker detects the intended mechanism rather than merely seeing an empty sink.

This is finite engineering qualification. It does not establish hostile-worker confinement, a population failure rate or distributed closure. Earlier checker failures and corrections remain part of the record. See [the preserved protocol](../../qualification/v0.2/PROTOCOL.md) and [the repository's qualification account](../../README.md#preserved-v02-qualification).

### Framework integration pilot

The v0.3 pilot uses actual supervisor/subagent, human-in-the-loop and checkpoint machinery with scripted model responses. Eight fixed cases compare direct and checkpoint/resume paths. Four revoked attempts were refused; four live controls produced their declared effect or duplicate disposition. The gateway remains alive across graceful worker restart.

This is integration conformance, not a live autonomous-agent study or arbitrary crash-recovery test. See [the pilot decision](../decisions/2026-11-03-bounded-integration-pilot.md) and [protocol](../../integration/v0.3/PROTOCOL.md).

### Request to fence study

Six fixed schedules were executed on each of two paths, giving twelve cases. All matched the frozen checker expectations: six effects and six revoked denials. No recorded old-authority effect followed a local fence in these cases. The paths share the authority mechanism, so they are matched controls rather than independent security implementations. The fixture permits at most one outstanding withdrawal request; correlation relies on this fixed scope, not generalized authenticated revocation receipts. The completion envelope is fixture provenance, not a signed remote certificate.

| Schedule | What happened | What it teaches within this fixture |
| --- | --- | --- |
| S0 | A live action committed; no withdrawal occurred. | Legitimate work is a necessary control. |
| S1 | The fence and confirmation preceded execution; the action was denied. | Confirmed withdrawal can precede a protected attempt. |
| S2 | The effect committed before the fence; confirmation arrived later. | Withdrawal is not rollback. |
| S3 | The fence stopped execution before confirmation arrived. | Effective enforcement and caller knowledge can differ in time. |
| S4 | The fence stopped execution; confirmation was withheld. | An unconfirmed caller can coexist with an installed fence. |
| S5 | Request delivery was withheld; an effect committed without a fence in the window. | The same unconfirmed caller state can coexist with a different sink state. |

S4 and S5 are the central contrast. The caller's uncertainty does not identify the privileged sink's state. A stored zero post-fence count in a no-fence case is not evidence of successful fencing; the conditional measure is not applicable.

Sources: [executed study](../decisions/2026-11-03-request-to-fence-interface-study.md), [case summary](../review/WITHDRAWAL_INTERFACE_SUMMARY_v0.1.json), [post-run review](../review/WITHDRAWAL_INTERFACE_POSTRUN_REVIEW_v0.1.md). A fresh-environment same-host [reproduction](../review/WITHDRAWAL_INTERFACE_LOCAL_REPRODUCTION_v0.1.md) and a separately authored [AI-assisted artifact audit](../review/WITHDRAWAL_INTERFACE_PROTOCOL_FIRST_AUDIT_v0.1.md) add checks, not independent implementations or human validation.

## What remains open

### Native Temporal comparison

Bounded setup and schema checks were completed. The bridge attempt failed before dispatch with a socket-permission error and a subsequent cleanup error. No native Workflow/Activity qualification or measured Temporal experiment ran. Previously denied runtime operations must not be retried or bypassed through this documentation update.

A permitted environment alone would not complete qualification. The exporter and runtime evidence capture must be checked; observation phases, native outcome mappings, deadlines and cleanup acceptance must be settled and verified before a separate measured comparison can be considered. Source: [partial qualification](../decisions/2026-11-04-temporal-partial-qualification.md), [methods review](../review/TEMPORAL_METHODS_REVIEW_20261104.md).

### Synthetic artifact checker

The offline checker prototype has recorded passes for 115 project tests and 26 separately authored regressions. These are synthetic artifact checks, not native Temporal evidence. Its intended separation of collection completeness, treatment occurrence, claim support, qualification and cleanup must survive contact with real exported records before wider claims are warranted. Source: [implementation package](../checker-implementation/2026-11-05/README.md).

### Human evidence review

The retrospective package contains eight derivative packets from two selected synthetic historical cases. Packet qualification is complete; reviewer evaluation is unperformed. The full administrator archive contains answers and source identities, so it is unsuitable for blinded reviewers. Source: [packet qualification](../decisions/2026-11-03-retrospective-packet-qualification.md).

A proposed adjacent study asks whether independent reviewers can make more useful next-evidence requests under a fixed review budget than a competent source-linked checklist. The current packets can develop the rubric; they do not establish reviewer benefit or provide eight independent cases. Actual acquisition units, reference judgments, leakage controls, comparator strength and human-review authorization must be resolved before evaluation. This is a separate study question, not an extra result of the local revocation study.

## The next reader-facing work

1. **Reconcile the account.** Use this dated synthesis as the report entry point and keep every historical result attached to its own protocol and denominator.
2. **Validate the first workbench.** Verify the intended GitHub reading surface and, in an authorized environment, actual clean-kernel execution. The earlier fresh-process execution is not a Jupyter-kernel run. The existing [verification report](../../notebooks/VERIFICATION.md) preserves that distinction.
3. **Add focused views only when useful.** Next candidates are methods/qualification and traceability explorers. Each should answer a question the first notebook does not answer cleanly.
4. **Qualify the adjacent study's evidence.** Prepare a documentation-only feasibility matrix before proposing a reviewer experiment. Stop if an ordinary retained export or strong checklist already solves the useful problem.

The detailed agenda and ownership decisions belong in the research roadmap. This sequence does not promise dates for blocked work or authorize new experiments, recruitment, model calls, public release or repository merging.

## When this study can be called complete

The completed twelve-case collection can already be closed as a bounded local study. Its closure package should give a reader the frozen question and scope, case results, corrections, reproduction instructions, source-linked claims, limitations and AI-assistance disclosure. A contrary result or justified uncertainty is a legitimate outcome; success is not defined as all mechanisms being safe.

The Temporal extension is complete only if its declared qualification gates and separately approved protocol are met, results and unfavorable cases are preserved, and the bounded comparison is reviewed. Alternatively, a documented decision to defer or stop it can close that workstream without claiming qualification.

The proposed human-review study is complete only under its own frozen protocol and analysis, or a documented feasibility stop. Neither extension is required to describe the already completed local study honestly. The broader Node & Norm research program has no automatic final endpoint; each new question requires its own scope, useful contribution and stopping rule.

## Record preservation and disclosure

Raw archives, JSON/JSONL, databases, logs, original protocols and checksum manifests remain source records. Python modules and tests remain implementation. Notebooks are guided views over those materials; they do not replace them. The older Word specification remains the broader historical design, not the current results report. Workbook v0.11 remains the current recorded traceability snapshot, with later status changes presented explicitly rather than silently rewriting it.

AI assisted the framing, implementation, checks, reviews and this synthesis. Mark retains research decisions; no exhaustive human verification is claimed. All present material remains private. A future public release requires separate review of claims, rights, identifiers and disclosure. This synthesis adds no observations and changes no recorded result.

## Source version

This account was reconciled against private draft PR #3 at commit `20e782df7c32e05821b1fbad92d521fd45e4509d`, whose base is `6a2d6b19e18df28e2a8e69ee45830a5f9b94f26c`. Local historical records and the existing notebook are preserved; this report and reader route are new presentation material pending review.
