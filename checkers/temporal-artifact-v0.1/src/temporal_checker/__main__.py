"""Local-only command-line report generation; an exit code is not qualification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .engine import check_bundle


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check saved synthetic artifacts without executing Temporal or the gateway.",
        epilog="Exit 0 means a report was generated, not that requirements passed or native behavior was qualified.",
    )
    parser.add_argument("case_dir", type=Path, help="Existing saved synthetic case directory")
    parser.add_argument("--output", type=Path, help="Also write JSON to a new file outside CASE_DIR; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        root = args.case_dir.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("CASE_DIR must be a directory")
        output = None
        if args.output is not None:
            output = args.output.resolve()
            if output == root or output.is_relative_to(root):
                raise ValueError("--output must be outside CASE_DIR to preserve evidence")
            # Reject even dangling links. Exclusive creation below also prevents
            # overwriting an existing hard link to an input or other user file.
            if args.output.is_symlink() or output.exists():
                raise ValueError("--output must name a new file; overwriting is forbidden")
            if not output.parent.is_dir():
                raise ValueError("--output parent directory must already exist")
        report = check_bundle(root)
        encoded = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if output is not None:
            with output.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(encoded)
        sys.stdout.write(encoded)
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        sys.stderr.write(json.dumps({"error": str(error), "report_generated": False}, sort_keys=True, allow_nan=False) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
