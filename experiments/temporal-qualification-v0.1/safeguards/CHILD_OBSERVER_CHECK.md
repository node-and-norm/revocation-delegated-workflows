# Single harmless-child exit-observer check

**Recorded completion: 12 November 2026, 21:14:16.009016 UTC.** Mark explicitly authorized this one supervisor-owned harmless-child check. This is a sanitized derivative of the separately assigned environment reviewer's exact tool observations; no persistent raw artifact was written by that check. It is not an independent reproduction.

## Reported sequence and result

1. Supervisor used `Popen` to start `/usr/bin/python3`; the child waited for one byte on standard input.
2. Registered native `EVFILT_PROC` / `NOTE_EXIT` observation before release; confirmed the child had not exited.
3. Sent one byte, then closed the input stream.
4. Received a matching exit event: PID 8123, filter -5, flags (`fflags`) 2147483648, after **1.480987333 seconds** from release, within the declared **3-second event wait**.
5. Child `wait(timeout=1)` returned exit code **0**; child was reaped. Kqueue descriptor closed. No fallback kill needed.

**Result: PASS for this single normal cooperative child-exit notification check.** The PID is historical and must not be reused as a live target.

Tool wall time was **7.776 seconds** and includes interpreter/process startup and other overhead. Release-to-event timing is not an end-to-end runtime bound. The declared wait timeouts do not prove hard real-time behavior under every OS condition.

## Scope

This exercised successful event delivery for one supervisor-owned normal child. It did not exercise a stuck child, forced termination, VM exit, crash/race conditions, escaped descendants, observer loss, complete process-tree containment or full guardian reliability. The dedicated VM was not stopped or otherwise acted upon. No study case or setting change occurred. No observer remains armed from this check.

The earlier named-VM registration-only result remains distinct. This child result cannot be transferred into proof that the VM exits when a lifecycle command returns. Further tests and merge require checking with Mark first. This documentation update reran no check.
