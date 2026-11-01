# Workflow selection and contribution gate

Date: 2026-11-01  
Status: **Recommended HOLD on freezing a novel-study protocol.  One adapted tutorial candidate is source-qualified for further assessment; its runtime and contribution are not qualified.**

## Decision

The source review narrowed the LangGraph direction to the email branch of LangChain's official personal-assistant subagents tutorial [1].  It has a concrete supervisor-to-subagent-to-protected-tool path, rather than merely names attached to scripted parent and child functions.  This is a candidate adapted tutorial, not a deployed application or an evaluated autonomous system.

Do not freeze a new experimental protocol or claim novelty yet.  The reviewed prior work materially overlaps with checkpoint recovery, current authority and effect scoring.  The next decision is whether an independently implemented conformance integration would have sufficient value, or whether a specific unanswered implementation question can be justified.  Neither outcome follows merely from adding a framework or using a stronger control contract.

The choice between a bounded conformance milestone and continued search for a distinct research question has been put to the researcher and remains pending.  This note records an AI-assisted recommendation, not a human decision to adopt either route.

No framework or model was installed, no new experiment was run, and no new experimental result was produced in this design assessment.  Q1 remains the only active direction.  The completed v0.2 qualification and all historical records retain their original scope.

## Source-qualified workflow candidate

The inspected tutorial's email branch has this path:

**supervisor create_agent → manage_email tool → email create_agent → human-in-the-loop middleware → send_email stub**

Use the actual agent, middleware and checkpoint execution path if this candidate proceeds.  Scripted model messages could exercise that path without a paid model, but would not establish autonomous-agent behavior.  The tutorial's email and calendar functions are stubs.  Any initial adaptation would use only harmless synthetic local effects, with no actual mail or calendar access.

The tutorial uses an in-memory checkpointer.  A restart experiment would require an explicitly versioned adaptation to persistent checkpoint storage.  Authority state must remain outside that checkpoint store: restoring execution state must never restore a revoked grant.  Pausing for human approval is not equivalent to authority revocation, and the upstream tutorial does not promise the latter.

### Source pins and unresolved runtime selection

These revisions identify inspected source, not a tested environment or resolved dependency lock.

| Component | Source basis | Qualification boundary |
| --- | --- | --- |
| Tutorial | LangChain docs commit `64063c67975bdc79bcb251027cf9016975865671`; `src/oss/langchain/multi-agent/subagents-personal-assistant.mdx`; blob `c0f70b516b9e5d0e822f44f168f08bbcd6ce561d` [1] | Source-qualified adaptation candidate only. |
| Agent and middleware | LangChain 1.4.7, commit `fbb8a35da7023ac0382c3b22f047337861bd3486`; human-in-the-loop middleware [2] | Source inspected; not installed or executed. |
| Deterministic test model | Same LangChain revision, unit-test model helpers [3] | Mutable model-index state requires deliberate reconstruction across restart; the helper is not automatically a restart-safe substitute. |
| Graph and persistent checkpointer | Candidate LangGraph 1.2.19 and checkpoint-sqlite 3.1.3; repository revision `5bd231cbfd913e05ebc662f519eb9a655bc766df` [4] | Candidate versions only; no resolved lock or runtime verification. |
| Core dependency | Candidate langchain-core 1.7.3 | Unresolved as part of the complete dependency set. |

The inspected LangChain package declares LangGraph `>=1.2.12,<1.3` and core `>=1.6.13,<2` [5].  Satisfying those version ranges does not prove that the complete candidate environment installs, runs or preserves the needed semantics.  Exact dependency resolution, licenses and execution checks remain prerequisites.

## Contribution gate and related work

**Permission to Retry** already studies native LangGraph/Temporal recovery, current authority and effect-based scoring.  Its contract permits a first delivery admitted before local revocation to complete afterward, unlike our proposed stronger effect fence.  That mismatch prevents an outperformance claim.  The reviewed paper supplies no public execution repository; an independently implemented comparison would not be an exact artifact replication.  See the paper for its full methods and limitations [6].

Additional overlap was identified at abstract-review level only: ACRFence (replay and authority resurrection), ResidualAuth (history retention), and VERA (delegated edges) [7–9].  These abstracts are screening evidence, not a completed assessment of their methods, implementations or results.  A fuller comparison is required before asserting an unanswered question.

Adding parent/child labels, a framework, a different provider, or a stricter chosen contract is not sufficient novelty.  A justified conformance study could still be useful if it supplies a reproducible implementation and exposes an integration boundary under explicit assumptions.  Such a decision must identify its intended user and what the evidence would change.

