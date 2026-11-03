# Research assignment workflow

Version 0.1 · 3 November 2026 · Draft for review

This workflow implements the [team charter](CHARTER.md) as a repeatable document process. It does not start an automated team or authorize a new experiment.

## 1. Define a bounded assignment

Record the question, intended user, decision it informs, existing study and artifact versions, allowed sources/actions, deliverable, owner, and stopping condition. Identify any missing authority before dependent work. Separate facts already established from assumptions and goals.

For the present study, keep the completed v0.3 integration evidence unchanged. The proposed reconstruction extension first needs a packet specification and scoring rubric. Its design approval is not evidence that an evaluation has run.

## 2. Establish the evidence boundary

Inventory exact inputs and versions. State what the original decision-maker could see, what a later reviewer receives, and what the evaluator retains as reference truth. These are different information sets.

For each source record, capture its locator, date, author/provider, status, relevant claim, limitations and reuse conditions. Cite exact sections for consequential claims. Record inaccessible material as inaccessible, not as evidence of absence. Detect duplicated or derivative sources before counting corroboration.

## 3. Prepare parallel research contributions

The evidence researcher compares the closest work and competing explanations. The methods researcher specifies the smallest useful test, strong baseline, controls, measures and rejection criteria. The critical reviewer checks both against source material and searches for decisive counterexamples.

Use explicit handoffs: question, inputs, version, permitted action, expected output and known uncertainty. Keep unresolved disagreement visible. Do not allow a reviewer to qualify its own unsupported assertion through repeated paraphrase.

## 4. Apply a contribution and feasibility gate

Ask:

- What does the proposed work add beyond existing semantics, instruments and baselines?
- Could ordinary retrieval and a competent checklist answer the question?
- Which observation would reject the claim or make the exercise uninformative?
- Is evidence sufficient to distinguish the competing explanations?
- Are data rights, privacy, effort and execution permissions adequate?

Choose continue, revise, replicate explicitly, or stop. A well-supported negative result or decision not to build is legitimate progress. Do not search indefinitely for a first-ever claim.

## 5. Freeze before an authorized evaluation

Save the protocol, packet construction/redaction rules, comparison methods, scoring rubric and source versions before exposing answers to evaluators. Separate raw records from derived packets. Keep case mapping and reference truth away from any reviewer intended to be blind; disclose prior exposure and shared access.

Correct abstention is preferable to unsupported certainty. Score whether a conclusion is justified by available evidence separately from whether it happens to match hidden truth. Case-level engineering checks are not independent statistical samples. A model proof, source inspection, runtime test and human review establish different things.

Execution, participant involvement or model/API use require the applicable approval. Until then, mark work design-only. Do not turn a documentation commit into an implicit experiment or CI run.

## 6. Preserve results and challenge them

If execution is later authorized, retain the original inputs, code/configuration, outputs, failures, corrections and environment information. Never overwrite historical results to make them fit later checks. Reproduction and separate review should identify exactly what was checked and what was not.

For reconstruction work, distinguish reported disposition, established attempt, cumulative effect history, initiator provenance, ordering, record coverage and unresolved obligations. A denied retry may coexist with an earlier effect. A framework message marked successful may describe successful message handling rather than a successful protected action.

## 7. Deliver and hand off

End with a concise decision brief: finding, supporting evidence, strongest alternative explanation, limitations, unresolved disagreement, next decision and links to canonical artifacts. Log material AI assistance and actual human review without inventing either.

Suggested assignment record fields:

- Assignment ID, study ID, owner and date.
- Question, scope, authority and stopping condition.
- Inputs and source versions; access/reuse restrictions.
- Contributors by role and actual tools/models where recorded.
- Claims, counterclaims and evidence locators.
- Checks performed, failures/corrections and unresolved issues.
- Decision, permitted next step, artifact locations and review status.

This record carries continuity across later sessions. GitHub versions documents and evidence; it does not itself schedule or execute researchers. Any future runtime needs its own reviewed permissions, resource limits, logging, stop behavior and test plan.
