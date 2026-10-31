# Node & Norm Q1 — v0.2 delegated revocation foundation qualification

**Instrument qualification only.** This package narrows three v0.1 gaps: genuine one-edge protocol delegation, enforcement code outside workers, and independent read-only commit observation. It is not a new research finding, a SOUNDGATE replication, a deployed-system vulnerability, statistical safety evidence or full source-design conformance.

## Final reviewed result

Initial runs each met all 18 declared fixture expectations and the original 17 tests, but separate AI-assisted review found three causal-treatment false qualifications: an unrelated denial could be counted as revocation success, admission could appear despite denied delegation, and execution could appear despite denied preparation. Original source/results and all three counterexamples are preserved. These were evidence-qualification defects, not demonstrated transaction-gate failures.

Attempt03 adds dependency validation and a distinct `qualify()` check for expected treatment and exact denial reasons. `assess()` still separately reports the post-fence endpoint; a strong-arm trace with a real post-fence effect remains VIOLATION, not silently hidden by expected treatment. Two added regression tests cover the three preserved counterexamples and this endpoint/qualification distinction. Attempt04 only moves the test runner entry point below all test classes so direct-script invocation includes every test. The final test count and reviewed source hashes are recorded in `qualification_summary.json`; separate AI-assisted review cleared the current source; its report and complete evidence are in `independent_review/`. Earlier runs must not be described as passing the later controls.

The observed diagnostic pattern is seeded admission-only post-fence effects in C1 and C3, no effects in those commit-fenced cases, and one legitimate effect in each arm's C0/C2 positive controls. Five negative schedules per arm (C4–C8) require their named denial and zero effects. Counts describe finite engineered fixtures, not independent samples, rates, confidence intervals or population evidence. C3's three retries remain one logical operation.

## v0.1 → v0.2 scope delta

| Boundary | v0.1 | v0.2 | Remaining limitation |
|---|---|---|---|
| Delegation | Controller transfers a prepared ticket between workers | Parent worker exercises a bounded delegation right at gateway; gateway issues distinct child-owned grant; parent delivers token; child exercises it | One edge only; deterministic protocol, not autonomous nested planning |
| Enforcement | Trusted worker contains check and database writes | Separate gateway contains checks and all database write code; worker.py only exchanges IPC messages | Same OS user; no sandbox/credentials boundary against a hostile worker |
| Identity | Fixture worker identity | Separate parent/child channels mapped server-side to immutable principal IDs | Fixture process wiring is trusted; tokens are deterministic identifiers, not cryptographic credentials |
| Observation | Read-only separate observer and ordered same-transaction events | Separate observer imports no gate code, reads grants, tickets, authority, events and effect rows in one snapshot | Same-host evidence can be coherently falsified by an adversary with sufficient access |
| Causal evidence | Admission, attempt, commit, ack | Worker local intent/response, gateway receipt, admission, grant issuance, commit and explicit ack | Direct parent-child delivery is worker/harness evidence, not independently observed by sink observer |

The frozen v0.1 directory and published ZIP are untouched. `legacy_v01/` copies its corrected oracle, harness and 18 regression tests. The four earlier checker blind spots were: duplicate without prior effect, unknown attempt IDs, altered preparation binding and boolean sequence numbers. v0.2 explicitly carries corresponding semantic regression tests. The v0.1 source/results/counterexamples remain authoritative in its separate package; this package does not rewrite history.

## Architecture and protocol

Read `PROTOCOL.md` for the pre-execution cap and contract. A controller starts exactly two workers, one gateway and one observer for each sequential case. All processes use Python multiprocessing `spawn`. Gateway server-side pipe mapping assigns parentP, childC and the administrative controller identities. Untrusted actor claims cannot change that mapping.

The gateway bootstraps parent grant `parent-0` for rootR/epoch7 with scope `summary:task1` and a bounded delegation right to childC. The parent itself sends a delegation request. Gateway checks ownership, scope, delegation right and current root authority before issuing immutable `child-1`, owned by childC, inheriting rootR/epoch7/scope with no delegation right. Parent sends that token over a separate pipe; child receives and uses it on its own gateway channel.

Child preparation issues `ticket-1` following admission. Both arms validate owner, scope and ticket binding at execution. Admission-only deliberately omits root freshness revalidation at final execution. Commit-fenced checks root active/epoch and inserts the effect in the **same SQLite BEGIN IMMEDIATE transaction**. Root revocation uses the same database write-transaction domain and updates root epoch to 8/inactive. No regrant occurs. Unique key `summary:task1` limits effects to one inert row, payload `inert summary`.

No worker imports SQLite or opens the sink. This is a code-path separation demonstration, **not hostile process confinement**. No new OS security settings, credentials, network services, installations or deployments were introduced.

## Prepared schedules

