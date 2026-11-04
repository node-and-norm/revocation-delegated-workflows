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
