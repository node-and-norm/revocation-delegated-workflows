# Bounded integration pilot: decision and evidence boundary

Date: 2026-11-03 UTC (2026-11-02 in the researcher's local evening).  
Status: **Bounded synthetic integration pilot completed; final AI-assisted review passed.**

## Decision

The researcher authorized a bounded runnable integration pilot using synthetic data and no paid model calls, with the reviewed package and AI-use records retained in the private repository.  The choice resolves the November 1 pending decision in favor of validating an actual integration.  It does not resume an open-ended novelty search or authorize public release.

The question is whether the existing local commit-fenced authority policy remains enforced through a documented framework path after a worker resumes a saved checkpoint, while matched authorized work completes.  This is an integration-conformance milestone.  A new revocation protocol, a framework vulnerability and AGI readiness are not claimed.

## What was integrated

The workflow adapts the email branch of the official LangChain personal-assistant tutorial.  It uses the actual framework path:

**create_agent supervisor → manage_email tool → create_agent email subagent → HumanInTheLoopMiddleware → synthetic send_email tool**

Scripted model responses are derived from persisted message history rather than a mutable in-memory response counter.  Those responses exercise the framework without calling a live language model.  The tool records a harmless local synthetic effect; it does not send email or access a calendar.

The framework first reaches a human-in-the-loop interrupt.  A persistent SQLite checkpointer retains the pending call and arguments.  The initial worker exits gracefully.  A fresh worker reconstructs the framework, verifies the restored pending action and interrupt, and resumes it.  The historical gateway remains alive throughout.  Only the worker restarts; arbitrary crash recovery, gateway restart and distributed recovery are outside this pilot.

Trusted controller code reattaches the principal, grant, ticket and operation references on reconstruction.  The checkpoint restores workflow/action state, not authoritative permission.  This arrangement does not demonstrate secure recovery or transport of arbitrary dynamic credentials.  The adapter binds the complete synthetic tool arguments before calling the gateway.  The gateway independently checks its principal channel, grant, ticket, scope and existing atomic sink policy.

## Comparison and evidence

The frozen matrix contained eight measured runs: direct reference or framework restart, crossed with no prior effect or a prior committed effect, crossed with live or revoked authority.  Both paths use the same final authority policy and protected operation.  The direct path replaces framework scheduling with explicit controller scheduling; it is not a second weaker security policy.

A prior effect is a reference setup action, not credited as framework execution.  Revocation and protected writes are ordered by the same gateway database commits.  The observer reads the sink without writing it.  Final framework output must retain the structured sink disposition, so denied work cannot be reported as successful sending.

The intended distinctions are:

- No prior effect, live authority: a new authorized effect and successful completion.
- No prior effect, revoked authority: refusal for revocation and no effect.
- Prior effect, live authority: a duplicate disposition without another mutation.
- Prior effect, revoked authority: refusal for revocation while retaining the pre-fence effect.

The historical policy checks revocation before duplicate lookup.  The pilot preserves that rule.  A late response or retained pre-fence effect is not a new post-fence mutation.  The same-history live controls are needed to exclude blanket denial as an explanation for apparent control success.

All **eight fixed measured cases** matched the declared expectations.  The separate reviewer regraded the saved records and inspected the actual sink and checkpoint SQLite files read-only.  Four revoked attempts were refused, with no post-fence effects.  The four live controls completed with the expected effect or duplicate disposition.  All four framework runs used distinct initial and resumed worker processes and retained matching checkpoint evidence.

The pilot's **18 instrument tests passed**.  These tests and eight fixed cases are engineering checks, not independent statistical samples, a failure-rate estimate or evidence covering all possible schedules.  The [measured summary](../../integration/v0.3/evidence/measured01_summary.json) and [final AI-assisted review](../../integration/v0.3/evidence/reviewer_final.json) provide the exact classifications and verification record.

## Corrections and interpretation

Qualification and measured collection are separate.  Earlier instrument failures, counterexamples, corrections and reruns remain retained rather than being silently repaired in place.  A matching expected result only qualifies the stated finite case; it does not estimate a failure rate or prove that all event orderings are safe.

The recorded result establishes that the actual framework, persistence and middleware path was exercised under the declared conditions and that the sink evidence matched the stated local contract.  It does not establish a new security mechanism or superior protection relative to systems with different contracts.

Review found two initial checker false passes involving contradictory delegation scope and admission-grant evidence.  Those counterexamples were preserved and the checker was corrected before measured collection.  Other retained qualification corrections address native-object serialization, evidence retention before assertions, read-only observation, the classification of prior effects without a revocation fence, a fabricated negative fixture and checkpoint/binding checks.  They are instrument-development corrections, not observed framework control failures.

## Relationship to prior work

The contribution review identified substantial existing work on long-running-agent revocation, late effects, causal controls and framework recovery.  Relevant comparisons include [Authorization Revocation for Long-Running AI Agents](https://arxiv.org/html/2609.21284v1), [arXiv:2610.15991v1](https://arxiv.org/html/2610.15991v1), and [Permission to Retry](https://arxiv.org/html/2610.31916v1).  These references motivate a bounded conformance integration, not a claim that adding LangGraph, a parent/child path or a stronger chosen fence is novel.  Differences in admission and effect contracts must be stated before comparisons.

## Limits, AI use and preservation

The pilot concerns one deterministic synthetic workflow on a trusted host.  It does not evaluate autonomous planning, live model decisions, remote email effects, malicious-worker confinement, deep delegation, arbitrary process crashes or institutional control effectiveness.  The observer and checker rely on the same trusted host and retained database integrity.

AI assistance supported source inspection, workflow adaptation, implementation, instrument qualification, review and documentation.  Separate AI-assisted review is not independent human validation.  The new traceability records identify consequential assistance, errors, corrections and claims alongside the evidence supporting them.

The v0.1/v0.2 qualification source, results and archives, the prior specification and dated decision notes remain preserved.  The earlier workbook and notebook are historical versions; new records are versioned separately.  The README supplies current status without rewriting earlier decisions.  No website edit or public release is part of this update.

## Inspect the artifacts

- [Pilot protocol and implementation](../../integration/v0.3/)
- [Prior workflow-selection decision](2026-11-01-workflow-selection-and-contribution-gate.md)
- [New traceability records](../traceability/v0.2/)
- [Research notebook v0.2](../../notebook/v0.2/Revocation_Research_Notebook_v0.2.zip)
- [Full source and evidence archive](../../archives/revocation_integration_pilot_v03_20261103.zip)
- [Pinned upstream sources and runtime references](../../integration/v0.3/evidence/source_pins.json)
