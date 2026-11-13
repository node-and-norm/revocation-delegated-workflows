# Safeguard notebook documentation verification · 12 November 2026

Scope: documentation additions to experimental PR #7, baseline f1e50910d4cdd41010840520f209f1ae084138b1. No candidate Python code, recorded tests or historical evidence changed.

- Notebook JSON parsed; 13 Markdown-only cells, unique valid cell IDs, expected cell fields and no code/output/execution-count fields.
- Ten distinct scenario IDs checked. All eleven relative notebook links resolve against baseline repository paths plus the new inspection record.
- README supplies a direct notebook entry. Saved Markdown tables and text diagrams require no notebook execution.
- Separate AI-assisted reviewer found two ambiguities: peer response identity versus saved result-envelope identity, and boundary versus attempt readiness. Both were corrected before repository update.
- Existing 37 candidate tests are historical recorded results, not rerun for this documentation. No real-process, socket or Temporal test occurred.
- nbformat was unavailable. No installation was attempted. These are structural checks, not official nbformat-library validation. Actual GitHub/Jupyter rendering and human usability review remain unverified.
- Runtime inspection evidence is a transcription of read-only tool observations with explicit limits, not independent host attestation. The Mac VM candidate is attributed to a separate coordinator report and unqualified.
- Package SHA256SUMS updated for these documentation files; existing code/test/log checksum entries retained. Root historical manifest is unchanged; it did not include this experimental package before the update.

AI assistance produced the chapter, source review, structural checks and review corrections. This is not independent human validation or experimental evidence for the proposed safeguards.

## Mac-status documentation addendum

Updated notebook and inspection record from a separate coordinator-reported read-only review: Colima and Lima both report stopped, but are related rather than independent evidence; saved configuration has persistent disks and network/forwarding features; workload/restart behavior is uninspected; denied Rosetta-related sysctl read was not retried. Startup risks are prospective, not observed behavior. No Mac tools, VM startup or configuration changes were used to make this documentation update. JSON, Markdown-only cell count and changed-file checks were repeated; official nbformat/viewer limitations remain.

## Historical checkpoint and dedicated-profile design addendum

Read pinned control-evidence-corpus commit f3e8066e2f1db268255914ed0bde08bcd415002b: experiments/us-control-sandbox/ENVIRONMENT.md, RUN-INDEX.md and run_container.py. Added attributed historical evidence and the launcher's unbounded subprocess calls, not current qualification claims. Added proposed dedicated VM profile with explicit mount/network/resource/management choices and unresolved security approvals. Notebook now has 15 Markdown-only cells. No VM creation, configuration change, startup, historical test or native qualification occurred.

Separate AI-assisted review checked the two added sections against all three pinned sources and found no blocking claim. Clarified that host guardian is not independent of host failure and writable output remains untrusted data, not executable content or authoritative guardian status.

## Dedicated VM setup addendum

Added separately reported actual setup at approximately 20:39 UTC on 12 November. Preserved original proposal as history; actual name, resources and shared networking are recorded separately. Sanitized VM_SETUP_STATUS.md records exact reported checks and names the locally retained verification artifact without exposing its absolute path. Configured and runtime-reported memory are separate. No workload images, containers or tests ran; official VM provisioning is distinguished. Cgroup v2 reporting is not guardian qualification. Notebook now has 16 Markdown-only cells. This update ran documentation serialization checks only, not code tests or VM operations.

## Host guardian design addendum

Directly read Lima v2.0.3 pkg/instance/stop.go and cmd/limactl/stop.go. Added force-stop semantics and concrete fail-closed observer/guardian design; implementation deliberately withheld because process identity/observer access and full containment semantics are unverified. No process-inspection denial retried. Notebook now has 17 Markdown-only cells; documentation JSON, unique cell IDs and no executable-cell checks passed. No lifecycle or study test occurred.

Separate AI-assisted source review confirmed force-stop claims and identified wider reconciliation scope. Added explicit unresolved network side-effect review and eventual approval disclosure for disk unlock, metadata removal and reconciliation. Exact target binding does not imply the whole CLI is profile-scoped.

## Narrow observer-readiness documentation addendum

