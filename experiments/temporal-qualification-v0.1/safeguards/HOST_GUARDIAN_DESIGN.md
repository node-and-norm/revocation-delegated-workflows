# Host guardian and independent exit observer

12 November 2026. **Concrete proposed design; not implemented or qualified.** This document adds no lifecycle, process-inspection, security-change or study-execution permission.

## Source-reviewed force-stop limitation

Lima v2.0.3 [`pkg/instance/stop.go`](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/instance/stop.go), `StopForcibly`, requests SIGKILL for the recorded driver and host-agent PIDs, logs signaling errors, attempts additional-disk unlocks and removes temporary files. It does not wait for those processes to exit and returns no error value to the caller. Cleanup failures may therefore be logged rather than propagated as a failed force-stop action.

[`cmd/limactl/stop.go`](https://github.com/lima-vm/lima/blob/v2.0.3/cmd/limactl/stop.go), `stopAction`, invokes that function and then network reconciliation when its error variable is nil. The reconciliation call receives an empty instance selector (`reconcile.Reconcile(ctx, "")`); its wider network side effects need source review. An exact stop target alone does not prove the entire CLI is profile-scoped or that shared/old-profile networking is unaffected. Any concrete lifecycle approval must disclose relevant disk-unlock, metadata-removal and network-reconciliation effects.

Thus a force-stop CLI exit code and later management status are not independent evidence that the original VM processes exited. Source review establishes this code path, not the behavior of an executed stop on this Mac. The installed-binary/source correspondence must be checked before qualification; a matching version label alone is not byte equivalence.

Do not run that CLI on the guardian's deadline-enforcement thread. Network reconciliation and other lifecycle work may block. A timeout around the CLI limits waiting by its caller, not necessarily VM lifetime or descendant cleanup.

## Proposed components

| Component | Responsibility | Must not do |
|---|---|---|
| Host guardian | Own immutable attempt deadline and admission state; consume bounded observer/control status | Block on startup, stop CLI, hashing, filesystem persistence or guest RPC |
| Independent host exit observer | Bind VM driver/host-agent identities and register OS exit notifications before admitting a workload | Infer exit from deleted PID files, absent sockets, a reused numeric PID or guest-written output |
| Supervised lifecycle worker | Make one approved exact-target stop request with reviewed wider side effects at the declared escalation point | Restart the VM, retry uncertain action, target the old/shared profile or broaden its target |
| Evidence writer | Persist bounded records and report save failure separately | Delay containment or make untrusted guest files authoritative |

The host guardian is outside the guest failure domain, not independent of host suspension, kernel failure or loss of host access. The dedicated VM is already running; observer registration must precede **test-attempt admission**, not be falsely described as having preceded this VM's startup.

## Fail-closed readiness contract

No workload launch unless every item is positively established for the same profile and attempt:

1. Exact profile/instance mapping is bound to `revocation-qualification-v01`; old profile excluded. No default-context inference.
2. Authorized host inspection supplies the relevant host-agent/driver process identities, executable association and lifetime identity. Numeric PID alone is insufficient.
3. A supported OS facility has registered exit observation for each required original process. macOS process-exit notifications (for example kqueue EVFILT_PROC/NOTE_EXIT) are a **candidate primitive**, not an availability or permission claim.
4. Registration/identity races are addressed: recheck identity after registration, reject mismatch/replacement/already-exited/unobservable state. Before dispatch, obtain an observer-ready acknowledgment bound to attempt, instance and identities. The precise race-free primitive sequence needs implementation review.
5. All processes whose continued operation could keep the VM/workload alive are identified. Observing two named PIDs alone is not proof the set is complete; confirm the installed driver's lifecycle architecture.
6. The supported lifecycle operation has an exact target and a separately supervised invocation path. It must not hold the guardian's progress loop hostage.
7. Guardian, observer and lifecycle worker have capped status channels, monotonic deadlines, bounded memory/output and explicit failure handling. Lost observer readiness blocks dispatch; lost observation after dispatch makes cleanup unresolved.
8. Configured resources, networking and host mounts meet the separately approved test scope; the current shared-network setup does not automatically satisfy a network-disabled workload plan.

The gate returns `not_ready` with named reasons for missing capability, denied inspection, identity mismatch, observation failure, unknown process coverage or unqualified lifecycle behavior. It does not fall back to success based on `Stopped`, an empty container list or a CLI exit code.

## Proposed state sequence

```text
NOT_READY → IDENTITIES_BOUND → OBSERVER_ARMED → ATTEMPT_ADMITTED
                                                   ↓
                    normal completion OR deadline/failure
                                                   ↓
             CLEANUP_REQUESTED → EXIT_OBSERVED or CLEANUP_UNRESOLVED
```

An observation of original process exit supports a narrow host-process claim. A separate argument and qualification must establish that the identified process set controls the entire VM and all in-scope workloads. Record requested stop, signal/CLI outcome, original-process exit observations, management status and workload evidence as different fields.

At the fixed cleanup cutoff, stop admitting further cases. Retain unresolved process/boundary ownership for operator recovery. No repeated stop, restart, kill-by-guessed-PID, disk unlock or metadata deletion is authorized by this plan. Killing a hung lifecycle helper is not evidence that it stopped the VM.

## Required records

Attempt and profile identity; installed tool versions/digests when available; approved target; identity-binding and observer-registration results; monotonic admission/escalation/cutoff times; one lifecycle request and its bounded output/exit status; OS exit observations tied to original identities; independent cleanup verdict; missing/late evidence and persistence failures. Redact private host paths from the repository; keep a locally controlled source record where needed.

## Why implementation remains blocked

The earlier process-inspection denial has not been retried or bypassed. Exact process identity access, supported exit-observer registration, complete VM process coverage and operational force-stop semantics are not verified. Source code for a guardian could be written without these facts, but would not make the environment ready and risks suggesting a safety guarantee it cannot establish. This increment therefore deliberately implements **no guardian executable or readiness gate**.

Next decision: obtain an explicitly permitted observation route with documented identity/exit semantics, review the exact bounded guardian implementation, and separately authorize its qualification. No lifecycle-stop tests or study tests occurred in this increment. Design acceptance, implementation, safeguard qualification and study execution remain separate decisions.
