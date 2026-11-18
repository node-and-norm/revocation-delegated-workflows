# Dedicated revocation VM setup status

Setup completed 12 November 2026 at approximately 20:38:31 UTC. Follow-up verification was reported at 20:38:49–20:39 UTC by the separately assigned environment reviewer. This is a sanitized derivative summary, not a raw transcript or independent reproduction.

## Source record

The local `SETUP_VERIFICATION_20261112.json` contains timestamps, checks and configuration hashes. Original and final configuration copies were retained locally. The private absolute host path is deliberately omitted here; this chapter does not claim to have independently rehashed or reproduced that local record.

## Reported actions and read-only checks

- Separately authorized Colima startup returned exit code 0. The official VM base image was downloaded and standard built-in emulation setup occurred. This does not qualify emulation compatibility or a workload.
- `colima status --profile revocation-qualification-v01`: running; VZ; aarch64; Docker; virtiofs.
- `docker --context colima-revocation-qualification-v01 info --format 'Server={{.ServerVersion}} CPUs={{.NCPU}} Memory={{.MemTotal}} Cgroup={{.CgroupVersion}}'`: server 28.4.0, CPUs 2, reported memory 2054496256 bytes, cgroup version 2.
- Docker container and image listings for the dedicated context were empty. No workload-image pull, container test or study execution was performed.
- `docker context show`: `default`, unchanged.
- Lima listing for `colima-node-norm-research`: `Stopped`.
- Guest `lsblk` through the dedicated profile: root 5368709120 bytes (5 GiB), data 2147483648 bytes (2 GiB). These are virtual capacities.
- Guest `findmnt -t virtiofs`: exactly one host folder mount, the dedicated staging folder, read-write. The private host path is redacted here.
- Guest `ss -lntu`: standard guest SSH 22, DNS 53 and DHCP 68 listeners; no workload listeners reported. This snapshot is not comprehensive egress or exposure testing.
- Final host free-space sample: 18.9555 GiB, above a 10 GiB planning reserve. The reserve is not enforced by that observation.
- Saved configuration: 2 CPUs, 2048 MiB memory, 5 GiB root disk, 2 GiB data disk. The configured memory and Docker-reported memory are separately recorded, not treated as identical measurements.

## Current scope and limits

Profile `revocation-qualification-v01` remains running at the recorded check. Shared networking was approved for this setup; network-disabled test-container isolation is not established. The original research profile remains stopped. No default-context switch, test workload or independent stop/cleanup qualification is established by these checks.

Docker reporting cgroup v2 is useful environment evidence, not proof of delegated access, reliable all-descendant kill, independently enforced deadlines or a guardian outside the fault domain. Those controls remain unqualified. No native Temporal case or measured study ran.

This documentation update made no VM/configuration changes and did not run code tests. It records a separately authorized setup rather than silently rewriting the earlier proposed profile. No further startup, teardown or security-sensitive change is authorized by this record alone.
