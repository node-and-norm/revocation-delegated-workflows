# One graceful-stop observation: operation and evidence contract v0.1

> **Source-review correction (12 November):** “no force” in the proposed VM operation means no requested forced VM shutdown. Ordinary Lima graceful-stop reconciliation may SIGKILL the user-v2 network helper after its polling threshold. This possible effect is not authorized merely by earlier graceful-stop wording. See [lifecycle source map](LIFECYCLE_SOURCE_MAP.md); the later active-state observation below narrows autostart and one helper identity, without closing effective configuration or lifecycle gates.


12 November 2026. **Proposed specification, independently AI-reviewed as noted in verification; not implemented, tested or permission to operate.** Read alongside [supervisor source review](SUPERVISOR_SOURCE_REVIEW.md). Current decision: **NOT READY**.

## 1. Exact bounded question

For one expressly approved graceful stop of the otherwise empty dedicated VM, can an independently armed host observer record exit of the freshly bound VM-host process within a 30-second observation window, while separately reporting command outcome, evidence completeness and cleanup?

Target: `revocation-qualification-v01`, Lima instance/context `colima-revocation-qualification-v01`. Candidate command shape: installed, reviewed `limactl stop` with that exact instance and **no force flag**. This is a specification, not an instruction to run it. No automatic retry, force-stop, restart, workload, settings change or merge. A stopped VM is not automatically restarted for convenience.

The command can reconcile shared networks. The last separately reported configuration contained only `user-v2`, with this VM the only listed running consumer. Thus stopping the VM may stop the now-unused shared service. These are historical inputs: fresh inventory and effective configuration binding are mandatory before any later approved attempt. Never promise no shared effects from an exact instance argument alone.

## 2. Gate ledger: all mandatory, no scoring away unknowns

| Gate | Required record | Current status |
|---|---|---|
| G1 authority | Owner's concrete operation approval and separately explicit owned-worker cleanup policy; scope, time and target | Future execution approval required |
| G2 active configuration | Exact installed version/source correspondence; config-resolution chain; effective instance/network values; immutable review identity | Unresolved binding, not solved by supplied hashes |
| G3 identity and concurrency | Fresh process lifetime identity, observer registration/recheck; exclusive lifecycle ownership or an explicitly accepted residual race model | Targeted registration previously succeeded; exclusivity and races unresolved |
| G4 helper ownership | Complete source-derived actor graph, permitted cleanup target and observed completion condition for each actor | Existing detached user-v2 identity reported; fresh dual observation, shared effects and cleanup still unresolved |
| G5 evidence custody | Reviewed bounded writer protocol with receipts, quotas, incomplete states and preservation path | Contract below only; writer unimplemented |
| G6 implementation | Corrected source, independent review and separately authorized qualification of relevant mechanisms | Local source held closed; unexecuted |

Any `unknown`, `conflict`, `denied`, `missing` or `stale` gate blocks admission. Prior process-registration and one cooperative child-event check satisfy neither full G3 nor G6. No configuration field or command-line flag counts as owner authorization.

## 3. Effective configuration and identity binding

The review packet must include:

1. Absolute installed executable identities, versions and byte digests. Explain how invoked paths, symlinks and wrapper behavior select those exact executables. A version string alone is insufficient.
2. The **actual resolution chain** for Lima instance configuration, global network configuration, Colima profile, applicable environment variables and inherited defaults. Derive it from the installed version's source and saved effective configuration, not from a caller's three arbitrary path labels.
3. For each source: role, resolved local identity, byte digest, observation time, effective values it contributes and redacted repository locator. Preserve necessary private host paths only in the controlled local packet. Reject aliases and missing roles; distinct files alone do not prove active roles.
4. Fresh complete instance inventory, explicit Docker-context identity, empty container/image lists and the dedicated mount/network facts. No `default` context assumption.
5. Process lifetime identity: numeric PID, owner, executable association, start-time identity, registration result and unchanged recheck. Record host-agent/driver records referring to the same process as one process, not two witnesses.
6. A concurrency declaration identifying who can change profile/network state during the attempt. Rechecks narrow a race; they do not eliminate it. If exclusive ownership cannot be established, state the residual race and obtain a design decision rather than claiming a race-free binding.

No current check is requested here. The earlier authorized narrow inspection is historical. No denied process listing or alternative syscall workaround is permitted by this contract.

## 4. Actor and side-effect ownership map

