# Read-only cloud runtime inspection · 12 November 2026

Purpose: assess visible process-containment prerequisites. This is a transcription of tool-returned observations, not signed host attestation. Commands below were metadata reads only. No test workloads, socket operations, signals, namespace actions, systemd commands, environment creation or settings changes were performed. File/path discovery does not verify operational semantics.

## Commands and observed output

`uname -srm` → `Linux 6.18.57 x86_64`

`cat /proc/self/cgroup` → `0::/`

`grep ' - cgroup' /proc/self/mountinfo` → no matching line.

`id` → `uid=1000(agent) gid=1000(agent) groups=1000(agent)`

`grep -E '^(Cap|NoNewPrivs|Seccomp)' /proc/self/status`:

```text
CapInh: 0000000000000000
CapPrm: 0000000000000000
CapEff: 0000000000000000
CapBnd: 0000000000000000
CapAmb: 0000000000000000
NoNewPrivs: 1
Seccomp: 2
Seccomp_filters: 1
```

`command -v systemctl systemd-run docker podman timeout nsenter unshare cgexec` found:

```text
/usr/bin/systemctl
/usr/bin/systemd-run
/usr/bin/timeout
/usr/bin/nsenter
/usr/bin/unshare
```

`ls -ld /sys/fs/cgroup` → No such file or directory. Read attempts for `cgroup.controllers`, `cgroup.subtree_control`, `cgroup.type`, `cgroup.events`, `cgroup.max.depth`, `cgroup.max.descendants` produced no content because this directory was absent. Metadata/access checks for `/sys/fs/cgroup`, `cgroup.procs`, `cgroup.kill`, and `cgroup.subtree_control` found no writable path. No writes were attempted.

`cat /proc/1/comm` → `codex`

Namespace symlink inspection showed the inspection process and PID 1 share the visible PID, cgroup and user namespace identities. This does not disclose or establish host-level control.

`grep -E ' /sys | /run | /proc ' /proc/self/mountinfo`:

```text
145 141 0:35 / /proc ro,nosuid,nodev,noexec,relatime - proc proc rw
157 141 0:40 / /run ro,nosuid,nodev,relatime - tmpfs tmpfs rw,mode=755,uid=1000,gid=1000
196 145 0:64 / /proc rw,nosuid,nodev,noexec,relatime - proc proc rw
```

Metadata checks found none of these ordinary endpoints: `/run/systemd/system`, `/run/user/1000`, `/var/run/docker.sock`, `/run/podman/podman.sock`, `/run/dbus/system_bus_socket`, `/run/systemd/private`, `/run/user/1000/bus`, `/run/user/1000/systemd/private`.

`cat /proc/cgroups` reported enabled controller rows; that establishes kernel metadata, not delegated access:

```text
#subsys_name hierarchy num_cgroups enabled
cpu 0 4 1
cpuacct 0 4 1
blkio 0 4 1
devices 0 4 1
freezer 0 4 1
net_cls 0 4 1
perf_event 0 4 1
net_prio 0 4 1
hugetlb 0 4 1
pids 0 4 1
```

## Decision limit

No usable delegated cgroup, systemd-scope or local container-control route was evidenced through the paths inspected. Provider-level facilities remain unknown. No actual termination, descendant containment, watchdog behavior or denied operation was tested. A later environment must be assessed independently.

## Mac candidate: later status update, not selected for execution

A separate coordinator-reported read-only review on 12 November 2026 found both Colima and Lima reporting `node-norm-research` as **stopped**. These related management views are not independent proof of guest process absence, lifecycle enforcement or descendant containment. The cloud inspection transcript above is not evidence about the Mac.

The saved VM profile includes persistent disks, user-mode networking, host-name resolution, proxy propagation and broad automatic forwarding. Existing workloads and restart policies remain uninspected. Startup could resume retained services/workloads and expose network paths before a qualification fixture is ready. These are prospective risks arising from the saved configuration, not observed startup behavior.

A Rosetta-related `sysctl` read was denied. It was not retried or bypassed; runtime suitability remains unresolved. This document does not claim the exact denied invocation or preserve a raw Mac transcript; the facts in this section are attributed to the separate coordinator-reported review.

No VM startup, test workload, configuration/security change or denial retry is authorized by this documentation update. Before a separate startup decision, inspect retained workload/restart behavior and concrete network exposure, and establish independent watchdog/containment support. Stopped status alone does not qualify the VM or make startup inert.
