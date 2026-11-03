# AI-assisted research team charter

Version 0.2 · 3 November 2026 · Draft for Mark Julius Banasihan's review

## Research purpose

An institution may withdraw an AI agent's authority while delegated work remains queued, retries, or resumes from a saved checkpoint.  Node & Norm studies whether the withdrawal reaches the protected action and what evidence supports that judgment.  The research team supports this work through source analysis, experimental design, critical review, and reproducible records.

Mark Julius Banasihan leads the research program and retains responsibility for its questions, interpretation, and release decisions.  Frontier-AI assurance and AGI readiness provide its longer-term direction.  The completed pilot establishes a bounded integration result within a trusted local test environment.

## How the team works

The team operates through defined assignments.  Alfred coordinates AI-assisted contributions and presents the evidence, disagreements, and decisions to Mark Julius Banasihan.  Each assignment identifies its sources, permitted actions, deliverable, and stopping point.  Reviewed artifacts carry the work forward across later sessions.

The current arrangement consists of research roles and documentation.  A persistent execution environment, schedule, credentials, budget, and external appointments would each require a separate decision.  GitHub preserves the team's documents and version history.  Execution infrastructure would need its own access controls, resource limits, stop behavior, and test plan.

## Responsibilities and review

### Human research lead: Mark Julius Banasihan

Mark Julius Banasihan selects the research question, judges its significance, and decides which claims the evidence can support.  He approves changes in scope and consequential next steps.  Decisions should identify the evidence considered, the remaining uncertainty, and the action authorized.

### AI research coordinator: Alfred

Alfred divides a bounded question into assignments, supplies the relevant sources and constraints, and integrates the findings.  He checks that the proposed method addresses the research question and that each conclusion can be traced to evidence.  He brings unresolved disagreements to the research lead with their practical consequences and available choices.

### Literature and evidence researcher

The evidence researcher reads primary papers, documentation, repositories, and applicable standards.  The output identifies the closest prior work, documented capabilities, competing explanations, and the precise contribution under consideration.  Source quotations and interpretations remain distinguishable.  Inaccessible material is recorded with the access limitation.

### Methods researcher

The methods researcher defines the cases, comparison methods, controls, measurements, and rejection criteria.  The protocol explains what the test can establish and which assumptions it relies on.  It also identifies the smallest useful exercise, expected effort, required evidence, and conditions for stopping or revising the design.

### Critical reviewer

The critical reviewer checks consequential claims against the original evidence.  The review looks for answer leakage, weak comparisons, incomplete provenance, ambiguous measurements, and alternative explanations.  Each concern receives a documented response: corrected, accepted as a limitation, unresolved, or rejected with supporting evidence.

AI reviewers may share models, sources, or assumptions.  Their agreement therefore requires examination before it carries evidential weight.  Record separate AI-assisted review accurately.  Independent human validation requires an identifiable human review process and evidence of the work performed.  A fresh reviewer should receive primary evidence and assessment criteria, with prior exposure disclosed.

## Immediate scope

The execution-grounded revocation question remains active.  The completed qualification and v0.3 integration records remain preserved.  A proposed retrospective evidence exercise would complement that work by examining what a later reviewer can establish from selected portions of the record.  Evidence veracity and oversight scaling remain deferred as separate research programs.

Two saved framework cases report the same revoked denial while their cumulative effect histories differ.  The trusted controller inserted an earlier effect in one case.  These deliberately selected synthetic records illustrate an information distinction under the pilot's assumptions.  Claims about production failures, reviewer performance, or a novel mechanism would require further evidence.

The next design deliverables are a packet specification, a scoring rubric, a comparison against competent source-linked review, and a leakage assessment.  The rubric should distinguish the resumed attempt, cumulative effects, initiator provenance, event ordering, and unresolved questions.  Packet evaluation, model calls, participant involvement, and new workflow runs remain subject to the applicable execution approval.

## Developing specialist capacity

Specialist responsibilities should grow with the evidence workload and the need for separation of duties.  One person or AI-assisted role may initially cover several responsibilities.  The assignment record should make those combinations visible, especially when the same contributor prepares data and reviews its interpretation.

