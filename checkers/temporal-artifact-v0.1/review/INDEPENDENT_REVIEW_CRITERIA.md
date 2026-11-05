# Independent artifact-only checker review criteria

5 November 2026. AI-assisted review specification, not native evidence or human validation. Source: approved proposal v0.3, DOCX SHA-256 4461fd4694521b291092edd2737e8a50f41de6ee342d037511dba7dff4659246; PR #2 consolidated v0.2 at head 8c2c1615985fd90b08a9cca8aabaa7b7e5e052f7. New v0.3 rules supersede earlier prospective wording only for newly versioned fixtures.

## Review standard

The checker must not import or run the gateway, Worker, bridge, Temporal SDK, controller, sockets, or transport mocks. Read-only source review, synthetic saved-artifact creation and artifact-only tests are in scope. No remote repository change is required. A passing synthetic suite establishes checker behavior only, not qualification or readiness for measurement. D01 mappings and numerical deadlines remain open.

Each fixture has a neutral immutable identity, explicitly synthetic provenance, complete expected per-rule statuses, and an intended semantic rule. A semantic mutation reseals the manifest and is required to reach that rule with integrity satisfied. Separate stale-hash mutations exercise integrity. A global non-pass alone does not validate a negative fixture.

Every result preserves separate integrity, setup/schedule, actual native tuple, sink facts, capture, caller support, cleanup, qualification and analysis-eligibility dimensions. Missing or bad input fails the affected gates without globally erasing independently established positive facts. No expected outcome, runner flag or caller claim is an oracle.

## Concrete adversarial matrix

