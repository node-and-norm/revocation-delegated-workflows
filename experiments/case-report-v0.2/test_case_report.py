"""PLANNED CHECK SOURCE ONLY. Not executed; separate user approval required.

Uses original archive path supplied through CASE_REPORT_ARCHIVE; no VM/network.
Creates only in-memory derived packets, receipts, report dicts and HTML strings.
"""
import os
import unittest
from copy import deepcopy
from case_report import extract, strict_json, encode, report, seal_local, unavailable, render_html, InvalidInput, ARCHIVE_HASH


class PlannedAcceptance(unittest.TestCase):
    def original(self, case):
        return extract(os.environ["CASE_REPORT_ARCHIVE"], case, "planned-" + case)

    def variant(self, case, change, name):
        raw, _ = self.original(case)
        p = strict_json(raw)
        p["packet_id"] += "-" + name
        p["fixture_kind"] = "constructed"
        p["transformations"].append(name)
        change(p)
        # Trusted fixture construction after verified extract, NOT imported input.
        return seal_local(p)

    def messages(self, result, panel):
        return "\n".join(a["text"] for a in result["panels"][panel])

    def test_a1_s4(self):
        r = report(*self.original("S4"))
        self.assertEqual(r["status"], "source_bound_under_local_custody")
        self.assertIn("UNCONFIRMED", self.messages(r, "requester"))
        self.assertIn("epoch 8", self.messages(r, "authority"))
        self.assertIn("sequence 7", self.messages(r, "authority"))
        self.assertIn("Attempt denied at sequence 9", self.messages(r, "action"))
        self.assertIn("0 entries", self.messages(r, "action"))

    def test_a2_s5(self):
        r = report(*self.original("S5"))
        self.assertIn("epoch 7", self.messages(r, "authority"))
        self.assertIn("One matching local effect entry", self.messages(r, "action"))

    def test_a3_caller_only(self):
        def change(p):
            for k in ("authority", "events", "effects"):
                p[k] = unavailable()
        r = report(*self.variant("S4", change, "omit-all-but-caller"))
        self.assertIn("UNCONFIRMED", self.messages(r, "requester"))
        self.assertIn("Request authority", self.messages(r, "authority"))
        self.assertIn("No bound attempt", self.messages(r, "action"))

    def test_a4_no_action(self):
        def change(p):
            p["events"]["items"] = [i for i in p["events"]["items"] if i["value"]["kind"] in ("bootstrap", "revocation")]
            p["events"]["coverage"]["status"] = "declared_partial"
            p["effects"] = unavailable()
        r = report(*self.variant("S4", change, "omit-action-and-effects"))
        self.assertIn("Withdrawal event", self.messages(r, "authority"))
        self.assertIn("No bound attempt", self.messages(r, "action"))

    def test_a5_denial_no_inventory(self):
        r = report(*self.variant("S4", lambda p: p.update(effects=unavailable()), "omit-effect-inventory"))
        self.assertIn("Attempt denied", self.messages(r, "action"))
        self.assertIn("cumulative effects unknown", self.messages(r, "action"))

    def test_a6_positive_unknown_coverage(self):
        def change(p):
            p["effects"]["coverage"] = {"status": "unknown", "boundary": None, "basis": None}
        r = report(*self.variant("S5", change, "withhold-completeness-declaration"))
        self.assertIn("At least 1", self.messages(r, "action"))
        self.assertIn("total count and coverage unknown", self.messages(r, "action"))

    def test_a7_same_boundary_conflict(self):
        def change(p):
            i = deepcopy(p["authority"]["items"][0])
            i.update(item_id="synthetic-conflict", origin="constructed")
            i["value"]["active"] = 0
            p["authority"]["items"].append(i)
        r = report(*self.variant("S5", change, "add-explicit-synthetic-conflicting-authority"))
        self.assertTrue(any(a["classification"] == "conflicted" for a in r["panels"]["authority"]))
        self.assertEqual(len(r["supplied_packet"]["authority"]["items"]), 2)

    def test_a8b_unrelated_effect(self):
        def change(p):
            p["effects"]["items"][0]["value"]["root"] = "unrelated"
            p["effects"]["items"][0]["origin"] = "constructed"
        r = report(*self.variant("S5", change, "change-effect-root"))
        self.assertIn("Positive effect assertion retained", self.messages(r, "action"))
        self.assertNotIn("One matching local effect entry", self.messages(r, "action"))

    def test_a8c_missing_member_hash(self):
        raw, receipt = self.original("S5")
        p = strict_json(raw)
        del p["source_member_sha256"]
        r = report(encode(p), receipt)
        self.assertEqual(r["status"], "unbound")

    def test_byte_binding_and_missing_receipt(self):
        raw, receipt = self.original("S5")
        self.assertEqual(report(raw + b"\n", receipt)["status"], "unbound")
        r = report(raw)
        self.assertEqual(r["status"], "unbound")
        self.assertTrue(r["supplied_packet"]["effects"]["items"])
        self.assertNotIn("One matching", self.messages(r, "action"))

    def test_strict_json(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'\xef\xbb\xbf{}', b'\xff'):
            with self.assertRaises(InvalidInput):
                strict_json(raw)

    def test_receipt_and_self_hash_rejection(self):
        raw, receipt = self.original("S4")
        p = strict_json(raw)
        p["packet_sha256"] = ARCHIVE_HASH
        self.assertEqual(report(encode(p), receipt)["status"], "unbound")
        r = strict_json(receipt)
        r["packet_id"] = "other"
        self.assertEqual(report(raw, encode(r))["status"], "unbound")
        r = strict_json(receipt)
        r["source_checks"][0]["expected_sha256"] = "0" * 64
        self.assertEqual(report(raw, encode(r))["status"], "unbound")

    def test_html_escape(self):
        r = report(b'{"x":"<script>alert(1)</script>"}')
        html = render_html(r)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_r1_repeated_execute_id(self):
        def change(p):
            receipt = next(i for i in p["events"]["items"] if i["value"]["kind"] == "receipt" and i["value"]["data"]["request"].get("op") == "execute")
            duplicate = deepcopy(receipt)
            duplicate.update(item_id="duplicate-execute", origin="constructed")
            duplicate["value"]["seq"] = 8
            p["events"]["items"].append(duplicate)
        r = report(*self.variant("S5", change, "repeat-execute-request-id"))
        self.assertIn("Repeated execute request ID", self.messages(r, "action"))
        self.assertNotIn("One matching local effect", self.messages(r, "action"))
        self.assertNotIn("Matching effect event", self.messages(r, "action"))

    def test_r1_effect_result_and_event_kind(self):
        for mutation in ("outcome", "kind"):
            def change(p):
                event = next(i for i in p["events"]["items"] if i["value"]["kind"] == "effect")
                event["origin"] = "constructed"
                if mutation == "outcome":
                    event["value"]["data"]["result"]["outcome"] = "denied"
                else:
                    event["value"]["kind"] = "denied"
            r = report(*self.variant("S5", change, "inconsistent-effect-" + mutation))
            self.assertNotIn("One matching local effect", self.messages(r, "action"))
            self.assertNotIn("Matching effect event", self.messages(r, "action"))

    def test_r1_payload_not_request(self):
        def change(p):
            event = next(i for i in p["events"]["items"] if i["value"]["kind"] == "effect")
            event["origin"] = "constructed"
            event["value"]["data"]["result"]["payload"] = "different"
            effect = p["effects"]["items"][0]
            effect["origin"] = "constructed"
            effect["value"]["payload"] = "different"
        r = report(*self.variant("S5", change, "effect-and-inventory-payload-not-request"))
        self.assertNotIn("One matching local effect", self.messages(r, "action"))
        self.assertNotIn("Matching effect event", self.messages(r, "action"))

    def test_r1_unrelated_authority(self):
        def change(p):
            item = p["authority"]["items"][0]
            item["origin"] = "constructed"
            item["value"]["root"] = "unrelated"
        r = report(*self.variant("S5", change, "unrelated-snapshot-root"))
        self.assertTrue(any(a["classification"] == "unbound" and a["rule"] == "snapshot-context-root-mismatch" for a in r["panels"]["authority"]))
        self.assertEqual(r["supplied_packet"]["authority"]["items"][0]["value"]["root"], "unrelated")

    def test_r1_conflict_requests_evidence(self):
        def change(p):
            item = deepcopy(p["authority"]["items"][0])
            item.update(item_id="conflict-request", origin="constructed")
            item["value"]["active"] = 0
            p["authority"]["items"].append(item)
        r = report(*self.variant("S5", change, "same-boundary-conflict-request"))
        self.assertIn("Request original authority/event records", self.messages(r, "authority"))

    def test_r2_duplicate_effect_is_not_another_effect(self):
        def change(p):
            p["effects"]["coverage"] = {"status": "unknown", "boundary": None, "basis": None}
            item = deepcopy(p["effects"]["items"][0])
            item.update(item_id="constructed-copy-of-effect", origin="constructed")
            p["effects"]["items"].append(item)
        r = report(*self.variant("S5", change, "duplicate-effect-evidence-in-incomplete-inventory"))
        self.assertEqual(len(r["supplied_packet"]["effects"]["items"]), 2)
        self.assertIn("At least 1 distinct matched recorded effect identities", self.messages(r, "action"))
        self.assertNotIn("At least 2", self.messages(r, "action"))
        self.assertTrue(any(a["classification"] == "duplicate_evidence" for a in r["panels"]["action"]))


# No automatic unittest.main(): run only through separately approved discovery.
