# Proposed later stages

These are design notes only. Stage one is the glossary and registry in this package.

## Stage two stable study identifiers

Propose opaque stable identifiers for claims, sources, artifacts, protocol versions, cases, runs, attempts, observation cuts and decisions. Keep a permanent record identity separate from its immutable version identity and content hash. Do not replace native Workflow/run/Activity IDs or gateway request/operation keys: store those as scoped identifiers, with explicit mappings and provenance. Fixture correlation must not be described as authentication.

A claim version should carry its exact proposition, scope, known status, evidence links, observer, evidence-view permissions, observation cut, uncertainty, AI role, reviewer role and supersession history. A run must point to exact protocol/source/runtime versions. A denial should record its action, target, pre-execution versus uncertain outcome and source, without transforming authorization into empirical evidence.

Proposed minimal relations: supported_by, contradicted_by, derived_from, scoped_to, observed_at, executed_under, reviewed_by, supersedes and corrects. Require typed endpoints and a recorded basis for every relation. A relation to an AI review records a review, not independent human validation. Unknown links remain unknown rather than inferred from a shared filename or timestamp.

Before adoption, map existing labels without rewriting old artifacts; check duplicate and ambiguous identities, source resolution, correction preservation and queries that distinguish planned from executed cases. No stage-two ID migration is performed here.

## Stage three evaluate whether a graph helps

Use a small retained snapshot only after stage-two records are sufficiently stable. Compare graph queries against the same information available in the flat registry and ordinary linked files. Predeclare questions, expected answer evidence, access rules and correction cases. Candidate questions:

1. Which claims support fence installation but not caller confirmation at the same cut?
2. Which conclusions depend on a historical protocol status superseded by a later result report?
3. Which apparent passes lack expected sink grading or use incompatible observation cuts?
4. Which proposed cells have no executed run, and which sources support only setup readiness?
5. Which claims would require review if a source or protocol version is corrected?

Evaluate correct evidence retrieval, unsupported inferences, unresolved/conflict handling, permission-boundary leakage, update burden and whether the graph adds a useful capability beyond the flat baseline. Seed examples are prospective test cases, not results. Do not measure human review speed or accuracy without a separate designed evaluation. If the flat registry answers the practical questions equally well, retain it and do not expand merely to claim an ontology contribution.

No graph software, ingestion, experiment, benchmark, result or publication claim is included in this package.