| ID | Fixture change | Required result |
| --- | --- | --- |
| R01 | Set all runner success flags and exit codes favorable while removing expected effect consistently. | Expected-outcome failure; flags cannot repair facts. T04/F01/F06. |
| R02 | Delete an effect row while retaining its event; converse; orphan event_seq; payload/root/epoch mismatch. | Bidirectional row/event accounting failure and identified defect. T06/F05. |
| R03 | Add execute receipt without terminal; terminal without receipt; two terminals for one receipt; substitute non-execute receipt. | Exact execute/terminal reconciliation failure, no count-all-receipts shortcut. |
| R04 | C1 extra dispatch transport-fails, with zero committed receipts/effects. | Failed zero-dispatch control outcome; actual attempt retained, no setup-based exclusion. |
| R05 | C4 second dispatch returns duplicate, effect remains one. | No-additional-execute outcome fails despite unchanged effect cardinality. |
| R06 | M3/M4/K2 denial is invalid_ticket, wrong_actor or invalid_grant, no effect. | Denial fact retained, no revoked-fence-protection credit. T05/F03. |
| R07 | Committed ledger effect and matching row, bridge response missing/transport error. | Effect present; transport outcome independently unresolved. T27/F28. |
| R08 | Current fence receipt absent, ledger shows valid relevant revocation. | fence_existence present; receipt-backed fence unresolved. T34. |
| R09 | Fabricated current fence receipt, no corresponding ledger transition. | No fence confirmation; unsupported positive claim. T30/F07. |
| R10 | Fence/release causal order reversed or absent, otherwise coherent records. | Reversed order unsatisfied; absent order unobserved; separate positive facts survive. T11/F08. |
| R11 | Reverse all wall clocks but preserve causal graph and transaction sequences. | Same order conclusions. T23/F17. |
| R12 | Favorable clocks, remove required causal links. | Order unresolved, not repaired by timestamps. T24/F18. |
| R13 | Correct Activity ID but wrong run, scheduled/start link or actual attempt. | Linkage failure, not accepted chain. T08a/T25/F10. |
| R14 | Consistently rename opaque synthetic IDs with every binding/reference updated. | Equivalent semantic verdict, no authenticity claim. T08b. |
| R15 | maxAttempts=2 effective configuration versus maxAttempts=1 with unexpected attempt 2. | First is setup defect; second is retained adverse native outcome. Neither invents qualification acceptance. |
| R16 | Replace cancellation observation with heartbeat or client success response. | Native observation unobserved; not cooperative delivery proof. T09/F20. |
| R17 | Only finally record; no interceptor settlement/native terminal. | Only finally fact supported, no settlement or cessation inference. T26/F21. |
| R18 | Workflow completes while Activity failed; exact failure detail retained. | Preserve separate tuple components and unexpected outcome; never equate Workflow completion to Activity success. T12/F02. |
| R19 | Unknown native tuple, no reviewed mapping, or mapping copied from synthetic expectations. | Actual tuple preserved; empirical mapping/qualification gate remains unobserved or blocked. T12/T32/F26. |
| R20 | C4 effect before client response but after invocation-start. | Pre-request requirement fails, since invocation-start is anchor. |
| R21 | C4 effect/bridge/Activity/coordinator chain missing one acknowledgment. | Pre-request causal conclusion unresolved despite favorable timestamps. |
| R22 | C4 invocation record exists, process crashes before actual submission. | Invocation exists; actual submission/delivery unresolved. |
| R23 | C4 matching initial/final snapshots without complete mutation ledger. | Effect present at both observations; no uninterrupted-preservation claim. T21/F27. |
| R24 | C1/C4 introduces revocation or continuation-release. | Intended cancellation-only contrast contaminated; actual outcomes retained. |
| R25 | P1 includes P2 terminal, P3 effect, or later source locator. | Leakage/support failure; no primary repair from later evidence. T13. |
| R26 | P2 requires P1 persisted acknowledgment before release; omit or reverse. | Phase/capture schedule defect or unresolved relation, not a valid primary cut. |
| R27 | Native primary cut precedes interceptor settlement/terminal; sink-only fixture omits native hold. | Native completeness insufficient; sink-only omission legitimately inapplicable. |
| R28 | Queued/buffered/in-flight/uncertain dispatch remains despite zero current effects. | No conclusive absence or quiescence; observed failure to settle may be adverse. |
| R29 | Capture relies on active admission seal/process kill/synthetic fence. | Intervention recorded, no cancellation-based absence credit. |
| R30 | Missing source acknowledgment, pagination token chain, prefix declaration or closing check; contiguous IDs retained. | Affected completeness unobserved; contiguous IDs alone insufficient. T14/T17/F15. |
| R31 | Different sink transaction IDs or inconsistent all-table boundaries. | Mixed snapshot rejected; no global-atomicity claim. T15. |
| R32 | P3 same previously resolved dispatch commits late. | Certificate contradiction/investigation; primary and later facts remain phase-labeled. |
| R33 | P3 distinct newly authorized operation commits after closed interval. | Does not alone retroactively invalidate prior bounded capture. |
| R34 | Cleanup shutdown error/nonzero child exit/forced action after valid primary effect. | Primary effect retained; cleanup and overall qualification fail. T16/F29. |
| R35 | Missing original error, replaced by secondary cleanup error. | Failure-preservation gate fails; no favorable cleanup repair. |
| R36 | Duplicate JSON keys, malformed JSONL line, unsupported version, duplicate logical IDs, unresolved locator, causal cycle. | Fail closed on affected structural gate. T17/T28/F19. |
| R37 | Native ID encoded float, exponent, fractional number, boolean, negative, overflow/coerced text. | Reject invalid representation; valid large decimal strings/lossless integers retain exact identity. |
| R38 | Registry traversal/absolute path/symlink escape/duplicate identity/undeclared evidence/registry self-hash. | Integrity rejection with precise path/role reason. |
| R39 | Unknown nested semantic field or enum versus namespaced diagnostic extension. | Unknown semantic fields cannot satisfy rule; allowed diagnostic retained uninterpreted. |
| R40 | View B envelope duplicated in alternate filename, nested extra field, renamed object or source-map private reference. | View isolation failure; no loophole for equivalent encoding. T20/F25. |
| R41 | A and B underlying byte content differs; identical A/B evidence with envelope removed only. | First paired comparison invalid; second may reconstruct identical results and must not manufacture benefit. T19/F24. |
| R42 | Hidden truth supports caller assertion, permitted cited evidence does not. | Unsupported determinate, never correct due to privileged access. T18/F23. |
| R43 | Caller unresolved on decidable and undecidable references, plus omitted field. | Avoidable unresolved, justified unresolved and malformed/omitted are distinct. |
| R44 | Caller determinate contradicts permitted decisive evidence and has bad refs. | Contradicted takes precedence over unsupported unless malformed/omitted already applies. |
| R45 | Always-unresolved output on decidable set; no determinate claims. | Zero conclusive coverage; determinate support rate undefined, not 100%. |
| R46 | Planned P2 never collected or never supplied; supplied P2 output omitted. | Planned 94 denominator retained; never-supplied not caller omission; supplied omission scored. |
| R47 | K1/K2 lifecycle output fields, fabricated native records or P2 phase. | Exactly seven P1 opportunities; native inapplicability enforced, no fabricated identities. |
| R48 | Correct schedule, complete unexpected adverse sink/native outcome, bad caller claim. | Attempt remains; applicable analysis eligible independent of favorable result/claim. T31. |
| R49 | Relabel earlier qualification/Q2 record as measured K1; pooled diagnostic/paired-view count. | Provenance/inclusion rejection; preserve separate populations. T22. |
| R50 | Remove evidence supporting absence/order; add irrelevant files; reorder unrelated records. | Evidence removal never strengthens support; extra undeclared files cannot improve support; causal results serialization-invariant. |
| R51 | Deadline unset/negative/non-finite or anchored across processes; late success after declared timeout. | Readiness blocked; timeout means not observed before deadline, never proven absence; no deadline extension to rescue outcome. |
| R52 | Novel native tuple after freeze or instrument-version mismatch. | Original attempt retained, investigation/stop indicated; no silent mapping rewrite. T32. |

## Completion requirements

- Trace preserved T01–T34 and nonredundant F01–F30 to executed test names and exact rule assertions. Overlap is coverage, not additional empirical cases.
- Distinguish unit tests from serialized integration fixtures, raw SQLite reconciliation, view projection checks, and CLI tests.
- Test positives as well as negatives, both modes and sink-only applicability, justified and avoidable abstention.
- Report any unsupported native adapter, schema binding, capture proof, timing calibration or raw exporter honestly. Synthetic stub metadata cannot close these gates.
- Verify deterministic output, no input mutation and no socket/Temporal import path during artifact-only execution.
- Freeze review to exact code/test/schema hashes after fixes. Any subsequent edits require affected tests to rerun.
