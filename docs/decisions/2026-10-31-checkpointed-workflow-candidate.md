# Design decision: checkpointed workflow candidate

Date: 2026-10-31  
Status: **Candidate for the next design phase; no framework-based experiment selected or executed.**

## Decision and purpose

Prioritize LangGraph as the first framework to assess for one externally grounded delegated workflow.  The candidate question is:

**After a parent-authority revocation is durably committed, can resumed or retried delegated work create a new protected effect using earlier permission?**

The next design task is to select a documented workflow, pin its implementation and dependencies, and state what testing it would establish beyond the completed local qualification and existing research.  A framework choice alone does not establish a research contribution.  The existing v0.2 instrument and results remain frozen.  Q1 remains the sole active direction; evidence veracity and oversight scaling remain deferred.

## Source-backed rationale

LangGraph documents that replay from a prior checkpoint re-executes downstream nodes, including API requests and interrupts [1].  Its interrupt reference states that resumption restarts the node [2].  Those execution semantics create a concrete integration question: task progress may be restored after the authority governing its actions has changed.  They do not constitute a promise of authority revocation or a demonstrated framework defect.

The proposed initial integration would use deterministic nodes and harmless synthetic protected records.  It would exercise an actual framework without yet evaluating autonomous model behavior.  A model-driven condition requires a distinct informative hypothesis, an explicit scope and authorization; adding a model is not itself a scientific advance.

## Candidate comparison and observations

The exact protocol remains to be chosen.  A useful bounded comparison would distinguish:

1. Approval retained in checkpointed task state.
2. Current permission checked before submitting an action, with an observable interval before the protected commit.
3. Effective authority checked within the same transaction or equivalent serialization protocol as the protected effect.

Deliberately stale or admission-only adapters are diagnostic controls, not discoveries.  A contribution claim requires a justified replication or evidence about a specific unanswered boundary in a documented integration.

Start with ordinary continuation, restart and checkpoint replay.  Add retries or forks only when they exercise a distinct mechanism.  Preserve these measurement requirements:

- Define the fence as durable revocation commitment, ordered with protected effects.  A stop request, response timestamp or UI acknowledgment is not the fence.
- Count new protected effects after that boundary separately from attempted calls, denial reasons and returned results.
- Keep authority state outside the workflow checkpoint.  Restoring task progress must not restore revoked authority.
- Include matched authorized-work controls.  Blanket denial is not useful control.
- Distinguish a pre-fence effect reported later from a new post-fence effect.  Returning an existing idempotent result does not create a new mutation; duplicate suppression does not authorize a new one.
- Use explicit synchronization and durable event evidence rather than infer causal order from wall-clock timestamps alone.
- Preserve incomplete and failed runs.  Check that the intended delegation, preparation and denial causes occurred, as in the current instrument.

## Correction to the supplied architecture example

The reviewed Google AI Mode text suggested a Redis WATCH/MULTI/EXEC check that records an action as committed, followed by an HTTP request to an external service.  That sequence does **not** atomically fence the external effect.  Permission can be withdrawn after EXEC but before the external service commits the change.  Redis documents that WATCH applies through EXEC, which unwatches the keys [3].

The example is suitable as a proposed negative control, not as a safe implementation to adopt.  An intent record must not be mislabeled as evidence of an external commit.  Moving the current SQLite check into an API gateway, or substituting another database, does not by itself close the gap.  A separate receiver requires authority validation coordinated with its own effect boundary, or a clearly weaker stated contract.  A network sandbox cannot undo an external operation already accepted.

## Alternatives deferred

- **CrewAI:** a possible later replication.  Current documentation describes checkpoint, resume and fork support [4].  It is not excluded for lacking persistence.
- **OpenHands Software Agent SDK:** a possible later coding-agent setting [5].  Its wider tool and process boundaries require additional mediation and observation work.
- **NVIDIA OpenShell:** a possible later confinement test, if the question requires resisting direct gateway bypass [6].  Isolation and final-effect authority enforcement are separate properties.
- **Additional sandbox platforms:** not required for this candidate assessment.  The original Daytona repository is archived and should not be described as the current actively maintained open-source core [7].

These are bounded source-inspection judgments, not measured framework rankings.  No framework, sandbox or model was installed or executed in this assessment.  Future adoption requires version-specific license, dependency and runtime checks.

## Continue, redirect or stop

Proceed to a protocol only if a documented workflow, observable effect boundary and justified question can be identified.  Freeze the comparison, failure accounting and stopping conditions before executing it.

Redirect toward a clearly labeled conformance replication, or stop, if the exercise merely reproduces races seeded into our own adapters.  Redesign if authority checks and effects span uncoordinated stores, if observation cannot distinguish commit from admission, or if apparent safety comes from preventing all useful work.  Novelty, framework vulnerabilities, hostile-worker containment and AGI readiness remain unestablished.

## Record and AI-use disclosure

AI assistance was used to examine the user-supplied Google AI Mode text, verify official documentation, compare candidate frameworks and draft this decision record.  The supplied text was treated as a set of claims to check, not as authoritative implementation guidance.  No new experiment or independent human validation is claimed.

This dated note supplements the original repository record.  The earlier specification, qualification archives, source, results, review records, workbook and notebook are unchanged.  SOURCE_PROVENANCE.json and STAGING_VERIFICATION.json retain their original staging scope; this note does not relabel those checks as verification of a new experiment.  The root SHA256SUMS is refreshed solely to cover the current documented tree.  No website change, public release, paid API use or deployment is part of this update.

## Sources inspected on 2026-10-31

The official pages below support this design assessment.  Their mutable current URLs are not a frozen implementation; pin exact revisions before a protocol is selected.

1. LangGraph, [Use time-travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel).
2. LangGraph, [interrupt reference](https://reference.langchain.com/python/langgraph/types/interrupt).
3. Redis, [Transactions](https://redis.io/docs/latest/develop/using-commands/transactions/).
4. CrewAI, [Checkpointing](https://docs.crewai.com/en/concepts/checkpointing).
5. OpenHands, [Software Agent SDK](https://github.com/OpenHands/software-agent-sdk).
6. NVIDIA OpenShell, [Sandbox policies](https://docs.nvidia.com/openshell/latest/sandboxes/policies).
7. Daytona, [archived repository and status notice](https://github.com/daytonaio/daytona).
