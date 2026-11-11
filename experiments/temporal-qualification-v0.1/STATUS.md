# Ownership and observation-handoff qualification candidate

11 November 2026. Unintegrated engineering candidate, not a Temporal qualification pass.

## Implemented mechanism

`SingleUseExchange` runs exactly one worker through an injected process context. The worker persists dispatch intent before attempting the fixed child execute request, sends once, then waits for one gateway reply. The supervisor bounds its process join with the remaining monotonic exchange budget. A late/missing reply, worker error, start failure, partial-send failure or deadline expiry stays `uncertain`; it is not reported as cancellation, revocation or no effect. Only a validated on-time reply from an exited worker is `reply_observed`, which is a transport result, not a treatment verdict. Callers must separately require complete records and cleanup; reply_observed with record_complete=False cannot qualify a case.

The session is consumed even on failure and rejects reuse/concurrent use. The original gateway endpoint remains caller-owned through teardown; the caller must not use that stream concurrently or recreate a fresh session to retry it. Missing/broken evidence never establishes absence of effect. Late result files stay separate from a timely supervisor reply. Forced termination only establishes attempted cleanup; if the process remains alive or its state cannot be established, cleanup is incomplete.

Reply and supervisor files are attempt-specific and bounded to 64 KiB; the directory must be newly created. Worker intent is flushed/fsynced before send. Atomic rename avoids accepting a partial result file; crash durability of directory rename has not been qualified. Local filesystem ownership is trusted, not hostile-process authentication.

## Tests and exact limits

37 mock/pure test methods pass in the current suite (22 exchange regressions plus 15 ownership/cut checks). They cover a timely response, no second dispatch, concurrent/repeated rejection, construction/start failures, partial send, deadline exhaustion, late/missing/misbound/oversized replies, journal failure, primary plus cleanup failure, unsettled termination and shrinking join budget.

The process/clock/channel are doubles. Some join doubles synchronously execute the worker against a fake channel; some emulate a blocked exchange without executing it. Tests use actual temporary file serialization but do not prove real blocked pipes, process scheduling, descriptor transfer, termination or Temporal behavior. No native process, socket, server, model call or measured collection ran.

**Not a hard real-time bound:** process construction/start, OS terminate, filesystem operations and kernel scheduling are not themselves externally preempted by this Python supervisor. Join is deadline-bounded; cleanup has a separate budget. The strict claim is controlled state transitions and no retry in this candidate, not guaranteed wall-clock return on every OS failure. A platform-level outer watchdog remains a qualification/design requirement.

## Integration readiness

Suitable for review and preservation as an explicitly experimental private-repository candidate. Not ready to replace the existing bridge or qualify native cases. Prepared for a private draft PR preserving experimental code; no native collector integration or merge is included.

Before integration:
1. Resolve ownership handoff and enforce one outstanding exchange per actual channel, not merely per Python object. Do not reuse a potentially partial/tainted pipe.
2. Replace the unbounded Q2 cleanup stop RPC with a reviewed separate bounded lifecycle mechanism. This execute-only session cannot send controller operations.
3. Integrate coordinated observation cuts and exact per-treatment sink/native verdicts. Supervisor process termination must not substitute for these.
4. Define authoritative protocol/schema and acceptance criteria for deadlines, native record completeness and late evidence.
5. After explicit permission and an appropriate environment, qualify actual spawn/descriptor/blocked-pipe behaviors and outer watchdog, then native Temporal lifecycle. Measured collection still requires a separate decision.

Earlier candidates and historical evidence remain untouched. Previous EPERM restrictions were not retried or bypassed.

## Ownership / observation-handoff extension

The next increment adds a same-interpreter endpoint-object claim across session instances, and `ObservationCut` to validate declared capture acknowledgments and file digests before a precleanup handoff. 37 mock/pure methods currently pass, including cleanup-during-hashing regressions. It deliberately records atomic_snapshot_proven=False and qualification_verdict=None even for a complete handoff. See README.md for aliasing, synchronization and exporter-truth limits.

## Repository preservation blocker

A branch-creation request was rejected before mutation by the execution reviewer, citing retained read-only research instructions. No branch, commit, pull request or merge was created. No alternate route or retry was attempted. Explicit permission for the concrete private branch/draft-PR update is needed before another request. Local implementation and evidence remain available.

### Later authorization

The owner explicitly approved creating a private experimental branch and draft PR while leaving main unchanged and not running Temporal. A check confirmed the earlier denied request had not created the branch. The once-only evidence-backed retry succeeded. This package is being preserved on that branch; no merge or native execution is authorized by this approval.