- **Data custodian:** Preserves original records, documents source versions and rights, identifies duplicated material, and records every extraction or redaction.  The custodian controls answer keys and case mappings during any approved blinded evaluation.
- **Test-environment specialist:** Maintains reproducible dependencies and configuration, documents isolation assumptions, and separates qualification runs from measured runs.  The specialist records setup failures and verifies that later changes preserve the intended test conditions.
- **Quality reviewer:** Checks instrument behavior, negative controls, scoring, leakage, and reproduction instructions.  The review connects each reported measure to the claim it is meant to support.
- **Research-integrity reviewer:** Checks attribution, AI-use disclosure, reuse rights, corrections, conflicting evidence, and human-review status.  Before an authorized release, the reviewer examines whether the artifact contains private information or claims beyond the approved scope.

These responsibilities describe planned capacity.  Assignment records will identify the roles actually staffed and the work completed.  Additional roles should address a specific workload, skill requirement, or conflict of responsibilities.

## Planned use of TypeSafe AI's Jev

Jev is a candidate instrument for structured semantic judgments in evidence triage.  A future approved comparison could ask it whether a source supports a claim, whether two records conflict, which evidence is missing, or whether a case should be referred for review.  The design should define the permitted labels and the action associated with each label before evaluation.

Node & Norm's TAE × Jev work already includes live model use.  That earlier study provides relevant experience with structured judgments and response validation.  Its results remain tied to its own inputs, reference labels, model version, and validation rules.  Calibration and usefulness in the revocation study still require a task-specific comparison.

Deterministic code should continue to check source identifiers, hashes, record bindings, timestamps, ordering rules, permissions, and required fields.  Jev's proposed role concerns semantic interpretation after those checks.  Mark Julius Banasihan retains decision authority, and the workflow should preserve an explicit unresolved or refer-for-review path.

The planned comparison should use the same evidence and review budget for Jev, a competent deterministic or checklist baseline, and an appropriate structured-output model baseline.  Pin the model and SDK versions, retain raw responses and rejected outputs, and record prompts, label order, latency, cost, and abstentions.  Evaluate supported, unsupported, contradictory, ambiguous, and instruction-bearing evidence, including sensitivity to label order and irrelevant material.

Model probabilities, derived confidence statistics, evidence sufficiency, and authority need separate fields and interpretations.  Assess calibration against an independently specified task reference, and report errors alongside abstention coverage.  Constrained output structure provides a useful interface; factual support must still be checked against the source.  Vendor examples and advertised accuracy, speed, or cost require evaluation under their stated conditions before reuse as research claims.

