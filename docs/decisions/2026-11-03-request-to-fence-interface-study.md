# Request-to-fence interface study v0.1

Date: 2026-11-03 UTC  
Research owner: Mark Julius Banasihan  
Status: measured collection complete; separate AI-assisted post-run audit passed.

## Decision and purpose

Preserve this bounded execution study as a separate extension of the existing revocation integration pilot. It examines the caller-visible withdrawal interface across request acceptance, sink-side fence installation and completion delivery. The retrospective packet exercise remains complementary and has no completed reviewer evaluation.

The useful distinction is operational: an accepted withdrawal request, an installed fence and a completion message reaching the caller are separately observed events. This distinction is established systems reasoning. These results document how the local instrument implements and reports it under six fixed schedules.

## Evidence and results

| Schedule | Observed effect and caller state in both arms |
| --- | --- |
| S0: live control | One effect; no withdrawal; caller IDLE. |
| S1: fence and completion before execution | Revoked denial; no effect; caller INSTALLED_CONFIRMED. |
| S2: request held before sink delivery | One effect before the fence; later completion confirms installation. The earlier effect remains. |
| S3: completion held until after resume | Execution denied after fence installation while the caller is PENDING; later completion confirms installation. |
| S4: completion withheld at relay | Execution denied after installation; caller UNCONFIRMED_AT_OBSERVATION_END. |
| S5: request delivery withheld | One effect; no fence within the observation window; caller UNCONFIRMED_AT_OBSERVATION_END. |

All 12 fixed cases passed their declared checks: six effects and six revoked denials, with no post-fence effects. The direct reference and native checkpoint/resume paths share the adapter and gateway. They are matched integration controls. Each native resumed worker used a distinct process, and the final supervisor message preserved the actual sink disposition.

S4 and S5 end with the same caller knowledge state and different sink states. That supports explicit uncertainty in the tested interface. It does not establish a new principle, a production failure, an empirical failure rate or a general claim about AI behavior.

## Preserved records

- [Frozen candidate v0.2 protocol](../review/WITHDRAWAL_INTERFACE_PROTOCOL_v0.1.md)
- [Measured 12-case summary](../review/WITHDRAWAL_INTERFACE_SUMMARY_v0.1.json)
- [Separate AI-assisted post-run audit](../review/WITHDRAWAL_INTERFACE_POSTRUN_REVIEW_v0.1.md)
- [Reproduction and read-only verification instructions](../review/WITHDRAWAL_INTERFACE_REPRODUCTION_v0.1.md)
- [Complete source, qualification and measured-record archive](../../archives/withdrawal_interface_study_v01_20261103.zip)

The four readable documents above are byte-identical copies of the archive records. Relative paths inside those frozen records refer to the extracted archive. Extract the full archive for code, dependencies, raw events, databases and internal references.

Archive SHA-256: `adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c`. All 231 entries in its internal manifest were checked before repository preservation. The manifest detects byte changes; it does not attest independently to execution or establish authenticity of a remote provider.

## Qualification and corrections

The package retains earlier diagnostic failures and their corrections. Direct-path handling was aligned with the shared execution adapter. Partial failure capture and cleanup were corrected. Epoch validation was tightened to reject floating-point values, including in relay completion handling. A separate checker schema issue was corrected explicitly. Qualification includes 14 module/failure tests, 12 corrected schedule cases and 40 targeted rejected mutations. These are overlapping engineering checks.

Frozen candidate v0.2 adds measured-collection metadata and the collection flag to the qualified candidate. The archive preserves both versions and their hashes. Some frozen protocol and correction text describes its earlier qualification-stage status; `measured01/SUMMARY.json` and the post-run review record the later completed collection. Historical files remain unchanged. The archive omits historical design files that were stored outside its package root. After the initial repository preservation, the builder located them and their checksums were verified. This corrects the earlier note describing those references as unavailable. They are preserved separately as [initial design](../review/WITHDRAWAL_INTERFACE_DESIGN_INITIAL_v0.1.md), [revised design](../review/WITHDRAWAL_INTERFACE_DESIGN_v0.1.md) and [implementation specification](../review/WITHDRAWAL_INTERFACE_IMPLEMENTATION_SPEC_v0.1.md). These are historical planning records; the frozen protocol and measured records establish the executed scope. The original archive remains byte-identical.

## Interpretation boundaries

