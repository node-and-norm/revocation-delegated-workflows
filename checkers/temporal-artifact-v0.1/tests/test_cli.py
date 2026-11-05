import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from temporal_checker.__main__ import main


class CliTests(unittest.TestCase):
    def invoke(self, args, report=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr), patch(
            "temporal_checker.__main__.check_bundle", return_value=report or {"native_qualification": False, "requirements": {"integrity": "unsatisfied"}}
        ) as checker:
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue(), checker

    def test_report_generation_not_scientific_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            code, out, err, checker = self.invoke([temp])
            self.assertEqual(code, 0)
            self.assertFalse(json.loads(out)["native_qualification"])
            self.assertEqual(err, "")
            checker.assert_called_once()

    def test_output_same_as_stdout_and_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "case"
            root.mkdir()
            output = Path(temp) / "result.json"
            code, out, err, _ = self.invoke([str(root), "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertEqual(output.read_text(), out)
            self.assertEqual(self.invoke([str(root)])[1], out)

    def test_inside_output_rejected_without_checking_or_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            code, out, err, checker = self.invoke([temp, "--output", str(Path(temp) / "result.json")])
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertIn("outside CASE_DIR", err)
            checker.assert_not_called()
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_existing_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "case"
            root.mkdir()
            output = Path(temp) / "result.json"
            output.write_text("existing")
            code, _, _, checker = self.invoke([str(root), "--output", str(output)])
            self.assertEqual(code, 2)
            self.assertEqual(output.read_text(), "existing")
            checker.assert_not_called()

    def test_symlink_to_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "case"
            root.mkdir()
            evidence = root / "registry.json"
            evidence.write_text("evidence")
            output = Path(temp) / "result.json"
            output.symlink_to(evidence)
            code, _, _, checker = self.invoke([str(root), "--output", str(output)])
            self.assertEqual(code, 2)
            self.assertEqual(evidence.read_text(), "evidence")
            checker.assert_not_called()

    def test_missing_case_is_error(self):
        with tempfile.TemporaryDirectory() as temp:
            code, out, err, checker = self.invoke([str(Path(temp) / "missing")])
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertFalse(json.loads(err)["report_generated"])
            checker.assert_not_called()

    def test_nonfinite_report_is_error_not_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp:
            code, out, err, _ = self.invoke([temp], {"invalid": float("nan")})
            self.assertEqual(code, 2)
            self.assertEqual(out, "")
            self.assertFalse(json.loads(err)["report_generated"])


if __name__ == "__main__":
    unittest.main()
