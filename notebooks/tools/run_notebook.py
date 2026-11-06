#!/usr/bin/env python3
"""Execute every code cell in a fresh process, without starting a Jupyter server.

This is an explicit lightweight verification runner, not nbclient or a Jupyter
kernel. All notebook outputs are explicit show()/print() calls. The runner
captures their actual values, rejects errors, and can save outputs for GitHub.
The default only checks. --write updates the derived notebook, never inputs.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "notebooks"))
from workbench import presentation


def validate(notebook):
    if notebook.get("nbformat") != 4 or notebook.get("nbformat_minor") != 5:
        raise ValueError("Expected nbformat 4.5")
    ids = set()
    for cell in notebook["cells"]:
        cid = cell["id"]
        if cid in ids or not cid or len(cid) > 64 or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in cid):
            raise ValueError("Invalid or repeated notebook cell id")
        ids.add(cid)
        if cell["cell_type"] not in ("markdown", "code") or not isinstance(cell["metadata"], dict):
            raise ValueError("Unsupported cell structure")
        if not isinstance(cell["source"], (str, list)):
            raise ValueError("Invalid cell source")
        if cell["cell_type"] == "code":
            if not isinstance(cell["outputs"], list):
                raise ValueError("Missing output list")
            compile("".join(cell["source"]), f"cell:{cid}", "exec")


def execute(path):
    notebook = json.loads(path.read_text())
    validate(notebook)
    namespace = {"__name__": "__main__"}
    count = 0
    running = False
    original_cwd = Path.cwd()

    def guard(event, args):
        if not running:
            return
        if event in ("socket.__new__", "socket.connect", "subprocess.Popen", "os.system"):
            raise RuntimeError(f"Offline verification blocked {event}")
        if event == "open":
            _, mode, flags = args
            if (isinstance(mode, str) and any(x in mode for x in "wax+")) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)):
                raise RuntimeError("Notebook attempted a file write")
        if event in ("os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.chmod", "os.link", "os.symlink"):
            raise RuntimeError(f"Notebook attempted a filesystem change: {event}")

    sys.addaudithook(guard)
    try:
        os.chdir(path.parent)
        running = True
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            count += 1
            outputs = []
            stream = io.StringIO()

            def capture(view):
                # Flush prints before rich output to preserve output ordering.
                if stream.tell():
                    outputs.append({"output_type": "stream", "name": "stdout", "text": stream.getvalue()})
                    stream.seek(0); stream.truncate(0)
                outputs.append({"output_type": "display_data", "data": view._repr_mimebundle_(), "metadata": {}})

            presentation._display_sink = capture
            with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                exec(compile("".join(cell["source"]), f"{path.name}:{cell['id']}", "exec"), namespace)
            if stream.getvalue():
                outputs.append({"output_type": "stream", "name": "stdout", "text": stream.getvalue()})
            cell["execution_count"] = count
            cell["outputs"] = outputs
    finally:
        running = False
        presentation._display_sink = None
        os.chdir(original_cwd)
    notebook["metadata"]["workbench_execution"] = {
        "method": "fresh-process sequential Python, explicit rich-output capture; not a Jupyter kernel run",
        "network_and_subprocesses": "blocked during cell execution",
        "file_mutation": "blocked during cell execution",
        "code_cells": count,
        "result": "all cells completed",
    }
    validate(notebook)
    return notebook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", nargs="?", type=Path, default=ROOT / "notebooks/01_revocation_evidence_workbench.ipynb")
    parser.add_argument("--write", action="store_true", help="Replace this derived notebook's saved outputs")
    args = parser.parse_args()
    path = args.notebook.resolve()
    notebook = execute(path)
    payload = json.dumps(notebook, indent=1, ensure_ascii=False) + "\n"
    if args.write:
        path.write_text(payload)
    print(json.dumps({"result": "PASS", "code_cells": notebook["metadata"]["workbench_execution"]["code_cells"],
                      "method": notebook["metadata"]["workbench_execution"]["method"],
                      "saved_outputs": args.write,
                      "output_sha256": hashlib.sha256(payload.encode()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