This is a synthetic, local, deterministic study with scripted model responses, one root, one delegation edge, one valid ticket, one execution attempt and at most one outstanding withdrawal. The sink, host and controller are trusted. The gateway remains alive across graceful worker restart. The relay deliberately withholds messages. No arbitrary network-loss, caller/relay/gateway crash recovery, late-message handling, global closure, production readiness, model behavior or novel protocol claim follows.

The underlying gateway does not validate the root/epoch fields of the revocation request or echo the request identifier. Correlation relies on the fixed-scope, single-outstanding-request fixture. The completion envelope is fixture provenance, not a signed remote certificate. Caller observations are kept separate from sink and controller records.

The measured run manifest records commands and environment details after collection. It is a reproducibility record rather than an independent execution attestation. The post-run audit is separate AI-assisted review, with no claim of organizational independence or human validation. Repository preservation performed checksum and document checks only; it did not rerun the study.

## Disclosure and next decision

AI assistance covered design, implementation, checking, review and documentation. Failures and corrections remain available in the archive. [Workbook v0.5](../traceability/Revocation_AI_Use_and_Research_Decision_Traceability_v0.5.xlsx) records the qualification, corrections, freeze, measured collection and post-run review. Earlier workbook and operating-stack records retain their historical dates. Venue-specific disclosure requirements require checking before any submission. No universal AI-disclosure standard or publication approval is claimed.

The next research decision is whether a narrowly specified extension adds practical information beyond these fixed schedules and existing revocation/recovery work. Additional experiments, human review and public claims require their own documented scope and approval. The current evidence supports the tested interface and its explicit uncertainty states.

## Separate local reproduction

A subsequent execution reproduced all 12 fixed cases in a fresh isolated virtual environment on the same host/runtime, using the unchanged frozen checker and an existing local wheelhouse. The 14 module/failure-preservation tests passed. Deterministic fields matched the original cases; generated process and checkpoint identifiers were checked for correct linkage rather than byte equality. The 40 historical mutation checks were not rerun.

The [local reproduction report](../review/WITHDRAWAL_INTERFACE_LOCAL_REPRODUCTION_v0.1.md) and [reproduction evidence archive](../../archives/withdrawal_reproduction_evidence_20261103.zip) preserve commands, environment verification, new records and databases. This is a separate execution of the same instrument, with the same trust boundary and checker. It provides no independent implementation, cross-host replication, enlarged statistical sample or production assurance. The wheelhouse lies outside the original study archive.

Reproduction archive SHA-256: `b6e73bc4bffe5b1ff2e56f8d363750ea2d2227f08ce719b83da3fdc2be298035`. The original study archive remains unchanged. Workbook v0.5 predates this reproduction and remains intact. [Workbook v0.6](../traceability/Revocation_AI_Use_and_Research_Decision_Traceability_v0.6.xlsx) adds the reproduction record.

## Protocol-first artifact audit

A separately authored AI-assisted checker audited the 12 saved measured cases from the frozen protocol and selected raw JSON/SQLite evidence. Its report records no use of the original implementation or checker. All 660 baseline and 78 supplemental assertions passed. All 20 artifact mutants were rejected: 15 initial controls and five coordinated controls that preserved snapshot consistency while violating the tested semantics. These counts describe engineering checks over the existing collection.

The [audit report](../review/WITHDRAWAL_INTERFACE_PROTOCOL_FIRST_AUDIT_v0.1.md) and [complete audit package](../../archives/withdrawal_protocol_first_audit_20261103.zip) preserve code, captured outputs, input provenance and selected source records. Extract the package and run the documented audit commands from its parent directory. The package excludes generated Python bytecode; source files and the supplied checksum manifest are unchanged.

The audit ran on the same host and used the same study evidence. It provides a separately implemented artifact checker, with no new collection, human validation or independent implementation of the authority mechanism. It did not inspect checkpoint databases or establish runtime caller access isolation. Agreement among recorded artifacts does not establish recording authenticity. The earlier reproduction and this artifact audit are separate activities.

Archive SHA-256: `20e0b69db2109e862e6d94c1a3697670b760ec62712ae7cee4ddff2fd8dd7a61`. The audit's supplied manifest has 48 verified entries. Original study and reproduction archives remain unchanged. [Workbook v0.7](../traceability/Revocation_AI_Use_and_Research_Decision_Traceability_v0.7.xlsx) records this audit; earlier versions remain historical snapshots.