| Actor | Candidate owner | Allowed action in a future approved attempt | Required completion evidence / open question |
|---|---|---|---|
| Host guardian/observer | Research supervisor | Observe, classify, close observer | Exact registration/closure and preserved record; host failure remains outside claim |
| Direct lifecycle worker which execs CLI | Research supervisor | One graceful-stop request; direct-worker cleanup only if specifically approved | Direct child exit/reaping; termination may interrupt shutdown, not undo it |
| Dedicated VM-host process | Lima/host lifecycle machinery | Request graceful shutdown through approved CLI only | Native event tied to original identity; not process-tree-wide proof |
| CLI-created subprocesses | **Unresolved** until complete source map | No blanket group kill or guessed-PID cleanup | Who creates/reaps each helper? Can it survive worker exit? Missing answer blocks G4 |
| Shared `user-v2` service | Lima network manager; shared resource | Only reviewed and explicitly disclosed reconciliation effects | Exact consumers and supported status evidence; not inferred from VM event |
| Other profiles/host services | Outside test scope | No deliberate action | Wider reconciliation effects must be mapped; unexplained effect blocks admission |
| Evidence writer/storage | Separate supervised writer/custodian | Bounded persistence, no influence over stop outcome | Sequence/digest receipts and independent final verification |

Source anchors: [Lima 2.0.3 stop orchestration](https://github.com/lima-vm/lima/blob/v2.0.3/cmd/limactl/stop.go), [instance shutdown](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/instance/stop.go), [global network reconciliation](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/networks/reconcile/reconcile.go). Follow their actual helper call chains before declaring this map complete. This contract does not fill unknown ownership with an assumed process group.

## 5. Minimal immutable attempt-record schema

| Record | Mandatory fields |
|---|---|
| `attempt_plan` | schema/version, unique attempt ID, target/profile/context, approved source/config identities, authorization reference, fixed budgets, expected shared effects, gate ledger |
| `preflight` | exact read-only operations and outputs/limits, observed inventory, effective-config bindings, binary identities, timestamps, conflicts/missing records |
| `observer_ready` | attempt ID, original process lifetime identity, registration/recheck results, observation scope and unresolved coverage |
| `release_attempt` | sequence and monotonic timestamp **before** release write; delivery state: not-attempted / attempted-uncertain / byte-written-not-execution-ack |
| `exit_observation` | original identity, event type, retrieval monotonic time, cutoff, classification: within-window / late / no-event-observed / observation-lost; no invented exact exit time |
| `cli_result` | exact argv identity, start/exec status where knowable, exit status or unresolved, stdout/stderr kept separate, truncation/EOF/completeness |
| `cleanup` | each permitted action, exact owned target, reason, result, reaping/observer closure, errors, unknown descendants and shared-service state |
| `evidence_receipt` | attempt ID, source sequence range, byte count/digest, durable-save status and acknowledged boundary |
| `final_disposition` | separate process-observation, CLI, direct-worker cleanup, shared-service and evidence statuses; open gates; no aggregate qualification pass |

Every event carries attempt ID, producer identity, producer-local sequence and monotonic clock domain; UTC is descriptive. Do not compare unrelated monotonic clock domains. Missing records remain explicit. An exit observed after a stop request is not by itself causal proof the request caused it.

## 6. Bounded evidence-writer contract

Proposed initial limits: 1 MiB per CLI stream, 10 MiB total persisted attempt data, bounded in-memory event queue of 256 records, maximum serialized event 16 KiB. These are design values, not tested capacity. Combined memory/storage maxima must be reviewed before implementation; reserve space for final failure metadata rather than allowing logs to consume the whole budget.

- Guardian enqueue must be nonblocking. Writer startup/storage setup occurs before admission and separately from the timed observer path.
- A writer acknowledges a precise sequence range and digest only after the declared persistence step. Define whether that step includes file flush, fsync, atomic rename and directory durability; do not call a mere queue receipt durable.
- The review-approved plan and readiness evidence must have acknowledged preservation before release. `release_attempt` must be submitted before the write; if its preservation cannot be established within the predeclared admission budget, do not release. No synchronous storage wait may block the guardian's timed enforcement loop.
- Queue full, oversized record, write failure, missing receipt or timeout sets `evidence_incomplete`. Do not block, extend the observation deadline or replace lost content with reconstruction. Preserve a bounded failure marker if possible; if even that fails, report evidence loss outside the attempt record.
- Raw output is capped separately by stream. Retain prefix/tail policy only if predeclared and label omitted bytes; never present truncated output as complete. EOF, process exit and successful save are different facts.
- The writer must not inherit guest authority or accept guest files as guardian truth. Hashes prove byte identity, not authenticity or completeness.
- After observation, custody review checks sequence continuity, receipts and file digests. Late evidence remains late. Writer cleanup and orphan recovery need their own ownership plan; a hung writer cannot extend VM observation or become an excuse to run another case.

## 7. Timing, cleanup and outcomes

Pre-arm observer and separately supervised lifecycle worker before admission. Record T0 when the guardian creates/submits the release-attempt intent, before any release-byte write; cutoff T0+30 seconds. Await its durable receipt asynchronously while observation/deadline handling remains responsive. Dispatch is forbidden unless the receipt arrives before both the declared admission cutoff and T0+30 seconds. Do not reset T0 after receipt: persistence latency consumes the original window. A missed receipt/cutoff means no release, retained failure evidence and cleanup of the unreleased owned worker under its approved policy. Record actual write-attempt time separately; a saved intent does not prove a write or execution. This is an observation window, not a hard OS guarantee. Classify by event **retrieval** time after the OS call; at/after cutoff is late.

No requested forced VM shutdown, additional helper kill or restart. Lima’s disclosed built-in helper escalation remains possible. Direct-worker termination, if separately approved, targets only the owned child; it may interrupt graceful shutdown and leave helper/shared-service state unresolved. A successful kill/reap of that child is not proof the VM or helpers stopped. Unknown ownership or unresolved cleanup prevents subsequent attempts. The final report must survive individual close/cleanup failures and retain the primary failure.

A no-event-observed label means only that no matching event was received; it never means the process is absent.

No single green label: report `vm_process_exit_observed`, `cli_status`, `direct_worker_cleanup`, `shared_service_state` and `evidence_completeness` separately. The most favorable result supports only the narrow original-process observation for this case, not full guardian or containment qualification.

## 8. Reviewer acceptance checklist and next smallest step

Before any implementation/test proposal, the reviewer must identify a concrete source/evidence answer for each gate, every helper in the call chain, the active-config resolution chain, each record's producer and each failure's bounded disposition. Unanswered items remain no-go conditions.

**Next smallest design-only step:** finish the source-derived helper/side-effect map and configuration-resolution chain for the installed versions. This can establish which actors need ownership and which files really govern operation without stopping the VM or running tests. In parallel, specify the evidence-writer receipt protocol; do not claim it implemented.

Genuine progress here is an explicit reviewable contract replacing vague readiness claims. None of the four blockers is marked closed by writing this document. Publication of this documentation in the private draft does not approve execution, code upload, merge or security changes.

## 9. Active-state refinement (12 November)

On 12 November 2026, the separately authorized environment review reported `status=Running`, `AutoStartedIdentifier=""`, and `errors=[]` for the dedicated instance. Under the reviewed v2.0.3 source, that inspected state selects direct host-agent SIGINT rather than `launchctl bootout`. This resolves the previously unknown branch **at that observation only**; recheck before any future action.

The existing user-v2 PID file identified PID 6394. A targeted permitted identity check found current-user ownership, the resolved installed limactl executable, parent PID 1 and start time 1794515880.707602; the PID file remained stable. The VM-host PID was still 6396. These are historical identity observations, never constants to reuse as current targets. Executable/path/owner evidence is not argument attestation, complete actor coverage or lifecycle success. No signals, observer registration, tests or settings changes were performed in this preflight. This document is a sanitized account of the environment review's tool observations, not a preserved raw transcript.


Use the [three-outcome proposal](LIFECYCLE_SOURCE_MAP.md#simplified-proposal-observe-three-distinct-outcomes): separately observe the original VM-host, preexisting shared helper and CLI. No broad process-tree termination is proposed. The earlier next-step map is now available; next review dual-observer admission/failure behavior and evidence persistence, while keeping execution disabled. The four gate categories remain unresolved, though autostart and one helper identity are better evidenced.

## Persistence acknowledgment is not a power-loss guarantee

Source review, 13 November 2026. Separate two failure models:

| Failure model | Narrow claim allowed | Not established |
|---|---|---|
| Supervisor process fails while host remains available | A previously acknowledged, preserved snapshot may be recoverable; unsaved RAM records remain unknown | Complete dispatch or outcome history after a crash |
| OS crashes or host loses power | Record which persistence operations returned and their exact receipt scope | Survival of file contents, ordering and directory entries on this Mac |

Apple's archived [fsync manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fsync.2.html) warns that flushing to a drive does not establish that its internal buffers reached permanent storage. Its archived [fcntl manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fcntl.2.html) describes F_FULLFSYNC as a stronger flush request, but notes possible long completion times and hardware that ignores it. These historical documents do not verify current macOS, APFS, drive or mounted-filesystem behavior.

Design rule: call a receipt **acknowledgment of specified persistence operations**, not “power-loss durable.” Declare file flush, replacement and directory synchronization separately. Supported directory-entry persistence and rename behavior remain platform questions; neither a hash nor successful file synchronization proves them. Keep storage work outside the observation/cleanup deadline path. Do not add F_FULLFSYNC calls or change the accepted contract without separate implementation review.

The RAM-first alternative intentionally permits loss of unsaved observations if the supervisor fails. It has not replaced the stronger pre-release persistence contract or been authorized as an experiment.

Related issue [Lima #5087](https://github.com/lima-vm/lima/issues/5087) reports a LaunchDaemon/reboot scenario on Lima 2.1.1 plus development changes. It is a lead for version-specific review, not evidence the inspected Lima 2.0.3 VM is affected. No workaround, forced shutdown or restart is proposed from that issue.

No tests, VM operations or persistence qualification were performed for this addendum.

