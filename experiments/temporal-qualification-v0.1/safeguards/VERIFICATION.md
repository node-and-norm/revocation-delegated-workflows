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
