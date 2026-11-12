# Lifecycle source map and active-state gaps

12 November 2026. Read-only source review of Lima v2.0.3 and Colima v0.9.1, informed by the separately reported permitted configuration preflight. No command, stop, test or setting change was performed for this map. Installed-binary correspondence and active branches still need binding.

## Decision-changing finding

**A graceful VM-stop request is not a promise that no helper receives SIGKILL.** Lima's ordinary stop path can reconcile the shared `user-v2` network and escalate its network daemon from SIGINT to SIGKILL after its approximately five-second polling threshold. Therefore the earlier shorthand “no force” applies only to not requesting forced VM shutdown. It does not describe all downstream helper behavior.

The proposed operation is not ready for approval/execution under an unconditional no-forced-termination promise. Explain this possible helper escalation and either obtain approval for the exact resulting operation or choose a separately reviewed supported alternative. Do not suppress reconciliation, patch installed tools or add an automatic retry to evade that consequence.

## Source-bound call path

| Step | Source behavior | Limit / required evidence |
|---|---|---|
| Graceful VM stop | `StopGracefully` first calls `autostart.RequestStop`; if not requested, sends host-agent SIGINT | Active `AutoStartedIdentifier` must be inspected before claiming a particular branch |
| launchd branch | When identifier equals `io.lima-vm.autostart.<instance>`, macOS code executes `launchctl bootout gui/<uid>/<service>` | Branch is conditional; current parsed identifier was not established by the earlier inventory summary |
| Waits | Host-agent event-log wait has a 3m10s context; subsequent stopped-status wait has a 3m context | Our proposed 30s is an external observation window, not Lima's built-in overall deadline; earlier operations have their own unresolved duration |
| Global reconciliation | CLI calls `reconcile.Reconcile(ctx, "")`, loading configured networks and inspecting all instances | May start or stop shared services, not merely clean the named VM |
| user-v2 stop | Saves DHCP leases through the usernet client, sends SIGINT to recorded PID, polls PID-file state; after >5s may SIGKILL and return without independent exit wait | PID-file disappearance and command success are not native exit observations; writes/network-client work may fail or block |
| user-v2 start | If absent, locks network directory, prepares log files and launches detached `limactl usernet`; then polls until socket inspection returns something other than not-found, without an explicit deadline in that loop; another filesystem error also ends this check, so it is not verified socket readiness | Not reliably owned by CLI process-group cleanup; can create/write state and outlive initiating CLI |
| Colima wrapper | Colima `Stop` retries daemon-stop at one-second intervals up to its configured ten retries, removes host addresses, then invokes limactl | Direct limactl bypasses those wrapper steps; it cannot claim complete Colima cleanup |

Sources:
- [Lima instance stop](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/instance/stop.go)
- [Lima CLI stop](https://github.com/lima-vm/lima/blob/v2.0.3/cmd/limactl/stop.go)
- [launchd branch](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/autostart/launchd/launchd.go)
- [global reconciler](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/networks/reconcile/reconcile.go)
- [usernet start/stop](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/networks/usernet/recoincile.go) (filename spelling is upstream)
- [Colima wrapper](https://github.com/abiosoft/colima/blob/v0.9.1/environment/vm/lima/lima.go)

## Configuration resolution is not a side-effect-free default

[Lima directory resolution](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/limatype/dirnames/dirnames.go) uses `LIMA_HOME` when set, otherwise the default home directory, and resolves existing symlinks. The network file is under that resolved root's `_config/networks.yaml`.

[Network configuration loading](https://github.com/lima-vm/lima/blob/v2.0.3/pkg/networks/config.go) caches per process, may create the directory/default file if missing and fills a missing suitable user-v2 entry from defaults. Calling `LoadConfig` is therefore not inherently a read-only inspection. Require an existing expected config and bind its effective defaults/environment before lifecycle invocation. Do not allow a missing file to silently create a different network policy.

The private absolute `LIMA_HOME` path is intentionally omitted. A local approved configuration packet must retain the exact root and resolved files; omission here does not relax binding requirements.

## Already reported active preflight versus unresolved facts

The separately authorized read-only preflight reported only user-v2 (gateway 192.168.5.2/24), the dedicated instance selecting it, `colima-iris-validation` and `colima-node-norm-research` stopped, and `colima-revocation-qualification-v01` running. Default Docker context stayed unchanged. Automatic broad TCP/UDP forwarding rules were present; this is not network-isolated operation. These observations are not freshly repeated by this source map.

Inference from those observations plus the source: if the dedicated VM remains the sole running consumer, successful shutdown may cause the now-unused shared user-v2 service to stop, including possible SIGKILL escalation. Recheck inventory before any future approved action; do not treat that inference as an executed result.

Unresolved: exact active autostart branch; complete helper/service identity and ownership; independent service-exit evidence; supported recovery after an interrupted CLI; effective configuration/binary binding under races; bounded durable evidence. Observing the VM-host process does not establish all of these.

## Contract corrections and next design decision

1. Narrow “no force” to **no requested forced VM shutdown**; explicitly disclose helper escalation and worker-only cleanup separately.
2. Require active `AutoStartedIdentifier` and config-resolution evidence before selecting the lifecycle path.
3. Separate VM-process observation, CLI outcome, Colima-daemon/address cleanup and user-v2 service outcome. Unknown fields stay unknown.
4. Keep direct CLI-worker cleanup from claiming control of detached usernet or launchd-managed services.
5. Resolve whether the intended minimal operation is direct Lima graceful stop with these disclosed limits or a separately reviewed Colima wrapper operation. Neither is executed or newly approved here.

This is genuine progress in identifying effects that change the approval question, not closure of the guardian-readiness gates. All tests and merge still require checking with Mark.
