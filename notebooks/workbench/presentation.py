"""Small accessible HTML/SVG views with plain-text fallbacks. No JS or assets."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html import escape
import json
from urllib.parse import quote

from .core import BASE_COMMIT, ARCHIVE, RECORDS, SUMMARY, barrier_rows

INK = "#183044"
TEAL = "#076b70"
AMBER = "#8a4b08"
LIGHT = "#f2f6f8"
_display_sink = None


@dataclass
class View:
    text: str
    html: str = ""
    svg: str = ""

    def _repr_mimebundle_(self, **kwargs):
        data = {"text/plain": self.text}
        if self.html:
            data["text/html"] = self.html
        if self.svg:
            data["image/svg+xml"] = self.svg
        return data


def show(view):
    """Display in Jupyter; print readable text when run as ordinary Python."""
    if _display_sink is not None:
        _display_sink(view)
        return
    try:
        from IPython import get_ipython
        from IPython.display import display
        if get_ipython() is not None:
            display(view)
            return
    except ImportError:
        pass
    print(view.text)


def link(path, label=None):
    url = f"https://github.com/node-and-norm/revocation-delegated-workflows/blob/{BASE_COMMIT}/{quote(path)}"
    return f'<a href="{url}">{escape(label or path)}</a>'


def table(headers, rows, title="", note=""):
    rows = [[str(x) for x in r] for r in rows]
    plain = (title + "\n" if title else "") + " | ".join(headers) + "\n"
    plain += "\n".join(" | ".join(r) for r in rows) + ("\n" + note if note else "")
    html = f'<h3>{escape(title)}</h3>' if title else ""
    html += '<table style="border-collapse:collapse;width:100%;font-size:14px"><thead><tr>'
    html += "".join(f'<th style="text-align:left;padding:9px;border-bottom:2px solid {TEAL}">{escape(h)}</th>' for h in headers)
    html += "</tr></thead><tbody>"
    for i, row in enumerate(rows):
        html += f'<tr style="background:{LIGHT if i % 2 == 0 else "#ffffff"}">'
        html += "".join(f'<td style="vertical-align:top;padding:9px;border-bottom:1px solid #d6e0e6">{escape(x)}</td>' for x in row)
        html += "</tr>"
    html += "</tbody></table>"
    if not rows:
        html += "<p>No records match this filter. No conclusion follows.</p>"
        plain += "\nNo records match this filter. No conclusion follows."
    if note:
        html += f"<p><small>{escape(note)}</small></p>"
    return View(plain, html)


def overview(run):
    b = run.brief()
    return table(["Saved cases", "Effects", "Revoked denials", "Fenced cases", "Post-fence effects"],
                 [[b["selected_cases"], b["effects"], b["revoked_denials"], b["cases_with_fence"],
                   b["post_fence_effects_in_fenced_cases"] if b["cases_with_fence"] else "N/A — no fenced cases"]],
                 "Historical evidence • selected scope",
                 f"{b['no_fence_cases']} selected cases have no fence in the recorded window and are excluded from the post-fence question. These are fixed cases, not independent samples. Temporal native qualification remains blocked.")


def case_matrix(rows):
    labels = {"IDLE": "IDLE (no request)", "INSTALLED_CONFIRMED": "CONFIRMED",
              "UNCONFIRMED_AT_OBSERVATION_END": "UNCONFIRMED at window end"}
    return table(["Path / case", "Acceptance", "Sink fence", "Caller", "Effect / denial", "After fence"],
                 [[f"{r['path']} / {r['schedule']}", "volatile" if r["request_accepted"] else "none",
                   f"seq {r['fence_seq']}" if r["fence_seq"] is not None else "none in window",
                   labels[r["caller_state"]],
                   "effect: " + ", ".join(map(str, r["effect_sequences"])) if r["effect_count"] else "denied: " + str(r["reason"]),
                   r["post_fence_effect_count"] if r["fence_seq"] is not None else "N/A — no fence"] for r in rows],
                 "Acceptance, sink reality and caller knowledge are separate columns",
                 "Derived from saved record.json files and reconciled with the historical summary. Sequence numbers are local sink transaction order, not time. Original no-fence post_fence_effect_count=0 values remain unchanged in the source.")


def glossary_view(store):
    keys = {"request_accepted", "fence_installed", "caller_confirmation", "effect", "unconfirmed"}
    return table(["Term", "Source definition (verbatim)", "Does not imply (verbatim)"],
                 [[t["label"], t["definition"], t["does_not_imply"]]
                  for t in store.glossary["terms"] if t["term_key"] in keys],
                 "Vocabulary • source definitions, not notebook conclusions",
                 f"{RECORDS}/glossary.json • draft definitions v0.1, retained without edits.")


def source_inventory(store):
    return table(["Source key", "Kind", "Repository locator", "SHA-256 (prefix)"],
                 [[s["source_key"], s["source_kind"], s["repository_path"] +
                   (" :: " + s["archive_member"] if s.get("archive_member") else ""), s["sha256"][:16]]
                  for s in store.sources.values()], "Ten source snapshots • exact bytes verified",
                 "Full digests and paths are in evidence.receipts and the retained source manifest. Hash equality establishes byte identity, not authenticity, truth or execution attestation.")


def claim_view(records):
    return table(["Record", "Historical claim (verbatim)", "Historical status", "Source / locator"],
                 [[r["record_key"], r["claim"], r["known_status"],
                   "; ".join(f"{s['source_key']}: {s['locator']}" for s in r["source_refs"])] for r in records],
                 "Registry snapshot • as of 2026-11-04",
                 "Source-review findings are not empirical results. unchecked_success and current_gate require the dated Nov 5 prototype overlay below. Every record's uncertainty and AI-use text is available in evidence.registry.")


def raw_json(value, title, locator=""):
    content = json.dumps(value, indent=2, ensure_ascii=False)
    return View(title + "\n" + locator + "\n" + content,
                f"<h3>{escape(title)}</h3><p><small>{escape(locator)}</small></p><pre>{escape(content)}</pre>")


def excerpt(store, source_key, start_line=1, line_count=14):
    lines = store.source_text(source_key).splitlines()
    if type(start_line) is not int or type(line_count) is not int or start_line < 1 or line_count < 1 or start_line > len(lines):
        raise ValueError("Choose a positive line range within the source")
    end = min(len(lines), start_line + line_count - 1)
    selected = "\n".join(lines[start_line - 1:end])
    source = store.sources[source_key]
    loc = source["repository_path"] + (" :: " + source["archive_member"] if source.get("archive_member") else "")
    heading = f"Source excerpt • {source_key} • lines {start_line}–{end}"
    return View(heading + "\n" + loc + "\n" + selected,
                f"<h3>{escape(heading)}</h3><p>{link(source['repository_path'])}<br>{escape(source.get('archive_member', ''))}</p><pre>{escape(selected)}</pre><p><small>Verbatim slice. No ellipsis, normalization or generated text inside the excerpt.</small></p>")


def _svg_start(width, height, title, description):
    key = sha256(title.encode()).hexdigest()[:12]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title-{key} desc-{key}">'
            f'<title id="title-{key}">{escape(title)}</title><desc id="desc-{key}">{escape(description)}</desc>'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>'
            '<g font-family="Arial, sans-serif">')


def _text(x, y, text, size=14, fill=INK, weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{escape(str(text))}</text>'


def workflow_map():
    steps = [("01 SCOPE", "Bounded question", "Paths + schedules"),
             ("02 VERIFY", "Pinned local bytes", "Stop on mismatch"),
             ("03 RECONCILE", "Saved raw ↔ summary", "12 fixed cases"),
             ("04 RETRIEVE", "Select evidence", "No live research"),
             ("05 CHALLENGE", "3 counterexample tests", "Keep unresolved"),
             ("06 BRIEF", "Findings + audit", "Sources + limits")]
    svg = _svg_start(1000, 260, "Implemented offline evidence workflow",
                     "Six deterministic Python stages. A source mismatch stops before retrieval and reporting. No LangGraph or model runtime is active.")
    svg += _text(24, 32, "ONE QUESTION. SIX INSPECTABLE STAGES.", 20, INK, "bold")
    for i, (title, line1, line2) in enumerate(steps):
        x = 24 + i * 162
        svg += f'<rect x="{x}" y="62" width="150" height="116" rx="8" fill="{LIGHT}" stroke="#b6cbd6"/>'
        svg += _text(x + 12, 89, title, 13, TEAL, "bold")
        svg += _text(x + 12, 119, line1, 12)
        svg += _text(x + 12, 144, line2, 12)
        if i < 5:
            svg += _text(x + 151, 128, "›", 21, TEAL)
    svg += _text(24, 216, "HARD STOP: missing inputs, changed bytes, or failed selected consistency checks → no brief", 14, AMBER, "bold")
    svg += _text(24, 242, "Implemented: ordinary Python  •  Not active: LLMs, web retrieval, LangGraph, Temporal, background agents", 13)
    svg += "</g></svg>"
    return View(" → ".join(x[0] for x in steps) + "\nStop on invalid evidence. Ordinary Python; no LangGraph or model runtime.", svg=svg)


def barrier_view(record):
    rows = barrier_rows(record)
    n = len(rows)
    width = 1020
    cell = (width - 40) / n
    title = f"{record['path']} / {record['schedule']} • saved barrier captures"
    description = " | ".join(f"{r['capture']} {r['barrier']}: caller {r['caller']}, fence {r['fence']}, effects {r['effects']}" for r in rows)
    svg = _svg_start(width, 332, title, description)
    svg += _text(20, 33, title, 21, INK, "bold")
    svg += _text(20, 58, "Read left to right: capture order only. Spacing does not encode elapsed time.", 14)
    for i, row in enumerate(rows):
        x = 20 + i * cell
        svg += f'<rect x="{x}" y="86" width="{cell - 10}" height="186" rx="8" fill="{LIGHT}" stroke="#b6cbd6"/>'
        svg += _text(x + 12, 111, f"CAPTURE {row['capture']}", 12, TEAL, "bold")
        # Break on underscores rather than allow a long barrier/state to overflow.
        for j, part in enumerate(row["barrier"].split("_")):
            svg += _text(x + 12, 135 + j * 16, part, 14, INK, "bold")
        caller = {"INSTALLED_CONFIRMED": "CONFIRMED", "UNCONFIRMED_AT_OBSERVATION_END": "UNCONFIRMED"}.get(row["caller"], row["caller"])
        svg += _text(x + 12, 205, "Caller: " + caller, 12)
        svg += _text(x + 12, 229, "Fence: " + (f"seq {row['fence']}" if row["fence"] is not None else "none recorded"), 12)
        svg += _text(x + 12, 253, f"Effects: {row['effects']}", 12, AMBER if row["effects"] else INK, "bold")
    svg += _text(20, 300, f"Source: {ARCHIVE} ::", 11)
    svg += _text(20, 318, f"measured01/{record['path']}/{record['schedule']}/record.json → barriers[] (saved historical JSON)", 12)
    svg += "</g></svg>"
    return View(title + "\n" + description, svg=svg)


def brief_view(run):
    b = run.brief()
    post_fence = (f"{b['post_fence_effects_in_fenced_cases']} post-fence effects in {b['cases_with_fence']} fenced cases."
                  if b['cases_with_fence'] else "Post-fence question: N/A; no fenced cases selected.")
    rows = [["Scope", f"{b['selected_cases']} selected saved cases; paths={run.scope.paths}; schedules={run.scope.schedules}"],
            ["Derived accounting", f"{b['effects']} effects; {b['revoked_denials']} revoked denials; {post_fence}"],
            ["Counterexamples", "; ".join(f"{c['claim_id']}: {', '.join(c['witnesses']) or 'unresolved in selection'}" for c in b["challenge_results"])],
            ["Evidence boundary", b["basis"]],
            ["Temporal status", b["temporal"]],
            ["Limits", "; ".join(b["limits"])],
            ["Next decision", "Review this interface and source traceability. No new native experiment, API call, public release or claim of reviewer benefit is enabled."]]
    view = table(["Decision brief", "Account"], rows, "Bounded synthesis • generated from this selection")
    view.html += "<p>Canonical source: " + link(SUMMARY, "historical summary") + " · " + link(ARCHIVE, "saved raw archive") + "</p>"
    return view
