# Cooperative check: source-preservation record

The exact harness used for the approved 13 November 2026 run is preserved as `../cooperative_check.py`, SHA-256 `053f7284b0c86c8178983d289d863ea02b7ff0550f4b194a0224be8ccef70d72`. No bytes were edited after that run. Its opening preparation-time word “Unexecuted” is historical; see [the recorded result](cooperative-run-001/summary.json).

Dependencies remain `../bounded_exchange.py` and `../bridge.py`, with hashes in the result and package manifest. The script uses sibling imports, Python standard library, two anonymous one-way pipes and real spawn children. It does not call the socket listener. No secrets, credentials, personal local paths or client material were found in source inspection. This is a preserved research fixture, not an installed service or CI job.

To inspect: read the source and saved records without running them. Any future reproduction needs separate approval, a fresh output directory and the disclosed owned-child TERM/KILL contingency. The command-line flag is an accidental-execution guard, not an authorization mechanism. No execution, test, import, compilation or VM operation occurred during source preservation.

The pass is a single cooperative observation, not a reliability estimate or qualification of blocked/fault cases. Python helper teardown, OS blocking, persistence and complete containment remain unestablished. Source preservation improves auditability; it does not independently attest that the program ran.

## Historical proposed next step (subsequently approved and run)

This paragraph preserves the source-preservation proposal, not current status. The later [finite EOF result](finite-eof-run-001/summary.json) and [exact harness](../finite_eof_check.py) now document its separate approval and execution.

Original proposal: review one finite EOF case: the peer records receipt of the fixed request, closes its reply writer without sending a reply and exits normally. The expected candidate outcome is uncertain with a preserved receive error, never reply_observed; both direct children must be reaped and evidence/cleanup classified separately. Correct closure of every writer duplicate is a prerequisite, otherwise an apparent EOF test becomes an unintended wait. Keep the peer cooperative and finite, do not test an infinite hang or resistant child. Prepare and source-review its distinct harness and exact approval request first. No additional check is run or authorized by this document.