Added the separately reported, explicitly authorized 21:02:28 UTC identity/registration check and initial missing-constant attempt. Recorded observer closure, no remaining registration, no event delivery/stop proof, and source limits. Updated earlier design blocker wording chronologically instead of erasing it. Notebook now has 18 Markdown-only cells. No code or study tests were performed by this documentation update; JSON serialization/cell-count checks only.

## Harmless-child check documentation addendum

Recorded the single separately authorized check and exact reported timing/result, with cooperative-child limits and wall-time distinction. Notebook now has 19 Markdown-only cells. This documentation update performed serialization/cell checks only; it ran no child check, study test, VM action or merge.

## Local supervisor review documentation addendum

Recorded local-only source review/corrections and final AI-assisted re-review, with four unresolved blockers and a written operation-and-evidence contract as the next no-test step. No candidate code uploaded. Notebook now has 20 Markdown-only cells. This update checked documentation serialization/cell structure only; no candidate compilation, tests, VM lifecycle action or merge.

## Operation-and-evidence contract addendum

Added proposed contract v0.1 and notebook summary (21 Markdown-only cells). Separate AI-assisted review found no unsafe scope expansion, but requested an explicit persistence-versus-observation timing rule and clearer no-event terminology. Corrected: T0 precedes intent submission; asynchronous receipt wait consumes the original window; no release after either cutoff, no clock reset; actual write timestamp separate. No event observed never means process absent. Four blockers remain open. Documentation serialization only; no code test, VM action or merge.

## Lifecycle source-map addendum

Directly read Lima v2.0.3 usernet, network config, directory resolution and launchd sources plus Colima v0.9.1 stop wrapper. Separate AI-assisted source review found no blocking documentation issue; clarified that usernet startup socket inspection ending does not prove readiness. Added prominent correction: no requested forced VM shutdown does not rule out helper SIGKILL. Preserved unresolved active autostart/configuration/ownership and cleanup. Notebook has 22 Markdown-only cells. No VM operation, test, source-code upload or merge.

## Active-state / dual-observation documentation addendum

Recorded separately reported read-only empty-autostart and detached-helper identity observations. Proposed separate VM/helper/CLI outcomes; no new kill authority, no armed observer and no execution. Notebook has 23 Markdown-only cells. This increment serializes documentation only; no candidate code, tests, VM actions or merge. Separate AI-assisted review found the refinement appropriately narrow and requested two wording corrections: observer spans the command/window, and no-force shorthand explicitly excludes requested VM force/additional helper kills without denying Lima’s built-in escalation. Both corrected. Runtime facts are attributed, not independently revalidated by this document review.

## Persistence failure-model addendum

Read Apple’s archived fsync/fcntl manuals and Lima issue #5087. Added supervisor-failure versus OS/power-loss distinction, without asserting current filesystem semantics or issue applicability. Notebook now has 24 Markdown-only cells. Documentation serialization only; no code execution, tests, VM action or merge. Independent text-only review found no blocking wording issue; reviewer did not re-fetch sources or perform runtime validation.


## Specification-led walkthrough addendum · 13 November 2026

Added four static sections near the notebook entrance: requirement → scope → expected evidence → actual record → conclusion → uncertainty. S4/S5 values were read from the pinned historical summary and post-run review; independent AI-assisted review separately checked the summary rows and found no blocking content issue. Historical LangGraph/direct study, proposed native Temporal work and VM-safety preparation remain distinct. The SDD paper supplies conceptual inspiration, not validation of this adaptation. Notebook serialization shows 28 Markdown-only cells. New repository link targets were checked against the current tree; cited source files were read. No raw archive audit, cell execution, test, actual viewer rendering, VM action or merge occurred. Original historical records remain unchanged.


## Concrete next test gate · 13 November 2026

Added the prepared ten-method pure-policy test proposal and exact local source hashes. Separate AI-assisted source review found the suite suitable to ask permission to run; no candidate imports, compilation or execution occurred. The code remains local, not uploaded; the notebook explicitly warns the proposed command cannot run from this PR alone. No passing test result, RAM-first acceptance, VM action or merge is claimed. Notebook now has 29 Markdown-only cells; this addition has not been visually rendered.

