# Proposed execution-grounded extension: withdrawal request to protected effect

Status: design proposal, 2026-11-03. No new execution or model calls. Existing v0.3 remains unchanged.

## Question and reason

What can a caller establish about protected effects between issuing a valid withdrawal request and receiving confirmation that the relevant sink fence is installed?

The existing v0.3 controller waits for the gateway's completed revoke response before resuming the worker. `runner.py` calls `call(control, revoke)` synchronously, then starts the resume worker. The gateway updates authority, records revocation and commits before sending its response. That design tests execution after a completed local fence. It does not sample effects while the request is delayed or while the completion response is unavailable.

The proposed next step retains the actual supervisor/subagent checkpoint-resume path and trusted local effect sink. A controlled relay separates request submission, gateway delivery, durable installation and response delivery. Barriers establish event order. Delays are selected test schedules, not measured deployment latency.

## Three claims to keep separate

1. Request accepted: a controller recorded the request and promised to process it.
2. Fence installed: the sink committed withdrawal of the relevant root/epoch.
3. Completion observed: the caller received evidence of that installation and its declared observation scope.

An effect after request submission but before installation may conform to the declared fence-based contract. It demonstrates a caller-visible exposure interval; it is not automatically an enforcement defect. An old-authority effect after the sink fence violates the existing local contract.

## Small fixed schedule proposal

| Case | Ordered events | Expected interpretation |
|---|---|---|
| Live control | Resume without withdrawal | One authorized effect; worker completes |
| Existing fence control | Deliver withdrawal; commit fence; deliver completion; resume | Revoked denial; no new effect |
| Delayed request | Accept withdrawal at relay; hold delivery; resume and commit effect; deliver withdrawal | Pre-fence effect despite earlier request; completion must not promise rollback |
| Delivered request | Accept/deliver withdrawal; commit fence; resume before completion response reaches caller | Revoked denial; caller still lacks delivered completion |
| Lost completion | Commit fence; withhold completion response through observation end; resume | Enforcement holds; caller status stays unconfirmed rather than claiming failure or success |
| Failed delivery | Accept withdrawal; no gateway delivery through declared observation end; resume | Possible authorized effect under old sink state; request remains pending/unknown |

Optional future cases include caller retry of the same request, relay restart and independent authority. They should be separately specified before collection.

## Comparison and boundaries

The execution-control comparison must retain a competent local atomic-fence baseline. The relay changes evidence visibility and schedule, not the gateway's correctness policy. A diagnostic caller that labels request receipt as complete can illustrate a reporting defect; it must be labeled a deliberately weak authored control. The main comparator should acknowledge completion only after a verified durable fence response, retain request identity and preserve unknown status after response loss.

This is an integration qualification and applied replication. Root-scoped quiescence already separates cancellation, root cuts, local fences and manifested closure. Permission to Retry already separates permission, external effects, retained observations and unresolved recovery. The extension would establish how this specific native workflow and caller interface preserve those distinctions, if the apparatus qualifies. It would not establish a new revocation mechanism or general novelty.

## Minimal instrumentation

- A stable withdrawal request ID bound to root and withdrawn epoch.
- Controller/relay events for accepted, delivered, completion-observed and terminal-observation events.
- Existing authoritative SQLite effect and fence ordering.
- Framework checkpoint ID, interrupt ID, worker PID and exact action binding.
- Separate attempt disposition, operation history, fence state and caller knowledge.
- A declared event relation between relay scheduling barriers and gateway receipts. Do not infer ordering solely from cross-process wall clocks.
- Raw failures and missing acknowledgments preserved before checking.

The relay must neither silently discard the execute path nor prevent the framework from reaching the gateway. Matched live controls detect those alternatives.

## Checker obligations and negative controls

The checker independently reads the sink database and relay records. It rejects post-fence old-authority effects, unsupported completion claims, mismatched request/epoch bindings, overwritten unknown statuses and absent framework attempts credited as safe denial. It preserves a pre-fence effect even when the later resumed attempt is denied. It must distinguish deliberately withheld evidence from naturally missing evidence.

Before collection, qualify mutations: early completion label; deleted fence receipt; wrong root/epoch; inserted post-fence effect; absent execute attempt; failed live control; sequence relation without a matching barrier. Failure of the apparatus is a stop condition.

## Go/no-go

Proceed only after a frozen protocol states caller contract, schedule ordering, expected dispositions and evidence boundaries; a reviewer verifies the mapping to the unchanged gateway and native workflow; and the relay/checker pass qualification. Stop if the result would merely restate the schedule without testing a meaningful caller contract. A later production adapter would need its own scope, authorization and correspondence checks.

## Sources and inspected local artifacts

- `revocation_integration_pilot_20261103/integration/v0.3/PROTOCOL.md`
- `revocation_integration_pilot_20261103/integration/v0.3/runner.py`
- `revocation_integration_pilot_20261103/integration/v0.3/workflow.py`
- `revocation_integration_pilot_20261103/qualification/v0.2/gateway.py`
- https://arxiv.org/html/2609.21284v1
- https://arxiv.org/html/2610.31916v1

No remote credentials, actual mail, model API, participants or external writes are needed for this local candidate. Additional implementation and execution should be coordinated with the research lead before beginning.

## Historical overlap check

The v0.2 qualification README already includes C2, effect commit followed by revocation followed by a late explicit application acknowledgment. It states that the gateway response itself was received normally. The proposed relay schedules therefore must preserve the distinction: they would withhold actual delivery of the revocation request or fence-completion response, rather than merely delaying an application acknowledgment. Existing C1/C3 already cover post-fence stale execution; repeat them only as controls, not new findings.

## Revision 1: implementation contract after independent design review

This section supersedes ambiguous implementation language above. The initial document is preserved as `DESIGN.initial.md`. Six review findings are addressed below. No execution has occurred.

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
