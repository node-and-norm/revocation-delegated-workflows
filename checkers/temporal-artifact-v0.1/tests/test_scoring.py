import copy
import unittest

from temporal_checker.scoring import (FIELDS, VALUES, CATEGORIES, aggregate_reports,
                                      planned_opportunities, score_assertions)


def ref(record="e1", phase="P1"):
    return dict(artifact_id="sink", locator="/events/0", record_id=record,
                phase=phase, cut_id="cut1", boundary_id="boundary1")


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.field = "effect_existence"
        self.reference = {self.field: {"value": "present", "evidence_refs": [ref()]}}
        self.context = dict(phase="P1", scope="op1", permitted_refs=[ref()],
                            evidence_supplied=True, strict_refs=True)
        self.claim = dict(field=self.field, value="present", observer="caller",
                          scope="op1", assertion_phase="P1", evidence_refs=[ref()])

    def score(self, claims=None):
        return score_assertions([self.field], self.reference,
                                [self.claim] if claims is None else claims, self.context)

    def category(self, expected, claims=None):
        result = self.score(claims)
        self.assertEqual(result["counts"][expected], 1)
        self.assertEqual(sum(result["counts"].values()), 1)
        return result

    def test_correct_determinate_and_structured_refs_preserved(self):
        result = self.category("correct_determinate")
        self.assertEqual(result["opportunities"][0]["evidence_refs"], [ref()])
        self.assertEqual(result["metrics"]["conclusive_coverage"], 1)

    def test_six_exact_categories(self):
        self.category("correct_determinate")
        self.claim["value"] = "unresolved"
        self.claim["evidence_refs"] = []
        self.category("avoidable_unresolved")
        self.reference[self.field]["value"] = "unresolved"
        self.category("justified_unresolved")
        self.claim["value"] = "present"
        self.category("unsupported_determinate")
        self.reference[self.field]["value"] = "absent_with_complete_bounded_evidence"
        self.category("contradicted")
        self.category("malformed_or_omitted", [])

    def test_no_determinate_support_rate_is_undefined(self):
        self.claim["value"] = "unresolved"
        self.claim["evidence_refs"] = []
        result = self.score()
        self.assertEqual(result["metrics"]["conclusive_coverage"], 0)
        self.assertIsNone(result["metrics"]["determinate_claim_support_rate"])
        self.assertEqual(result["metrics"]["required_output_completion"], 1)

    def test_missing_evidence_is_not_missing_caller_output(self):
        self.context["evidence_supplied"] = False
        result = score_assertions([self.field], {}, None, self.context)
        self.assertEqual(result["evaluated_opportunities"], 0)
        self.assertEqual(sum(result["counts"].values()), 0)
        self.assertEqual(result["opportunities"][0]["status"], "evidence_unavailable")

    def test_missing_output_when_supplied_is_omitted(self):
        result = score_assertions([self.field], self.reference, None, self.context)
        self.assertEqual(result["counts"]["malformed_or_omitted"], 1)

    def test_hidden_truth_never_supplies_decidability(self):
        self.context["permitted_refs"] = []
        self.claim["value"] = "absent_with_complete_bounded_evidence"
        self.claim["evidence_refs"] = []
        result = self.category("unsupported_determinate")
        self.assertEqual(result["reference_decidable_opportunities"], 0)
        self.claim["value"] = "unresolved"
        self.category("justified_unresolved")

    def test_extra_hidden_reference_does_not_pass(self):
        self.claim["evidence_refs"].append(ref("hidden", "P2"))
        self.category("unsupported_determinate")

    def test_no_support_reference_is_unsupported(self):
        self.claim["evidence_refs"] = []
        self.category("unsupported_determinate")

    def test_contradiction_precedes_insufficient_citation(self):
        self.claim["value"] = "absent_with_complete_bounded_evidence"
        self.claim["evidence_refs"] = []
        self.category("contradicted")

    def test_malformed_claim_dimensions(self):
        original = copy.deepcopy(self.claim)
        mutations = [("observer", " "), ("scope", "wrong"),
                     ("assertion_phase", "P2"), ("value", "safely_stopped"),
                     ("value", []), ("evidence_refs", "e1"),
                     ("evidence_refs", ["e1"]), ("evidence_refs", [ref(), ref()]),
                     ("extra", 1)]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                self.claim = copy.deepcopy(original)
                self.claim[key] = value
                self.category("malformed_or_omitted")
        self.claim = original
        del self.claim["scope"]
        self.category("malformed_or_omitted")

    def test_duplicate_claims_fail_even_when_identical(self):
        self.category("malformed_or_omitted", [self.claim, copy.deepcopy(self.claim)])

    def test_unknown_field_retained_without_diluting_denominator(self):
        other = dict(self.claim, field="safely_stopped")
        result = self.category("correct_determinate", [self.claim, other])
        self.assertEqual(result["diagnostics"][0]["field"], "safely_stopped")
        self.assertEqual(result["planned_opportunities"], 1)

    def test_reference_canonical_order_does_not_matter(self):
        self.claim["evidence_refs"] = [dict(reversed(list(ref().items())))]
        self.category("correct_determinate")

    def test_future_phase_may_not_be_in_primary_allowlist(self):
        self.context["permitted_refs"].append(ref("later", "P2"))
        with self.assertRaises(ValueError):
            self.score()

    def test_p2_can_use_earlier_permitted_evidence(self):
        self.context["phase"] = self.claim["assertion_phase"] = "P2"
        self.category("correct_determinate")

    def test_unresolved_hidden_citation_is_malformed(self):
        self.claim["value"] = "unresolved"
        self.claim["evidence_refs"] = [ref("hidden")]
        self.category("malformed_or_omitted")

    def test_exact_terminal_discriminator_is_not_guessed_native_outcome(self):
        field = "workflow_execution"
        reference = {field: dict(value="exact_terminal_status", evidence_refs=[ref()])}
        claims = [dict(self.claim, field=field, value="exact_terminal_status")]
        result = score_assertions([field], reference, claims, self.context)
        self.assertEqual(result["counts"]["correct_determinate"], 1)
        claims[0]["value"] = "canceled"
        result = score_assertions([field], reference, claims, self.context)
        self.assertEqual(result["counts"]["malformed_or_omitted"], 1)

    def test_planned_94_opportunities_and_missingness(self):
        self.assertEqual(planned_opportunities(), 94)
        self.assertEqual(planned_opportunities(["M1", "K1"]), 27)
        result = aggregate_reports([self.score()], 94)
        self.assertEqual(result["planned_opportunities"], 94)
        self.assertEqual(result["evidence_unavailable_opportunities"], 93)
        self.assertEqual(result["metrics"]["planned_completion"], 1 / 94)
        self.assertEqual(result["evaluated_opportunities"], 1)
        with self.assertRaises(ValueError):
            planned_opportunities(["M1", "M1"])
        with self.assertRaises(ValueError):
            aggregate_reports([self.score()], 0)

    def test_all_unresolved_94_no_conclusive_credit(self):
        reports = []
        for cell in ("M1", "M2", "M3", "M4", "K1", "K2"):
            fields = list(FIELDS) if cell.startswith("M") else [f for f in FIELDS if f not in ("activity_call", "activity_execution", "workflow_execution")]
            for phase in (("P1", "P2") if cell.startswith("M") else ("P1",)):
                reference = {f: dict(value=sorted(VALUES[f] - {"unresolved"})[0], evidence_refs=[ref()]) for f in fields}
                claims = [dict(self.claim, field=f, value="unresolved", assertion_phase=phase, evidence_refs=[]) for f in fields]
                reports.append(score_assertions(fields, reference, claims, dict(self.context, phase=phase)))
        result = aggregate_reports(reports, 94)
        self.assertEqual(result["counts"]["avoidable_unresolved"], 94)
        self.assertEqual(result["metrics"]["conclusive_coverage"], 0)
        self.assertIsNone(result["metrics"]["determinate_claim_support_rate"])
        self.assertEqual(result["metrics"]["required_output_completion"], 1)

    def test_nonfinite_caller_values_and_refs_do_not_escape_report(self):
        import json
        for value in (float("nan"), float("inf"), float("-inf")):
            self.claim["value"] = value
            result = self.category("malformed_or_omitted")
            json.dumps(result, allow_nan=False)
            self.claim["value"] = "present"
            self.claim["evidence_refs"] = [value]
            result = self.category("malformed_or_omitted")
            json.dumps(result, allow_nan=False)
            self.claim["evidence_refs"] = [ref()]

    def test_removing_support_cannot_strengthen(self):
        self.category("correct_determinate")
        self.reference[self.field]["evidence_refs"].append(ref("e2"))
        self.context["permitted_refs"].append(ref("e2"))
        self.category("unsupported_determinate")
        self.claim["evidence_refs"].append(ref("e2"))
        self.category("correct_determinate")
        self.context["permitted_refs"].pop()
        self.category("unsupported_determinate")


if __name__ == "__main__":
    unittest.main()
