# A message arrived, but its answer did not

**Result: this one planned timeout check passed.** It ran once on 13 November
2026 after Mark approved it. No VM, real service or model was involved.

Imagine sending a message and hearing nothing back. The right conclusion is
“I do not know the result,” not “it succeeded” or “it never arrived.” Here the
receiver's separate record shows the message arrived. The supervisor reached
its observation limit, kept the result uncertain and stopped its worker as planned.

## What happened

1. The receiver recorded one exact synthetic request.
2. It waited about six seconds without sending an answer.
3. The candidate reached its five-second observation budget and kept `uncertain`.
4. The candidate sent its own worker TERM; that worker's exit -15 was observed.
5. The receiver exited normally. Both direct children were reaped and their
   handles closed. No additional harness cleanup signals were needed.

**Where this puts us:** one more component check completed, not the end of the
study. This follows the successful-reply and finite-EOF checks. Native Temporal
capture, mappings and broader qualification remain ahead. This does not prove
that all possible hangs can be stopped or that the full study is complete.

## Evidence for engineers

- [Summary](summary.json): exact program output, with source/runtime identity,
  measured timestamps and separate candidate/cleanup records.
- [Peer](peer.json): receipt and measured no-reply interval.
- [Intent](exchange/dispatch_intent.json) and [supervisor](exchange/supervisor.json).
- [Exact source](../../finite_timeout_check.py), retained byte-for-byte including
  its historical preparation-time “Unexecuted” header.

The exact command was:

```sh
PYTHONDONTWRITEBYTECODE=1 python finite_timeout_check.py --approved-single-finite-timeout-check --output finite-timeout-run-001
```

Source SHA-256: `139f215c3a934ec24a683beff2d289302181c2e4bd87ae313e3729dcd7a09559`.
The two dependency hashes are in the summary. Python 3.12.14. The peer's measured
wait was 6.00065 seconds; the exchange call took about 5.00582 seconds and the
whole harness interval about 6.13631 seconds. These are observations, not hard
end-to-end guarantees or a reliability estimate.

`cleanup.signals=[]` means no extra harness signals; the candidate's intended
TERM is separately recorded as `exchange.forced_termination=true` and worker
exit -15. Do not misread the empty list as “no termination occurred.”

The timestamps bracket confirmed receipt and waiting, but do not independently
observe entry into `recv` or the precise internal cutoff. Storage/scheduling
delays remain possible explanations of where the worker spent time. No forced
VM shutdown, resistant-child test, socket listener, crash durability, whole-tree
containment or native Temporal behavior was established. No retry or merge.
Further tests require separate approval. These program records are not an
independent runtime attestation or human validation.
