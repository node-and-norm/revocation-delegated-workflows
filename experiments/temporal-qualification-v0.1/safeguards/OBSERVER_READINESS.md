# Narrow observer-readiness check

12 November 2026, **21:02:28.109010 UTC**. This record is a sanitized summary of the separately assigned environment reviewer's tool observations, supplied to the coordinator. No persistent raw artifact was written by that check; this is not an independently signed or independently reproduced transcript.

## Explicitly bounded action

The owner authorized a targeted identity and observer-registration readiness check for the dedicated `revocation-qualification-v01` VM. It did not authorize stopping the VM or running a workload/study test. The earlier broad process-inspection denial was not retried or bypassed; no broad process listing was performed.

## Reported observations

1. Read the dedicated instance's `ha.pid` and `vz.pid` records; both identified the same process, PID 6396, in this observation. Two matching files are not two independently observed processes or proof of a complete process set.
2. Targeted `proc_pidinfo(PROC_PIDTBSDINFO)` and `proc_pidpath` checks verified current-user ownership, the real executable matching the installed `limactl` location, and start seconds `1794515885` / microseconds `915186`. Private absolute paths are omitted. Path identity is not cryptographic binary attestation.
3. Registered `kqueue` `EVFILT_PROC` / `NOTE_EXIT` for that PID, with `EV_ADD | EV_ENABLE | EV_ONESHOT`. Registration succeeded.
4. Rechecked the identity and PID records; they were unchanged.
5. An immediate nonblocking poll returned **zero events**. No exit was induced, so this is not an event-delivery test.
6. Closed the kqueue descriptor, removing the registration. **No observer remains armed from this check.** The VM remained running.

## Earlier incomplete attempt

At approximately 21:01:54 UTC, the first attempt checked identity but stopped before registration because Python did not expose the `KQ_EV_RECEIPT` constant. Its descriptor was closed. The subsequent attempt used standard supported registration flags and succeeded. The correction was not a permission-denial workaround; both attempts are retained here rather than reporting only the successful one.

## Claim and remaining gates

Supported claim: this narrowly authorized route could identify the named process and register the native exit observer at the recorded time, with unchanged identity on recheck.

Not established: delivery of an exit event; complete VM/descendant coverage; stop or force-stop effectiveness; cleanup; a persistently armed observer; independent deadline enforcement; resistance to host suspension/failure; safe lifecycle side effects; qualification readiness for the ten-case transport batch.

No signal, lifecycle stop, VM restart, workload, container test or study test occurred. This documentation update performs none of those actions. Further tests or merge require checking with the owner first. The exact PID and start identity are historical observations and must never be reused as a current target without fresh authorized binding.
