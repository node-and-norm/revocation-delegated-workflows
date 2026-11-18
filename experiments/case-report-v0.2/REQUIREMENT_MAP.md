# Source-only requirement map

| Requirement | Candidate source | Boundary |
|---|---|---|
| REPORT-01 four panels | `report`, `render_html` | No global pass badge; intake failures leave all panels unknown |
| 02 scope | `extract` metadata; report `scope` | Saved terminal snapshot, not global execution window |
| 03 identity | `source_identity`, `validate_receipt`, explicit admission/grant/bootstrap joins | Namespace includes packet/case/archive/member; denial root is derived |
| 04 recorded vs derived | `say` classifications and source/rule fields | Input remains visible; no live-state inference |
| 05 uncertainty | caller classification independent of other panels | Caller unconfirmed never implies authority inactive |
| 06 coverage | category availability/coverage and effect inventory branch | Present-empty differs from unavailable; A6 positive entry survives unknown coverage |
| 07 conflict | grouped authority assertions | Same root/epoch/boundary conflict only; requests original records through specification |
| 08 provenance | strict packet/receipt schemas, immutable source pins, transformations | Constructed items labeled; trusted local custodian claims not authentication |
| No circular digest | `encode`, `digest`, `validate_receipt` | Hash full raw packet; receipt excluded |
| No hidden evidence | extractor explicit categories/event sequences | Workers/barriers/relay/execute_response never enter packet |
| No label-derived answer | report classifier | source_case used only in pinned identity validation and source labels |

## Source-inspection findings still requiring independent review

The spec fixes the high-level fields but not every nested type; this candidate
chooses exact field sets and explicit rejection rather than permissive fallback.
The extractor labels completeness only as completeness of the selected original
field/allowlist. That is newly authored packet metadata, not a historical capture
completeness claim. A6 explicitly withholds that metadata.

The test module is prospective source only. Its names are not passed-check claims.
A8a extraction-boundary coverage is deliberately not claimed. Read the README's
remaining limitations before approval of any execution.

## R1 source correction (not executed)

Repeated execute request IDs now prevent ambiguous result attribution; both effect
paths require effect kind/outcome agreement and payload agreement with the execute
request. Snapshot roots outside supplied bootstrap/grant roots are explicitly
unbound for the selected action while retained as supplied assertions. Missing
context does not invent an association. Same-boundary conflicts request original
records and provenance clarification. Five prospective regression methods cover
these changes. They have not been run.

## R2 source correction (not executed)

Effect evidence is deduplicated by packet/case/archive/member namespace and the
local event sequence/root/epoch/effect-key tuple, not by item ID. Copies remain
visible with a `duplicate_evidence` label. A6's lower bound counts distinct matched
effect identities, while the inventory entry count explicitly includes duplicate
evidence. One prospective regression method preserves two copies and expects one
distinct identity. It has not been run. This is bounded local identity handling,
not general semantic deduplication or proof that event IDs are globally unique.
