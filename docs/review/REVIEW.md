# Independent AI review — delegated revocation qualification v0.2

## Decision

**No remaining blocker for the declared finite qualification on final source.** This is a model-free, local, deterministic instrument qualification, not a new vulnerability finding, estimate of reliability, or demonstration of AGI control. Source v0.1 was not edited; its three core source hashes still match the earlier reviewed version, and its preserved 18 tests pass. No installation, network/API request, security-setting change or publication was performed by the reviewer.

## Invariants verified

- Gateway maps distinct parent/child/control pipe endpoints to its own principal identifiers. It rejects a payload claim inconsistent with that mapping. Payload identities do not create new transport principals.
- Gateway bootstraps an explicit parent delegation right. The parent worker requests issuance; gateway creates a child-owned grant inheriting the root and epoch with restricted scope and no further delegation right. Parent then sends its token to the separately running child; child prepares and executes through its own channel. This is actual **one-edge protocol delegation**, rather than v0.1 replacement-worker handoff.
- Worker source contains no SQLite or enforcement implementation. Gateway owns the database and all effect writes. Both arms use the same owner/scope/ticket checks. Only final root authority freshness differs: the diagnostic arm reuses admission, while commit-fenced checks root epoch/active state in the same `BEGIN IMMEDIATE` transaction as effect insertion. Revocation and grant issuance serialize in the same SQLite domain.
- Gateway transaction commits before its execution response. Explicit application acknowledgement is a later request. Thus C2's late acknowledgement does not imply a late effect, nor a delayed gateway response. Pipe/snapshot barriers establish order without timing sleeps.
- Separate observer process imports no gate code, connects read-only and obtains a transactionally consistent snapshot of actual committed sink rows. It does not accept worker success claims as effect evidence. Same-transaction event and sink rows establish local commit order, not an independently anchored timestamp.

## Corrections found and verified

Initial independent replay matched all 18 fixture expectations and 17 original tests. Three coherent counterexamples nevertheless passed the original endpoint-label/effect-count qualification:

1. Fenced post-revocation attempt was denied for `scope_expansion`, despite the specified valid scope, rather than `revoked`.
2. A child admission appeared after child-grant issuance was denied and the child grant was absent.
3. An execution attempt appeared after preparation was denied and the admission ticket was absent.

All had no observed effect, so NO_VIOLATION was insufficient to establish that the intended causal treatment ran. They are preserved in `counterexamples01.json`; these were oracle/qualification weaknesses, **not observed gateway bypasses**.

The correction keeps the endpoint separate from treatment qualification. `assess` rejects missing delegation/admission dependencies. `qualify` additionally requires the specified execution outcomes and exact denial causes, including `revoked` for every fenced C1/C3 attempt. The wrong-cause trace still has the observational no-effect endpoint but fails qualification; missing dependency traces are INVALID. A valid post-fence effect remains VIOLATION even if the arm label says commit-fenced. All three preserved cases are now nonqualified.

Final test-only change moved the unittest main guard below added tests so direct invocation includes all 19. Reviewer inspected that diff and reran discovery, direct invocation and the complete fixture harness on final source.

## Verified results (not research sample counts)

- **18/18 final arm × schedule fixtures** matched expectations in `replay03`. These are nine schedules and two arms, not independent samples. Admission-only produced seeded post-fence effects in C1 and C3; commit-fenced did not. Both arms passed no-revocation and legitimate pre-fence/late-ack controls. Scope, identity, foreign-grant, scope-expanding delegation and post-revocation grant-issuance controls rejected as specified.
- **19/19 final unit tests**, through both discovery and direct invocation. This is the same test set run twice, not 38 distinct checks.
- **349/349 reviewer semantic/database checks**: 3 preserved regressions; 170 single-event deletions with renumbering; 18 extra events; 54 grant-field mutations; 14 missing-child-evidence cases; 18 boolean sequence substitutions; 72 direct read-only SQLite checks of row counts, post-fence effects, payload/ancestry and child-grant registry. Mutation checks test exact declared fixture evidence, not arbitrary protocol traces or complete fuzz coverage.
- **36/36 independent real-IPC assertions** across both arms: child attempts controller actions/claims; parent/child foreign grant use; unknown grant; invalid delegation recipient; no child redelegation right; valid issuance/admission; changed payload; foreign ticket; post-revocation grant denial; contrasting stale effect; shutdown and actual sink row counts. These use the actual gateway process, not a mocked predicate. Gateway source is byte-identical between these checks and final replay.
- **18/18 preserved v0.1 tests** pass. These remain legacy engineering regression checks, not new v0.2 observations.

Counts overlap; do not sum them into a population or accuracy estimate. C3 is three attempts of one logical effect, not three trials. Mocked timeout tests and actual missing-database observer tests cover specified failure paths, not all OS faults. Missing or invalid evidence cannot qualify; an INVALID classification must not be interpreted as proof of no effect.

## Commands and evidence

From `qualification_revocation_v02`, final commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v > ../qualification_revocation_review_v02/unit_final.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python test_qualification.py > ../qualification_revocation_review_v02/direct_final.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python harness.py --output ../qualification_revocation_review_v02/replay03 > ../qualification_revocation_review_v02/replay_final.log 2>&1
(cd legacy_v01 && PYTHONDONTWRITEBYTECODE=1 python -m unittest -v)
```

From workspace root:

```sh
PYTHONDONTWRITEBYTECODE=1 python qualification_revocation_review_v02/ipc_checks.py
PYTHONDONTWRITEBYTECODE=1 python qualification_revocation_review_v02/semantic_checks_final.py > qualification_revocation_review_v02/semantic_checks_final.json
```

`ipc_checks.py` requires a fresh `ipc01` directory; preserve the recorded results instead of overwriting. Reviewer scripts assume the original sibling source/reviewer directory layout. Initial and corrected replays, raw SQLite databases, exact source snapshots, counterexamples and logs are preserved. Final source hashes are in `final_source_hashes.json` and `replay03/runtime.json`.

## Limits and stop

Process separation is **not hostile-process containment**: all processes share an OS user and the filesystem is accessible. Complete mediation is an assumed code-path boundary, not an adversarial security result. Tokens are deterministic fixture identifiers, not cryptographic capabilities. Parent-child delivery is worker/harness evidence, not independently witnessed by the database observer. Same-host event/row agreement does not authenticate a coherently altered database. There is one root, one descendant, one scope/key and no regrant, partition, remote effect, crash-durability campaign, adaptive behavior or concurrency exhaustion.

The admission-only flaw was deliberately seeded. The review does not establish novelty or a deployed weakness. This is separate AI-assisted review, not independent human validation. Finite review and correction verification are complete; no further experiments were started.
