# Independent post-run review

Audit time: 2026-11-03 19:16 UTC. Scope: the separately authorized measured campaign under frozen_candidate_v02, not additional workflow execution.

## Verdict

All 12 measured cases pass the independently executed frozen checker against their raw SQLite sink databases. The direct and native paths each include exactly S0–S5. All records identify themselves as measured. No missing case, unexpected effect, wrong request identity, unsupported completion claim, missing native outcome or frozen-source hash mismatch was found.

All six native cases use distinct initial and resumed process IDs, preserve their exact checkpoint and interrupt/action identities, and propagate the actual sink result to the final supervisor message. Independently opened checkpoint databases contain the recorded initial and final checkpoint IDs. Standalone worker_pause.json and worker_resume.json exactly match their embedded record artifacts.

## Outcomes

Both paths reproduce the registered outcomes:

- S0: one authorized effect, caller IDLE.
- S1: revoked denial, no effect, caller installation confirmed before resume.
- S2: one pre-fence effect remains recorded after installation confirmation.
- S3: revoked denial while caller remains pending, followed by installation confirmation when the response is delivered.
- S4: revoked denial and no effect, but caller remains unconfirmed at observation end because completion is withheld.
- S5: one authorized effect with no delivered withdrawal/fence in the observation window; caller remains unconfirmed.

The total of six effects is expected: three in each path. Six resumed attempts are denied as revoked. Live controls succeed, so safe denials are not credited to an absent execution path. A confirmed fence does not imply rollback of S2's historical effect.

## Freeze and source audit

Every file listed in frozen_candidate_v02/FREEZE.json matches its recorded SHA-256, including gateway, workflow, relay, caller, runner, protocol, checker, tests and dependency files. The runner diff from the qualified candidate only introduces collection_kind metadata and parsing of the --measured flag; the default remains qualification and schedule execution logic is unchanged.

The frozen checker itself was used for this independent post-run replay. No checker or frozen candidate edits were made during this audit. Artifact integrity establishes consistency with the saved freeze. It is not cryptographic runtime attestation; RUN_MANIFEST.json now provides the exact reported invocations, zero exit statuses, interpreter/package versions and matching source/freeze hashes. It is explicitly labeled as a post-collection record from executed commands, not independent attestation. Referenced stdout/stderr artifacts are present.

## Evidence

- independent_postrun_checker.json: four independent verdicts for each measured case, including read-only authoritative sink comparison.
- independent_postrun_audit.json: frozen hash checks, record hashes, outcome summaries, checkpoint-database confirmation and standalone worker-artifact equality.
- ../INDEPENDENT_REVIEW.md: development findings, fixes and mutation qualification, including preserved rejected historical traces.

## Interpretation limits

These are deterministic local conformance cases with deliberately selected schedules, a fixed single authority and one local atomic sink. They qualify the caller's evidence handling and actual native checkpoint-resume integration. They do not estimate race probability, deployment latency, reliability rates or production readiness. They do not show arbitrary crash recovery, genuine network response loss, multi-root targeting, global quiescence, rollback or a novel revocation mechanism. Caller isolation is structurally enforced by its interface inside a trusted fixture, not an adversarial process sandbox.

No outcome discrepancy remains. The campaign is suitable for the bounded case-level result above, with the qualification history and limitations retained.
