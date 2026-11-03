# Withdrawal interface qualification: proposed implementation specification

Status: reviewed design only. No implementation or collection has occurred. Historical rationale and reviewer corrections are preserved in DESIGN.md and DESIGN.initial.md.



The initial design is preserved as `DESIGN.initial.md`. Six review findings are addressed below. No execution has occurred.

### 1. Authority and request correlation

The unchanged gateway has one fixed rootR, active epoch 7, and a revoke operation that unconditionally installs epoch 8/inactive. It does not validate root or epoch fields supplied in a revoke request, and its reply does not echo the request ID. This experiment therefore has exactly one outstanding withdrawal for that fixed synthetic authority per fresh sink. The relay owns the request ID and forwards it as the gateway request's `id`. The custodian checker correlates that ID with the gateway's committed receipt and revocation outcome. The caller receives a relay response associated with the sole outstanding request. Correlation and truthful relay behavior are assumptions qualified in this bounded fixture, not generic sink enforcement of arbitrary target bindings.

Caller validation requires returned rootR, withdrawn epoch 7, new epoch 8, local-sink scope and the pending request ID. Wrong-target or wrong-epoch mutations test caller/checker rejection. They do not establish that the unchanged gateway rejects incorrectly targeted revoke requests.

### 2. Caller evidence boundary

Implement a separate caller module that receives only these messages:
- An acceptance response from the relay: request ID and `accepted_volatile`.
- A terminal completion envelope, when the schedule releases it: request ID, rootR, withdrawn epoch 7, new epoch 8, `installed`, `single_local_sink`, and the actual gateway response retained by the relay.
- The caller's declared observation-end signal.

The caller cannot read the sink database, relay-private log, controller scenario name, expected outcome, framework's protected-action result or privileged barrier records. The checker can read all those artifacts after the run. The relay generates a completion envelope only after receiving the actual gateway revocation response. It must validate that response's exact root and epoch contents. Envelope fields are fixture provenance, not a signed remote certificate.

### 3. Caller state machine

States: IDLE, PENDING, INSTALLED_CONFIRMED, UNCONFIRMED_AT_OBSERVATION_END, INVALID_RESPONSE.

- Local request issue creates PENDING before any acknowledgment.
- Acceptance is volatile relay receipt. It keeps PENDING and promises no durability or restart recovery.
- A matching, correctly scoped completion envelope changes PENDING to INSTALLED_CONFIRMED.
- End of observation while pending becomes UNCONFIRMED_AT_OBSERVATION_END.
- A mismatched or malformed completion becomes INVALID_RESPONSE and cannot establish installation.

Terminal caller states are absorbing for the finite observation window. Late and duplicate completion responses after terminal observation are excluded from this version and cannot revise the recorded result.

A failed/absent acceptance does not establish that the sink has or has not installed a fence. No timeout is interpreted as cancellation completion. No restart of the caller, relay or gateway is in this matrix. Every transition and visible input is recorded for independent checking. The caller does not declare rollback of prior effects or cessation of all computation.

### 4. Committed ordering and response withholding

The scheduler releases explicit relay and execution barriers. Gateway pipe-send time is recorded only as intent. Authoritative sink ordering comes from committed SQLite events. Gateway receipt and revocation outcome are visible together after their transaction commits. The scheduler's privileged observer waits for a matched committed receipt/outcome pair before it releases any barrier labeled 'after fence'. A committed gateway execute receipt and matching terminal outcome establish that the execute call reached the gateway. Worker output supplies additional framework-propagation evidence and is insufficient by itself.

Rename the earlier 'lost completion' case to `completion_withheld_at_relay`. In this case the relay actually receives the gateway's response and withholds forwarding to the caller through the terminal observation. No claim of genuine network loss, unavailable relay evidence or crash is made. A genuinely lost gateway-to-relay response remains a separately proposed fault model and is excluded from this version.

### 5. Frozen proposed collection matrix

Every schedule has two paths: direct reference and native framework checkpoint resume. Six schedules times two paths give 12 fixed candidate runs. Every run uses a fresh SQLite sink, one parent-to-child grant, one valid ticket, no prior effect, exactly one resumed execute attempt, and at most one withdrawal. Direct and framework paths share the adapter/gateway; they are matched conformance controls, not independent implementations of the security mechanism.

| Schedule | Required authoritative sequence | Execute result | Effect count | Caller state at observation end |
|---|---|---|---:|---|
| S0 live | No withdrawal; execute commits | effect | 1 | IDLE |
| S1 confirmed-before-resume | Revocation commit; completion delivered; execute | revoked denial | 0 | INSTALLED_CONFIRMED |
| S2 request-held | Caller request/volatile acceptance; execute commits; revocation delivered and committed; completion delivered | effect | 1 | INSTALLED_CONFIRMED |
| S3 response-held-until-after-resume | Revocation commit; execute; completion then delivered | revoked denial | 0 | INSTALLED_CONFIRMED |
| S4 completion-withheld-at-relay | Revocation commit; relay receives response; execute; caller observation ends without completion | revoked denial | 0 | UNCONFIRMED_AT_OBSERVATION_END |
| S5 delivery-withheld | Caller request/volatile acceptance; execute; observation ends before gateway receives withdrawal | effect | 1 | UNCONFIRMED_AT_OBSERVATION_END |

S2's one effect precedes the fence and remains present afterward. S5 has no fence within the observation window. Both must require the effect, rather than merely permit it, to demonstrate that the action path remained live. S3 additionally records the caller as PENDING during the already-fenced execute and only confirms after delivery. Shut down after final capture; cleanup cannot retroactively change the declared observation window.

### 6. Non-tautological qualification and decision gate

The schedule selects event order; that alone is not a research result. The implementation under test is the independently implemented caller's state transitions and the native workflow's propagation of exact gateway outcomes under the restricted observation interface. The checker must derive expected states from caller-visible evidence, and derive effect classifications separately from authoritative sink evidence. It may not import the caller transition function or accept stored pass/fail flags.

The qualification must show discrimination through mutations: early complete on acceptance; matching ID with wrong root/epochs; completion for unknown ID; malformed installed response; caller privileged-database access; missing execute receipt; missing effect in S0/S2/S5; post-fence inserted effect; dropped framework output; and mismatched observation cutoff. Some access checks require structural code review as well as trace tests. A negative control using deliberately premature completion is labeled an authored diagnostic control, never a framework default.

## Implementation plan and approval gate

1. Preserve historical source hashes and build in a new sibling workspace. Copy unchanged gateway and workflow into a versioned candidate package with hashes.
2. Implement relay, caller and scheduler modules separately. Keep private scheduler state out of caller arguments and messages. Add read-only database observation for committed barriers.
3. Write an independent checker with separate caller-knowledge, sink-effect, framework-path and completeness verdicts.
4. Qualify module transitions and all negative controls. Preserve failed qualification logs and corrections.
5. Obtain a separate source/contract review checking target-binding limits, evidence separation, ordering, scope and no hidden answer leakage.
6. Freeze source and protocol hashes before any measured collection. Execute 12 fixed runs only after the parent coordinates authorization and the qualification gate passes.
7. Report case-level conformance, exact uncertainty states, failures and limitations. Exclude exposure probability, production latency, distributed closure, arbitrary crash recovery, novelty and deployment-readiness claims.

The immediate prepared artifact is this corrected design. No implementation or measured collection is represented as complete.