The immediate Jev deliverable is a comparison plan and a decision about whether the instrument adds useful evidence.  Model/API calls, credentials, spending, benchmark implementation, and experimental execution require their applicable approval.  Current official references are the [model documentation](https://docs.typesafe.ai/models), [confidence documentation](https://docs.typesafe.ai/confidence), [citation-check example](https://docs.typesafe.ai/cookbooks/citation_check), and [known model limitations](https://docs.typesafe.ai/model-jaggedness).  Review the current versions when preparing an execution protocol.

## Long-term roles and decision record

Record future roles and operating rules as proposals with a named decision owner and a clear activation condition.  The record should capture the options considered, source evidence, rationale, open questions, and events that warrant another review.  It should also identify the information still needed to make the decision.  The aim is a faithful account of material considerations; completeness should be checked against the available assignment record.

The following planning entries establish the initial review queue:

| Planning entry | Reason to consider it | Options and questions to retain | Revisit trigger |
| --- | --- | --- | --- |
| Data custodian role | Multiple sources and derivative packets create provenance and answer-leakage risks | Shared responsibility or separate custodian; rights, storage, versioning and case-key access | An approved evaluation needs blinded packets or several studies reuse records |
| Test-environment role | Reproduction depends on stable configuration and explicit isolation assumptions | Local reproducible setup or dedicated environment; cost, access, retention and recovery | An approved study adds dependencies, parallel execution or a new effect boundary |
| Quality role | Instrument defects can survive a plausible-looking result | Separate checker, replication review or specialist review; competence and shared assumptions | Methods or test volume exceed the current team's review capacity |
| Integrity role | Cross-study reuse can obscure attribution, permissions and corrections | Assignment-level review or program-level reviewer; disclosure, rights and release criteria | Several studies share evidence or a public release is proposed |
| Cross-study synthesis role | Connections can generate useful questions across the collection | Periodic source review or a dedicated analyst; duplication, legal scope and evidence status | The catalog has a verified inventory and a concrete comparison question |
| Human specialist review | Some claims require domain expertise and external challenge | Suitable expertise, scope, independence, availability and compensation | A consequential claim or intended release warrants human review |
| Shared methods repository | Several studies may need common templates and standards | Continue study-local documents or create a shared repository; ownership and access | Repeated maintenance demonstrates a concrete benefit from shared records |
| Automated research runtime | Repeated approved tasks may benefit from consistent execution | Manual assignments or bounded automation; permissions, costs, logs and stopping behavior | A recurring workload has stable inputs, measurable checks and explicit authorization |

All entries are proposed.  Mark Julius Banasihan owns the decisions; Alfred maintains the supporting research record.  No appointments, spending commitments, new repositories, automated schedules, or expanded permissions arise from these entries.

Future AI operating rules should address source verification, treatment of hostile or instruction-bearing content, confidential information, access boundaries, model and tool versions, review independence, cost limits, escalation, and stopping behavior.  Record each rule's purpose, scope, owner, evidence and review date.  Permission changes require the applicable user approval, and sensitive actions retain their existing confirmation requirements.

## Coordinating several studies

Each active study needs a bounded question, an owner, an evidence location, and an approved next step.  Study records should retain their own protocol versions, results, limitations, and decisions.  Shared methods can be linked across studies while preserving the origin and scope of each finding.

A common Node & Norm methods repository may become useful once several active studies reuse the same charter, templates, or review practices.  The current private repository remains the home for this study's team documents.  Creating another repository or migrating a study requires a separate decision about ownership, access, and maintenance.

A cross-study review should produce a short connection record.  That record names the sources, describes the proposed mechanism, states the strongest alternative explanation, and identifies evidence that could reject the connection.  Promising links enter a research queue for evaluation.  Their status remains provisional until the supporting work is complete.

## Using the Governance Explorer

The [Governance Explorer](https://nodeandnorm.org/governance-map) offers a starting point for finding connections.  The website data reviewed on 3 November 2026 contains eight research programs, 80 unique governance topics, and 640 editorial relevance assessments: 137 direct, 307 context, and 196 not established.  It also contains 130 selected risk records and 56 incident cases.

The November 2 mapping and challenge were AI-assisted editorial work.  Independent human and legal validation, a new full-text review, and population coverage remain unestablished.  The counts describe the selected collection.  Causation, compliance, and control effectiveness require evidence beyond a mapped association.

The website records research-crosswalk.json, risk-selection.json, incidents.json, and map-clusters.json under /assets/governance/ are candidate inputs for a versioned inventory.  Source-level provenance and rights checks should precede reuse.  The separately shared project conversation was unavailable during preparation of this charter.

A future catalog should distinguish a study, paper, incident report, risk statement, control, legal provision, and evaluation artifact.  Each record needs a stable identifier, exact source locator, date or version, unit of analysis, access conditions, reuse rights, evidential status, and the claim it supports.  Allegations, verified events, hypotheses, and executed results require separate labels.

For example, a risk record concerning delayed intervention could suggest a revocation test.  The team would first inspect the underlying source, identify the relevant actor and action boundary, and determine whether the recorded mechanism matches the test environment.  An incident could then inform a case, subject to verification and rights checks.  Repeated descriptions from a common source would remain linked as dependent evidence.

Governance maps guide source discovery.  Material legal claims require the applicable primary provision, jurisdiction, regulated actor, use case, legal status, and effective dates.  Compliance and certification judgments require their own assessment.  A public page's reuse conditions also need verification before its material enters a shared artifact.

## Permissions, records, and disclosure

Each assignment operates within its actual approval.  Publication, spending, participant recruitment, third-party contact, private-data transmission, credential creation, expanded access, and experiments require their applicable authorization.  Repositories remain private pending an explicit release decision.  Research artifacts should exclude client information, unrelated personal records, and internal assistant instructions.

Preserve source snapshots, failed checks, corrections, and decision rationale.  Report proposed, implemented, executed, AI-reviewed, and human-reviewed work separately.  Hashes establish byte consistency; truth, authenticity, and scientific validity require additional checks.

The [assignment workflow](WORKFLOW.md) provides the operating sequence.  Review the charter whenever study scope, responsibilities, or permissions change.  Version 0.2 applies the research lead's E5 writing preference through clear agency, explicit reasoning, precise attribution, and direct statements of scope.