## Implementation gates before any protocol freeze

1. **Establish upstream behavior first.**  Qualify the selected tutorial's pause/resume behavior with deterministic model messages before adding an authority adapter.  Preserve the unmodified source reference and document each adaptation.
2. **Make deterministic recovery meaningful.**  Derive the scripted model's next response from persisted workflow state, or an equivalently documented restoration rule.  An in-memory cursor that resets on restart can change the task rather than reproduce recovery.
3. **Bind authority externally.**  Use trusted grant and operation identifiers, explicit delegation lineage, and immutable payload/action binding.  Model-editable state must not define identity or grant authority.  Restoring a checkpoint must not roll back the authority store.
4. **Match the effect contract.**  Define revocation commitment and protected-effect commitment in a shared authoritative ordering.  A gateway admission check followed by an independently committing receiver remains a different contract.  Do not treat an authorized intent as an external effect.
5. **Preserve useful work and classify retries.**  Include matched nonrevoked completion and legitimate pre-fence effects with later responses.  Distinguish a new mutation from a returned preexisting result, and specify duplicate handling rather than silently changing it between arms.
6. **Bound restart claims.**  The current v0.2 gateway initializes tables with CREATE statements; it is not a qualified restart/recovery service.  A worker restart while that gateway remains alive is a narrower possible test.  It would not establish gateway crash durability, recovery across all processes, or resilience to network partitions.
7. **Version the instrument.**  The current oracle contains expectations tied to cases C0–C8.  Any adapted checker or new schedules need a separate version and qualification; do not overwrite the executed v0.2 instrument or relabel its counts as framework results.
8. **Freeze only an informative comparison.**  Record the hypothesis, natural integration pattern, diagnostic controls, effect observer, liveness criteria, incomplete-evidence accounting and stopping rules.  Stop or redirect if results would merely reproduce deliberately seeded races or if the effect boundary cannot be observed.

The present commit-fenced gateway checks revoked authority before duplicate lookup.  Preserve that behavior in the historical instrument.  A future choice to return a prior result after revocation would require an explicit read-only/idempotency contract and its own checks; it is not an incidental refactor.

These are entry requirements for a future decision, not a frozen protocol or a claim that the gates have passed.

## Preservation and disclosure

AI assistance supported source inspection, comparison of claims, interpretation of the contribution boundary and preparation of this note.  Source-qualified means the candidate was examined in code and documentation; it does not imply runtime verification, independent human validation, novelty or deployment readiness.

This note supersedes the October 31 candidate note only as the latest design status.  That earlier note remains unchanged as a dated record.  The existing source, qualification archives, results, reviews, specification, workbook and notebook remain byte-preserved.  Historical SOURCE_PROVENANCE.json and STAGING_VERIFICATION.json keep their original scopes.  Only this note, the README status link and the root file-integrity manifest are part of the update.  No website edit, public release, model call or live email/calendar action is included.

## Sources inspected for this decision

1. [Pinned personal-assistant subagents tutorial](https://github.com/langchain-ai/docs/blob/64063c67975bdc79bcb251027cf9016975865671/src/oss/langchain/multi-agent/subagents-personal-assistant.mdx).
2. [Pinned LangChain human-in-the-loop middleware](https://github.com/langchain-ai/langchain/blob/fbb8a35da7023ac0382c3b22f047337861bd3486/libs/langchain_v1/langchain/agents/middleware/human_in_the_loop.py).
3. [Pinned LangChain unit-test model helpers](https://github.com/langchain-ai/langchain/blob/fbb8a35da7023ac0382c3b22f047337861bd3486/libs/langchain_v1/tests/unit_tests/agents/model.py).
4. [Pinned LangGraph repository revision](https://github.com/langchain-ai/langgraph/tree/5bd231cbfd913e05ebc662f519eb9a655bc766df).
5. [Pinned LangChain package requirements](https://github.com/langchain-ai/langchain/blob/fbb8a35da7023ac0382c3b22f047337861bd3486/libs/langchain_v1/pyproject.toml).
6. [Permission to Retry, version 1](https://arxiv.org/html/2610.31916v1).
7. [ACRFence, version 1 abstract](https://arxiv.org/abs/2603.20625v1).
8. [ResidualAuth, version 2 abstract](https://arxiv.org/abs/2609.08062v2).
9. [VERA, version 1 abstract](https://arxiv.org/abs/2608.30091v1).
