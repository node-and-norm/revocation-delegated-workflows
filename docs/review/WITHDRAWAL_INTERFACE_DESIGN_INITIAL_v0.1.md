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
