<h1 id="revocation-in-delegated-workflows">
<a href="https://nodeandnorm.org/">
<picture>
  <source media="(max-width: 600px)" srcset="https://raw.githubusercontent.com/node-and-norm/.github/13bac647d54ab62f3e6a8b500b2e5edc03e5227e/assets/research/v2/revocation-delegated-workflows/banner-mobile.svg">
  <img src="https://raw.githubusercontent.com/node-and-norm/.github/13bac647d54ab62f3e6a8b500b2e5edc03e5227e/assets/research/v2/revocation-delegated-workflows/banner.svg" alt="Revocation in delegated workflows" width="1000">
</picture>
</a>
</h1>

A person asks a system to stop work it has already handed off. How can anyone tell whether the action still went ahead? This Node & Norm study followed each request to the place where the action would take effect. In two scenarios the requester received no confirmation. In one, the system blocked the action. In the other, the action went ahead.

**The bounded local study closed on November 24, 2026.** The closeout examined the saved records from 12 scripted workflow cases. [Study overview](https://nodeandnorm.org/research/#current-study) · [Read the essay, *You asked it to stop. Did it?*](https://nodeandnorm.org/research/revocation/essay/)

## What the requester could know

The study ran six fixed schedules twice, once directly and once through a LangGraph workflow that could pause and resume. A local SQLite database recorded both when permission ended and whether the action went through. Three schedules show why a reviewer needs both records.

| Schedule | What the requester knew | What the authority and destination records showed |
| --- | --- | --- |
| S4 · Reply withheld | No confirmation arrived. | Permission ended before the worker tried to act. The system denied the attempt. |
| S5 · Request withheld | No confirmation arrived. | The request had yet to reach the authority when observation ended. The worker completed one action with permission. |
| S2 · Action first | The requester received confirmation that permission had ended. | The action had already taken effect. Withdrawal left it in place. |

Across the 12 cases, six actions took effect and six attempts were denied. Every recorded action occurred while permission was still active. Both paths used the same local authority, one handoff and at most one outstanding withdrawal. The schedules were chosen in advance. Production failure rates, behavior across independent services, live AI agents and benefits for human reviewers remain open questions. [All six schedules](docs/decisions/2026-11-03-request-to-fence-interface-study.md) · [Machine-readable outcomes](docs/review/WITHDRAWAL_INTERFACE_SUMMARY_v0.1.json)

## Inspect or reproduce the evidence

| To examine | Start here |
| --- | --- |
| The original research question, records and limits | [Guided study notebook](RESEARCH_STUDY.ipynb) and [research-book contents](notebooks/00_start_here.ipynb) |
| What the requester saw and what the destination did in S4 and S5 | [Exact saved records](notebooks/learning_02a_exact_s4_s5_records.ipynb) and [evidence workbench](notebooks/01_revocation_evidence_workbench.ipynb) |
| The study design, execution and review | [Methods notebook](notebooks/03_methods_and_reproduction.ipynb), [recorded inputs and outputs](notebooks/04_exact_scripted_inputs_outputs.ipynb) and [post-run review](docs/review/WITHDRAWAL_INTERFACE_POSTRUN_REVIEW_v0.1.md) |
| Historical stages and detailed operational notes | [Dated study synthesis](docs/reports/2026-11-06-current-study-synthesis.md) and [complete November 18 reading guide](https://github.com/node-and-norm/revocation-delegated-workflows/blob/032575d799cf2efb819508813f35bc9ffa2556a0/README.md) |

### Reproduce the request-to-fence study

Extract the [complete study archive](archives/withdrawal_interface_study_v01_20261103.zip). Start with `measured01/SUMMARY.json`. Each case under `measured01/direct/` or `measured01/framework/` contains a `record.json` and a `sink.sqlite` destination database. The [reproduction instructions](docs/review/WITHDRAWAL_INTERFACE_REPRODUCTION_v0.1.md) distinguish inspecting saved files from running the frozen instrument in a compatible environment. The recorded reproduction used the same host and instrument with an external collection of dependencies. [Reproduction report](docs/review/WITHDRAWAL_INTERFACE_LOCAL_REPRODUCTION_v0.1.md)

### Preserved v0.2 qualification

An earlier phase used 18 configured cases to test the measurement rules. Review found three errors in the checker. The corrections and original counterexamples are preserved. A separate integration pilot used eight fixed cases. Each stage has its own protocol and results. [Qualification record](qualification/v0.2/README.md) · [Integration pilot](integration/v0.3/README.md)

## AI assistance and research responsibility

Mark Julius Banasihan is responsible for the research decisions. AI tools assisted with design, implementation, checking, separately assigned reviews and writing. The workbook identifies recorded human decisions and the checks actually performed. Independent human validation and independent replication remain open. [Study disclosure notebook](notebooks/02_traceability_and_disclosure.ipynb) · [Node & Norm research integrity](https://nodeandnorm.org/about/research-integrity/#ai-use)

## Release and citation

The November 18 experimental GitHub pre-release preserves the study materials as they stood on that date. Its release notes describe the repository’s private status at the time. The repository is now public. The November 24 closeout reviewed existing evidence and is documented in the [public study account](https://nodeandnorm.org/research/#current-study). Original study materials carry no open-source license grant. Bundled third-party materials retain their own notices.

To cite the archived code and evidence, use **Cite this repository** or the [citation file](CITATION.cff).

> Banasihan, Mark Julius (2026). *Revocation in delegated workflows*. Experimental research archive, November 18, 2026. [GitHub pre-release](https://github.com/node-and-norm/revocation-delegated-workflows/releases/tag/research-archive-2026-11-18) · [Exact source revision](https://github.com/node-and-norm/revocation-delegated-workflows/tree/2ec55580a864d55c261de5770f2c58e58e828332)
