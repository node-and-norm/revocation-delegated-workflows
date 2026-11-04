# Partial qualification status

4 November 2026 UTC. Research owner: Mark Julius Banasihan.

## Outcome

Native Temporal qualification has not run. The current source is an unqualified development candidate. No measured study, live model call, external effect or production action occurred.

The historical archive SHA256 matched adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c. Its frozen gateway was copied unchanged: source/gateway.py SHA256 98445edd61af21bc5c740053f8a93f6c179e4c5efa7b28dd7363e779b8f059a9.

Four schema-only unittest methods passed; see logs/q1_schema.txt. These do not complete the proposed transport qualification. Node syntax checking completed without an error; that is not Workflow execution.

The first Q2 control attempt failed at socket.socket(AF_UNIX, SOCK_STREAM) with PermissionError EPERM, before bind or dispatch. See logs/q2.txt and q2_controls/live/sink.sqlite. The gateway had already created synthetic fixture state and issued delegation/admission. Its child endpoint then closed when bridge startup failed. The subsequent cleanup request raised BrokenPipeError. The log preserves both errors. This attempt supplies no bridge-control pass.

Two requests to execute an escalated correction/rerun were rejected before execution. The second followed forwarding of the later direct-user authorization evidence. Both rejection messages cited retained read-only/no-experiments instructions. These are tool-reported outcomes from the conversation, not subprocess outputs; no shell log was produced for them. Neither denied command applied its proposed source corrections or created its requested retry directory. Execution stopped after the once-only evidence-backed retry.

## Remaining corrections and checks

- Move socket creation inside protected failure capture; retain the child endpoint through controlled teardown even when startup fails.
- Preserve cleanup errors without masking the first failure.
- Bound the Q2 receiver against EOF and oversized responses; its current receive loop can repeat on an empty read.
- Add transport mocks for partial-send exception, poll timeout, receive failure, oversized/truncated frames, one dispatch/no retry, and socket-creation failure.
- Re-review the corrected candidate before further qualification.
- Complete native cancellation/lifecycle checks, exact outcome mapping, raw history export and independent checks only after the execution blocker is resolved.

Earlier review corrections are described in BRIDGE_LIFECYCLE_SPEC_v01.md and review/BRIDGE_REVIEW_v01.md. The pre-correction source snapshots remain distinct. No claim of byte-complete preservation of every intermediate edit is made.

A read-only process inspection after the failed attempt found no remaining qualification supervisor, Node runner or Temporal server process. The runtime-install/startup smoke records are maintained separately by the runtime qualification worker; they do not establish a Workflow/Activity test.

## Provenance note

This repository derivative omits the private authorization exchange and message identifiers. The execution boundary and failed-attempt account are unchanged. Original byte identity is retained in the source manifest; the omitted exchange does not establish empirical success.

## Packaging

Retain synthetic failed-run SQLite and logs as evidence. Exclude __pycache__, bytecode, sockets, process files and the node_modules symlink. The linked dependency directory belongs to the separately pinned runtime package. Preserve source unchanged during packaging and label this package partial/blocked, not qualified.
