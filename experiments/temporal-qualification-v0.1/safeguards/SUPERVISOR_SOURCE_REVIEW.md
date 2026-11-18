# Local supervisor source review: not ready

12 November 2026. A local-only Python supervisor candidate was drafted and reviewed by a separately assigned AI-assisted reviewer. No candidate source is included in this documentation-only PR update. It was not executed, compiled or tested; no VM operation, lifecycle stop, setting change or merge occurred.

## Review and corrections

The initial source review identified incomplete configuration requirements, possible late-event classification, lost output on exceptional/early exits, cleanup failures suppressing the report and insufficient release-attempt uncertainty. The correction pass added mandatory configuration records, capped incremental reads, a post-retrieval deadline check, explicit release uncertainty, separately retained output and guarded finalization.

A second source review identified helper-entry bypass, executable hash verification after invocation, premature drained-output labeling, config aliases and an overly broad evidence-completeness name. Further edits closed normal/helper entry points while the development guard is false, moved digest checks before external commands, rejected identical resolved file identities, tracked per-stream EOF and renamed the narrow field to output completeness.

Final independent AI-assisted source inspection confirmed those targeted corrections were present. This is source-review evidence only, not evidence they work at runtime. The source guard is a development precaution, not a security boundary. The candidate stays local and closed; no operational configuration is supplied.

## Four unresolved blockers

1. **Effective configuration binding:** prove reviewed paths and values are the actual active VM/network configuration, not merely distinct files with matching hashes.
2. **Identity and replacement races:** bind binaries, configuration and target process identities across review, invocation and observation. Hash-before-use narrows a problem but does not eliminate replacement races or concurrent lifecycle changes.
3. **Durable evidence:** a separate bounded persistence design must preserve identity, release, observation, CLI outcome and cleanup records on failures. Final printed output is not durable attempt evidence; writing must not block the deadline loop.
4. **Lifecycle-helper descendants:** direct owned-child cleanup does not establish ownership or termination of subprocesses/services created by the lifecycle CLI, nor undo network reconciliation. Wider effects and recovery scope remain unresolved.

No full guardian-readiness, containment, VM-exit or hard-deadline claim follows. Mark must be consulted before further tests or merge.

## Smallest next design step without a test

Prepare an **operation-and-evidence contract** for the exact graceful-stop path, using source review and already preserved configuration evidence only:

- Identify the exact supported command/version, effective configuration sources and target instance; record what evidence binds each role and what remains unknown.
- Map command subprocesses and shared-service effects from source. Assign an owner, permitted cleanup action and observable end condition to each; explicitly mark unowned descendants as a no-go.
- Specify a minimal attempt-record schema: preflight identities/config digests, release attempted/delivery uncertainty, event retrieval time versus cutoff, separate CLI outcome, per-stream completeness, cleanup outcomes and persistence errors.
- Define the evidence writer's bounded queue/storage contract and failure policy. Queue saturation or save failure produces an incomplete evidence result; it cannot extend the lifecycle window or become a pass.
- Give the reviewer an acceptance checklist. Only after this closes enough design gaps should an implementation or narrowly scoped test be proposed for separate approval.

This is a written specification task, not authorization to inspect denied process state, invoke APIs, stop/start the VM, implement a new runtime or run tests. If available source cannot establish descendant ownership or active configuration semantics, report the precise missing evidence rather than guessing.