| Case | Schedule/control | Expected outcome |
|---|---|---|
| C0 | Delegate → child prepare → execute → ack; no revoke | Both arms: one effect, no post-fence violation |
| C1 | Delegate → child prepare → revoke commit → execute → ack | Admission-only: seeded post-fence effect; fenced: denial |
| C2 | Delegate → prepare → effect commit → revoke commit → explicit late ack | Both arms: one legitimate pre-fence effect, no violation |
| C3 | Delegate → prepare → revoke → three sequential stale executions/acks | Admission-only: one post-fence effect then duplicates; fenced: three denials |
| C4 | Child requests effect outside its granted scope | Both arms: scope_expansion denial |
| C5 | Child channel claims parent principal | Both arms: caller_mismatch denial |
| C6 | Child channel presents parent's grant | Both arms: foreign_grant denial |
| C7 | Parent requests child grant exceeding its own scope | Both arms: scope_expansion denial; no child grant |
| C8 | Revoke root before parent requests child grant | Both arms: revoked denial; no child grant |

An unknown token and a forged parent claim sent over the actual child endpoint are additional unit/API controls. A nonexistent transport channel is not simulated by an actor string. These checks are finite protocol controls, not hostile socket or credential-attack testing.

## Commit, response and acknowledgement semantics

Worker ledger intent precedes its send; gateway receipt is separately persisted. Gateway result events and any corresponding sink row or authority/grant/ticket mutation are in the same transaction. A gateway response is sent only after commit. C2 delays a later explicit application ack request; it does **not** delay the gateway response already received by the worker. Oracle checks response agreement with gateway evidence and distinguishes effect commit from ack.

Pipe responses and snapshot requests establish causal barriers without sleep-based races. All IPC waits and process joins have a ten-second failure bound. Timeout or missing observer evidence becomes `INCOMPLETE`, never a clean pass. The observer connects in SQLite read-only mode, starts a read transaction and reads actual committed state rather than trusting worker success claims. Ordered event sequence numbers share transactions with their effects; they are not an independently anchored clock.

`oracle.py` imports neither worker nor gateway. It checks strict request schedule, schemas, exact actor/grant/scope/epoch bindings, event completeness/order, outcome-to-request links, sink/event consistency, registry state and worker-evidence agreement. It then separately classifies effects after the revocation event. A seeded violating trace remains a VIOLATION even if labelled as the strong arm; the oracle does not define safety from the arm label.

## Reproduce and inspect

Only installed Python standard library modules are needed; no network or dependency install:

```sh
python -m unittest -v
(cd legacy_v01 && python -m unittest -v)
python harness.py --output runs/your_unique_run_name
```

Run output directories must not exist. Every attempt keeps exact source and runtime hashes. Inspect `results.json`, `runtime.json`, per-case JSON (final trace, worker ledgers, intermediate snapshots) and raw SQLite databases. A qualification pass requires valid dependency-chain evidence, the expected oracle label/effect count, exact execution treatment, and all expected denial reasons (including revoked for every fenced post-revocation attempt). Intentional admission-only VIOLATION controls count as successful detector checks, not successful safety checks.

## Limits and stop

No LLMs, models, remote actions, user/private data, adaptive behavior, nested delegation, multiple roots, partial revoke, grant renewal, remote sink, crash durability campaign, hostile-worker sandbox, protocol fuzzing or exhaustive concurrency exploration. The finite schedule does not estimate real-world revocation reliability. Source-design requirements beyond this local assumed mediation boundary remain unqualified. Stop after separate review, bounded corrections, final finite verification and package; later research needs its own question and design.

## Final manifest reconciliation and separate review

`SCENARIOS.json` and every final attempt04 result were reconciled on exact oracle label, effect count and attempt count. The manifest contains **18 case-arm fixtures**, nine distinct schedules, including ten negative-authority-control fixtures (five schedules in both arms). **19 new tests** and **18 legacy tests** passed; direct test invocation repeats the same 19 tests rather than adding another set.

Separate AI-assisted review cleared the final source, reproducing all 18 fixtures and 19 tests, with **349 semantic/database assertions** and **36 actual IPC assertions**. These counts overlap and are not research sample sizes. Review is not independent human validation. Its initial counterexamples, all replay source snapshots/raw evidence and final report are preserved.

Reviewer scripts originally ran in a sibling directory and remain unchanged. From this package root, the packaged semantic recheck works with:

```sh
PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 python independent_review/semantic_checks_final.py
```

`PYTHONPATH` resolves source imports after relocation. The IPC reviewer script refuses to overwrite its existing `ipc01` evidence; do not delete or overwrite those original records. Reproduction of that historical script requires a fresh copied review workspace. Standard harness reproduction already uses a caller-chosen fresh run directory.

`MANIFEST.sha256` covers packaged files except itself and excluded bytecode; it provides integrity, not correctness. The ZIP has been checked against this manifest. Version 0.1's published ZIP and files remain unchanged. No further qualification work remains after this reviewed package.
