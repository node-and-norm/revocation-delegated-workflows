# Temporal partial qualification: setup passed, bridge remains open

Date: 4 November 2026 UTC. Status: development qualification evidence; no measured Temporal study.

## Recorded progress

The setup worker pinned Node 24.22.1, npm 11.9.0, Temporal TypeScript SDK 1.25.0, CLI 1.10.0 and bundled Server 1.32.2. Registry integrity metadata, an exact package lock, official release digests and license information are preserved. Native imports succeeded; the headless local server returned SERVING and its shutdown was verified. These checks establish the setup gate only.

Four bridge schema test methods passed. The first live bridge control failed during Unix socket creation with EPERM before dispatch. The failure occurred outside the bridge failure-journaling block; controller cleanup subsequently raised BrokenPipe after gateway EOF. Neither a live bridge control nor native cancellation/lifecycle qualification passed. No Temporal Workflow or Activity was executed.

The builder reported two rejected escalated correction/rerun requests, including one after relevant user authorization evidence was supplied. Neither command executed. Work stopped at that boundary. This package records those reported outcomes without treating permission failure as a vendor defect or research result.

## Review and remaining work

Separate AI-assisted source review identified descriptor-lifetime problems and examined revised development snapshots. Open corrections include socket-creation failure capture, cleanup preservation, an EOF/size-safe control receiver, and no-socket transport mocks for partial-send uncertainty, response failures, bounded frames, one dispatch and no retry. Four passing schema tests do not qualify those transport properties. Historical source snapshots remain unchanged. The final candidate is unqualified.

The [reviewed design](2026-11-03-proposed-temporal-interface-design.md) remains the protocol basis. Native outcome mapping, bridge controls and lifecycle qualification remain open. Measured collection needs its own qualified implementation and decision. No production, statistical reliability, novel principle or independent human-validation claim follows.

## Preserved evidence

[Partial qualification archive](../../archives/temporal_qualification_partial_20261104.zip) includes runtime source/locks, provenance and setup logs; bridge source and snapshots; synthetic failed-control SQLite; chronological review; builder status; and a package manifest. Archive SHA-256: `98a32239d9e9715c48434e7a2560b1412742fae1ff4e45941cbce553b3f6d904`.

Installed modules, caches, binaries and downloaded runtime archives are excluded. The retained package is an evidence snapshot, not a self-contained reproduction environment. The failed-control database records initialized synthetic state; no bridge dispatch/effect is demonstrated by this attempt.

AI assisted setup, implementation, review, failure diagnosis and documentation. Existing disclosure guidance retains its recorded dates and venue-specific limits. Workbook v0.10 records this qualification stage; workbook v0.9 and earlier versions retain their historical contents.

## Methods-review addendum: 4 November 2026 UTC

A further separately assigned AI-assisted methods review examined the preserved development candidate and reviewed protocol documents. These are prospective source-level findings. Native qualification never reached an executed case, so no false passing result was observed. The candidate and historical design files remain unchanged.

### Collected records and qualified cases

`source/workflows.ts` lines 18–28 catches Activity errors and returns the recorded state. `source/native_runner.cjs` lines 43–64 accepts linked terminal Activity events, explicitly rejects a timeout, and checks observation release before writing `ok: true`. Other terminal classes require treatment-specific interpretation. `source/supervisor.py` lines 53–57 checks process exit and saves a sink snapshot before setting `ok: true`; it does not independently assert the expected effect/denial disposition. Together these paths can label collection successful while a treatment-specific native or sink result is wrong. This is a prospective false-pass route in the candidate, not a demonstrated native run.

A future revision should distinguish collection completion from qualification. An independently checked case verdict needs the exact native terminal mapping, Activity/Workflow settlement and expected sink disposition for that treatment. Preserved native history and the trusted sink must support each assertion.

### Primary observation cut

The runner writes history before observation release, then releases the Workflow and shuts down the Worker in its `finally` block (`native_runner.cjs` lines 59–66). The supervisor waits for the Node process to exit before writing its sink and `supervisor_precleanup.json` snapshot (`supervisor.py` lines 53–64). That filename means before the supervisor's later cleanup; it does not establish a coordinated observation cut preceding Worker shutdown. A future revision needs an explicit acknowledged cut spanning the native history, Worker instrumentation, bridge and sink, with cleanup evidence kept separate.

### Normative status vocabulary

The preserved reviewed protocol snapshot lists `not_applicable_no_fence` for effect/fence ordering and `not_applicable_no_event` for request/observation ordering (`PROTOCOL_REVIEWED_DRAFT_v02.md` lines 80–81). The evidence contract instead includes `not_applicable_no_effect`, `no_fence_in_complete_window`, `no_request` and `no_observation` (`STATUS_EVIDENCE_CONTRACT_v01.md` lines 30–32). The current PROTOCOL_DRAFT.md already contains the no-effect category. This finding concerns historical-snapshot versus current-contract authority and version ambiguity, rather than an omission in that current draft. Designate the authoritative current protocol/schema and make the historical version relationships explicit before a candidate freeze or checker implementation. A checker must represent confirmed absence, missing anchors and unresolved evidence distinctly.

### Evidence and next gate

The source anchors above refer to the `bridge_qualification/source` files in the [partial qualification archive](../../archives/temporal_qualification_partial_20261104.zip). The protocol and contract remain in the [reviewed design archive](../../archives/temporal_interface_design_20261103.zip). This addendum adds methodological review only. No code patch, denied execution, model call or test was attempted. It does not resolve the earlier socket-permission blocker or qualify the bridge.
