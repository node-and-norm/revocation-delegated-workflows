# Independent local reproduction, 3 November 2026

## Result

The fixed 12-case matrix reproduced successfully in a fresh virtual environment. Both the archived 12 cases and the newly executed 12 cases passed the unchanged frozen independent checker. All deterministic evidence fields compared against the original case records matched. All six native framework checkpoint identities were found in the corresponding new checkpoint databases, matched between paused and resumed workers, and used distinct process IDs. The 14 module/failure-preservation tests also passed.

This is a separate execution of the same frozen instrument on the same host/runtime, not an independently implemented replication or a new general research finding.

## Provenance and environment

- Input: withdrawal_interface_study_v01_20261103.zip, 379,513 bytes.
- Input SHA256: adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c.
- Used frozen_candidate_v02, the measured-run candidate documented by REPRODUCTION.md, not the earlier v01 candidate embedded in the archive.
- Python: CPython 3.12.14, Clang 22.1.3; Linux 6.18.57 x86_64, glibc 2.41; SQLite 3.53.1.
- Created a new isolated .venv; installed using --no-index, --no-cache-dir, --require-hashes and the existing historical local wheelhouse. No dependency download was performed. The fresh pip freeze exactly matches frozen requirements.lock, and pip check passes.
- The wheelhouse was outside the input archive. It is a necessary locally available reproduction resource, not a claim that the ZIP itself contains every dependency.
- All 231 SHA256SUMS entries passed before and after execution. All 12 frozen-file hashes matched. The original ZIP hash remained unchanged. Source files and expected outcomes were not modified.

## Case outcomes (same in direct and framework arms)

| Schedule | Caller at observation end | Execute | Effects | Fence/effect ordering |
| --- | --- | --- | ---: | --- |
| S0 | IDLE | effect | 1 | no withdrawal |
| S1 | INSTALLED_CONFIRMED | revoked denial | 0 | fence before execute |
| S2 | INSTALLED_CONFIRMED | effect | 1 | effect before fence |
| S3 | INSTALLED_CONFIRMED | revoked denial | 0 | fence before execute; completion delivered later |
| S4 | UNCONFIRMED_AT_OBSERVATION_END | revoked denial | 0 | fence installed; caller completion withheld |
| S5 | UNCONFIRMED_AT_OBSERVATION_END | effect | 1 | withdrawal delivery withheld; no fence |

No old-authority effect followed a recorded local fence in these twelve fixed cases.

## Procedure and evidence

run_reproduction.py records every reproduction subprocess argument vector, working directory, start time, exit code, stdout and stderr in evidence/commands.json and named output files. It checks archive integrity, creates the environment, installs offline pinned dependencies, checks archived records, executes the documented direct and framework --measured commands into new directories, checks each arm, and verifies source/archive integrity again. The --measured flag was used because it is part of the documented reproduction command; it changes the collection label, not execution logic. These artifacts are a reproduction batch, not an expanded original campaign.

audit_reproduction.py compares deterministic record fields with archived records and checks native checkpoint identities through read-only SQLite access. It also executes test_modules and test_failure_capture. Its results and exact unit-test command are in evidence/comparison.json and evidence/module_test_command.json. New records, authoritative sink databases, worker output and checkpoint databases are in reproduced/.

The semantic comparison includes caller inputs/transitions, relay trace, committed barriers, full sink snapshot, execute response, cleanup, and direct adapter evidence. Framework process IDs, checkpoint IDs, model-message IDs and related generated metadata are expected to vary; full records were not claimed byte-identical. Within each new framework case the native checkpoint linkage and separate worker files were verified directly.

## Limits and documentation observations

- No model/provider API, real email or external network action was invoked. Workflow tracing is disabled. Offline pip flags prevented package-index access. No packet capture or OS network-isolation attestation was performed.
- The same trusted local host/controller, fixed synthetic authority and deterministic schedules remain. No hostile process boundary, remote sink, arbitrary crash/restart, lost gateway-to-relay response, caller/relay restart, late completion, concurrency distribution or deployment latency was tested.
- Success is deterministic conformance for this fixed fixture. It does not establish a security vulnerability, deployment readiness, autonomous-model behavior, distributed revocation closure, failure probability or a new revocation principle.
- The independent checker is the archive's frozen checker, not a newly authored replacement. The separate comparison/checkpoint script provides additional read-only verification but is not an independent reimplementation of the authority mechanism.
- The 40 archived semantic-mutation results were not rerun. The frozen mutation script writes a historical qualification artifact, so it was deliberately excluded to preserve the extracted archive unchanged. Existing mutation evidence remains archived; it must not be counted as fresh reproduction evidence.
- README.md and PROTOCOL.md contain earlier qualification/pending-state text alongside later completion updates. This report uses REPRODUCTION.md, the v02 freeze, and measured01 manifest for the executed procedure, without changing those historical texts.
- The source/command records and this report were made by the reproduction operator. They are not independently signed attestations.

No mismatch or unavailable dependency was encountered. No source correction or change to expected outcomes was needed.
