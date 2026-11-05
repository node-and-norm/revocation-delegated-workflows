# Interpretation and open work

## What this implementation can establish

This is an offline consistency and assertion-support checker for the local, explicit `synthetic-artifact-0.1` format. Synthetic tests exercise chosen rules and failure modes. Passing them establishes only that those executable expectations hold for those inputs with this code version.

It can compare registered bytes, validate supported schemas and linkage, reason over declared causal edges, reconcile supported saved sink tables, enforce caller-view boundaries and score claims against permitted references. Requirement results remain separate; one successful dimension does not repair another failed or missing dimension.

## What remains open

- **Production native exporter and adapters:** the synthetic format is not a lossless production Temporal export adapter. Concrete native schema mappings, version compatibility, source completeness and actual exporter behavior require separate implementation and review.
- **Native outcome mappings:** exact Workflow-side promise, Worker settlement, native Activity terminal and Workflow terminal tuples have not been empirically qualified here. These observations are distinct. A `finally` record is not Worker settlement or proof of all code cessation.
- **Numerical deadlines:** synthetic budget values, when present, are test data. They are not calibrated native deadlines. Finite budgets, local monotonic anchors, margins and freeze decisions remain open.
- **Native qualification and measurement:** no native run or live transport test is performed by this checker. C1/C4 controls, transport ambiguity, cleanup behavior and live sink controls require separately permitted qualification. Fresh measurement requires a later explicit decision after qualification and freeze.
- **Completeness and trust:** an offline checker cannot prove that producers omitted nothing or that certificates and acknowledgments are genuine. SHA256 proves byte agreement with a manifest, not authenticity. Complete-prefix, stable-interval and producer-accounting claims rely on a reviewed trusted fixture and complete coverage of relevant update routes.
- **Causal inference:** cross-process wall-clock ordering is not proof of causality. Matching snapshots establish presence at those observations, not uninterrupted preservation without complete interval evidence. Invocation-start alone does not prove an external cancellation call was submitted or delivered.
- **Side channels and isolation:** deterministic view validation checks the supported representation. It is not an adversarial security sandbox or an attested isolation mechanism. No human reviewer speed, usefulness or decision-quality benefit is measured.
- **Statistical claims:** the six-cell plan and 94 field opportunities do not imply independent observations, reliability estimates, production safety, novelty or AGI readiness. Paired views and synthetic fixtures are not additional measured cases.

## Missingness and adverse outcomes

Retain the fixed attempted-case and planned-opportunity denominators. Missing phases or unsupplied evidence are not caller omissions. Unknown fields and malformed output do not become justified abstentions. Unsupported agreement with hidden truth earns no support credit. Always-unresolved output is not favorable accuracy.

Unexpected effects, additional dispatches, retries, early closure and cleanup failures must remain visible. Analysis eligibility depends on evidence required by that analysis, not a favorable outcome or correct caller claims. Late evidence may expose contradictions but cannot backfill a missing primary observation.

## Operational boundary

Only local saved artifacts and newly created reports are in scope. This package neither imports nor executes the Temporal runtime, Worker, gateway or bridge and provides no networking or execution driver. It does not authorize retries of denied operations, emergency intervention, remote edits, live qualification or measured collection. Report generation success and CLI exit status never replace native qualification acceptance.

## Additional implementation boundaries

The complete synthetic registry is not an independently persisted P1/P2 runtime seal. Combined saved producer records are phase-filtered, but no claim is made that the primary bundle was physically sealed before release. `freeze_requirements.phase_manifest_sealing` remains unobserved. Real per-phase registries and a producer-prefix capture/export procedure are still required.

Runtime monotonic deadline enforcement is not implemented. All delivered fixture budgets are unset. The current native and settlement payloads use a deliberately closed synthetic result union: an empty object, a Boolean `synthetic` marker, or a string `type`/`message` pair. Actual SDK result/failure encodings need their own reviewed adapter rather than being accepted through an open dictionary.

Paired fixture projections share a deterministic reference generator. Equal A/B scores are a software packaging check, not an independent baseline comparison or empirical result. The contract's named Activity execution observations can coexist: a correctly cited Worker settlement remains supported even if a native terminal observation is also available.
