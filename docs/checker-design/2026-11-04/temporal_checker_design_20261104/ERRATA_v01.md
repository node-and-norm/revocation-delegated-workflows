# Correction to original independent checker design

4 November 2026. Original `INDEPENDENT_CHECKER_DESIGN.md` preserved unchanged. This erratum supersedes the ambiguous eligibility statements in its section 1, and should be applied with `CROSS_REVIEW.md` before integration. Source/design review only; no execution.

## Unsupported caller assertions are outcomes, not measured exclusions

The original design's sentence requiring “all required checks passed and no unsupported assertions” as an eligibility conjunction is too broad. It can be read as excluding the very unsupported caller claims the study intends to measure. That would produce outcome-dependent selection bias.

Use three distinct decisions:
1. **Instrument qualification:** Positive fixtures must receive the expected supported classifications; deliberately unsupported assertions in negative fixtures must be detected and scored correctly. A checker passing a negative fixture does not mean the fixture's assertion was supported. A proposed adapter's qualification behavior must be assessed against predeclared expectations, not discarded because it was unfavorable.
2. **Measured-case inclusion:** Depends only on predeclared evidence completeness, valid treatment, pinned configuration, valid capture/view construction and any explicitly frozen cleanup eligibility requirements. Do not exclude an otherwise eligible case because its caller made an unsupported assertion or its observed substantive outcome was unfavorable. Keep inclusion reasons independent from scored outcome. Eligibility criteria must be frozen before measurement and cannot be altered to remove inconvenient results.
3. **Scored outcomes:** Report native tuple, sink conformance, baseline/projection reference classifications and every supported/unsupported/unresolved assertion for every included case. Unsupported assertions are retained negative outcomes. Structural evidence defects may legitimately preclude a claim or inclusion under the frozen rules, but a wrong claim about sound evidence is not such a defect.

Previously unknown native mappings remain a qualification/freeze blocker, not a license to discard unexpected measured outcomes. If a novel measured outcome appears after freeze, retain it, stop further collection if required, investigate and report against the predeclared mapping. Any new mapping or collection version must preserve the original outcome.

## Complementary corrections

- Make cancellation/continuation requirements conditional on cell: no cancellation for K1/K2, no execute for the proposed strict C1, prior effect before request for C4.
- Treat C1 zero attempts and C4 exact attempt schedule as proposed freeze choices, not already-established protocol requirements.
- Distinguish semantically valid consistent opaque-ID renaming from broken linkage or binding against an unchanged manifest.
- Cleanup cannot upgrade primary facts; if frozen cleanup rules make the case ineligible, preserve and report its established facts and exclusion reason.
- A later change outside a bounded certified interval does not alone falsify that interval. A pending same-operation dispatch contradicting the certificate does.

This correction incorporates independent methods-review feedback supplied by the parent and review worker. It introduces no empirical result.
