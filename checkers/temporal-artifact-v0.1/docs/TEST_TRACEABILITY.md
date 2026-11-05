# Test traceability and remaining coverage

The project suite is executable synthetic software validation, not native qualification. Exact expectations are written in unittest assertions. Semantic mutations reseal their manifests before checking the intended rule; stale-hash tests are separate. Saved positive fixture expectations are in `fixtures/catalog.json`.

**Do not read this as “T01–T34 fully qualified.”** Runtime dependencies and several broader mutation variants remain open. The table identifies implemented coverage and limits rather than converting proposal vectors into empirical results.

| Proposed vector | Implemented evidence / limit |
| --- | --- |
| T01 | `test_c1_zero_execute_both_modes`; C1 saved fixtures in both modes. Native tuples remain unresolved. |
| T02–T03 | `test_six_cells_have_94_opportunities_per_view`; M1–M4 saved fixtures. |
| T04 | `test_invented_success_cannot_override_wrong_outcome`; real runner behavior not executed. |
| T05 | `test_wrong_denial_cause`, `test_wrong_denial_preserves_bounded_absence`. |
| T06 | `test_omitted_effect_row`; sink orphan/missing-event tests. |
| T07 | Sink duplicate receipt/result test plus C4 extra-dispatch test. |
| T08a | Wrong run/start binding tests, pin validation and linkage review tests. |
| T08b | Fresh fixtures use random neutral IDs and serialization invariance is tested. A complete multi-record opaque-rename metamorphic test is not separately implemented. |
| T09–T10 | Missing cancellation observation and misspelled behavior tests. |
| T11 | Revocation command/link and graph checks implemented. Fully correlated reversed-ledger mutation is not a separately saved test vector. |
| T12 | All ordinary fixtures keep `native.mapping` unobserved; actual tuples are reported. Qualified mapping acceptance is unavailable. |
| T13 | Phase-boundary late-commit test and independent P3 same-request/unrelated-request regressions. |
| T14 | Missing acknowledgment, missing phase, phase isolation and native-boundary tests. |
| T15 | `test_mixed_sqlite_snapshots` detects inconsistent saved transaction identities. A real concurrent capture race has not been run. |
| T16 | Cleanup error retains effect; CLI/report success never means scientific acceptance. |
| T17 | Duplicate keys, closed fields, malformed JSON, nonobject registries, unsafe paths, missing capture and truncated/incomplete history tests. |
| T18–T19 | Hidden fence/no-caller-support tests; exact equal A/B source projection and fixture scores. A/B uses one synthetic helper, not independent competing implementations. |
| T20 | Phase leakage, nested envelope, exact projection, extra-path checks and A/B byte-identity regression. Not a hostile-producer side-channel proof. |
| T21 | C4 before-request, acknowledgment linkage and same-effect-at-two-cuts checks; no uninterrupted-persistence claim. |
| T22 | Relabeling synthetic origin/study phase rejected. No claim to cryptographically authenticate a producer's provenance. |
| T23 | `test_reverse_wall_clocks_no_change`. |
| T24 | Causal graph rules never consult wall clocks; missing links fail schedule/capture checks. A fully isolated favorable-clock/no-order fixture is not separately saved. |
| T25 | Wrong run, wrong native start reference, unresolved observed binding tests. |
| T26 | `test_finally_not_worker_or_native`; permitted weaker-observation review regression. |
| T27 | `test_committed_effect_survives_lost_bridge_response`. |
| T28 | Fractional IDs, graph cycles, duplicate records, reserved graph namespace, huge-boundary and nonfinite parsing tests. |
| T29 | Missing capture/ack and pending-work mutations make absence unresolved. |
| T30 | `test_fake_fence_receipt_no_ledger`. |
| T31 | `test_unfavorable_claim_does_not_exclude`. |
| T32 | Production freeze/novel-native-tuple stopping remains unimplemented because no observed mappings or runtime driver exist. A synthetic mapping cannot qualify native execution. |
| T33 | Positive K cardinalities plus sink duplicate/missing/orphan cases. Not every K cardinality combination has its own end-to-end saved fixture. |
| T34 | `test_receipt_missing_ledger_fence_remains`. |

## Supplementary F01–F30

The original independent design is preserved in `provenance/INDEPENDENT_CHECKER_DESIGN.md`. F01–F05, F07, F09–F11, F13–F17 and F19–F30 overlap the implemented categories above. F06 (fully consistent effect/event removal), F08 (fully correlated reversed fence), F12 (dedicated native-timeout fixture) and F18 (isolated timestamp-only order fixture) are not separately instantiated as full end-to-end vectors. Their relevant accounting, graph, capture or unresolved-mapping rules exist, but rule existence is not an executed vector. Native-timeout and unexpected-native facts remain reported without qualification acceptance.

## v0.3 additions

Covered: C1 extra dispatch with zero effects; C4 extra dispatch with one effect; invocation without submission; no credit for always-unresolved output; missing phase not caller omission; queued/uncertain work; forbidden capture intervention; late same-dispatch commit versus unrelated later operation; outcome-independent analysis eligibility; exact denial cause; receipt-backed confirmation versus ledger existence; and phase-specific native observations.

The independent harness additionally exercises defects found during review. Its preserved initial failures and final result show corrections, not native experiments. No test denominator is pooled with the six-cell research plan.
