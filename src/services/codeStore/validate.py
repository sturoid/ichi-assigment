"""Standard-library validator for store.json. Returns a list of problems; empty means valid.

It checks the contract a check relies on, not just the shape: every index entry
points at a cell that carries that key, keys and ids are re-derived from each
cell's dims and printed labels, values agree with their printed text, every cell
is code text from a document in the manifest, and conditions are never claimed
complete before their text is loaded.

It cannot prove the store matches its sources: a consistent edit (a value and its
printed text both changed) passes here. That is what ``Store.load(path, manifest)``
is for: it rebuilds from the sources and requires identical bytes.
"""
from __future__ import annotations

import math

from .store import AUTHORITIES, DOC_STATUSES, STORE_SCHEMA_VERSION, cell_id, cell_keys

_DOC_REQUIRED = {"id": str, "kind": str, "status": str, "authority": str}
_PROV_REQUIRED = {"id": str, "kind": str, "short_name": str, "title": str, "dimensions": dict,
                  "table_footnotes": list, "conditions_loaded": bool, "cells": list, "index": dict,
                  "warnings": list, "review_items": list, "grid_file": str, "source": dict}
_CELL_REQUIRED = {"id": str, "dims": dict, "value_kind": str, "value_text": str, "printed": dict,
                  "conditions": list, "authority": str, "source": dict, "keys": list}
_VALUE_KINDS = {"number", "unlimited", "text", "empty", "not_permitted", "not_required"}


def _need(obj: dict, required: dict, where: str, errs: list[str]) -> bool:
    ok = True
    for k, t in required.items():
        if k not in obj:
            errs.append(f"{where}: missing {k!r}")
            ok = False
        elif not isinstance(obj[k], t):
            errs.append(f"{where}: {k!r} should be {t.__name__}, got {type(obj[k]).__name__}")
            ok = False
    return ok


def validate_store(store: dict) -> list[str]:
    errs: list[str] = []
    if store.get("schema_version") != STORE_SCHEMA_VERSION:
        errs.append(f"schema_version is {store.get('schema_version')!r}, expected {STORE_SCHEMA_VERSION!r}")
    docs = store.get("documents")
    provs = store.get("provisions")
    if not isinstance(docs, list) or not isinstance(provs, dict):
        return errs + ["store needs a 'documents' list and a 'provisions' object"]

    doc_ids: dict[str, dict] = {}
    for i, d in enumerate(docs):
        where = f"documents[{i}]"
        if not _need(d, _DOC_REQUIRED, where, errs):
            continue
        if d["id"] in doc_ids:
            errs.append(f"{where}: duplicate id {d['id']!r}")
        doc_ids[d["id"]] = d
        if d["status"] not in DOC_STATUSES:
            errs.append(f"{where}: status {d['status']!r} not in {DOC_STATUSES}")
        if d["authority"] not in AUTHORITIES:
            errs.append(f"{where}: authority {d['authority']!r} not in {AUTHORITIES}")
        if d["status"] == "available":
            if not d.get("files"):
                errs.append(f"{where}: available document has no files")
            for f in d.get("files", []):
                if not isinstance(f.get("sha256"), str) or len(f["sha256"]) != 64:
                    errs.append(f"{where}: file {f.get('path')!r} has no sha256")
                if ":" in f.get("path", "")[2:] or f.get("path", "").startswith(("/", "\\")):
                    errs.append(f"{where}: file path {f.get('path')!r} must be relative")
        elif d.get("files"):
            errs.append(f"{where}: unavailable document lists files")

    for pid, p in provs.items():
        where = f"provisions[{pid!r}]"
        if not _need(p, _PROV_REQUIRED, where, errs):
            continue
        if p["id"] != pid:
            errs.append(f"{where}: id {p['id']!r} differs from its key")
        doc = doc_ids.get(pid)
        if doc is None:
            errs.append(f"{where}: no document with this id in the manifest")
        elif doc["status"] != "available":
            errs.append(f"{where}: its document is marked {doc['status']!r}")
        if ":" in p["grid_file"]:
            errs.append(f"{where}: grid_file {p['grid_file']!r} contains ':' (not a valid Windows filename)")
        dims = p["dimensions"]
        order = dims.get("order", [])
        values = dims.get("values", {})
        if set(order) != set(values):
            errs.append(f"{where}: dimensions.order {order} and dimensions.values {sorted(values)} differ")

        cell_ids: dict[str, dict] = {}
        for j, c in enumerate(p["cells"]):
            cw = f"{where}.cells[{j}]"
            if not _need(c, _CELL_REQUIRED, cw, errs):
                continue
            if c["id"] in cell_ids:
                errs.append(f"{cw}: duplicate cell id {c['id']!r}")
            cell_ids[c["id"]] = c
            if c["authority"] != "code_text":
                errs.append(f"{cw}: authority {c['authority']!r}; a table cell cited as code must be 'code_text'")
            if c["source"].get("document") != pid:
                errs.append(f"{cw}: source.document {c['source'].get('document')!r} is not {pid!r}")
            if c["value_kind"] not in _VALUE_KINDS:
                errs.append(f"{cw}: value_kind {c['value_kind']!r} unknown")
            v, kind, vt = c.get("value"), c["value_kind"], c["value_text"]
            tokens = dims.get("value_tokens", {})
            if kind == "number":
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                    errs.append(f"{cw}: value_kind 'number' but value is {v!r}")
                else:
                    try:
                        if float(vt) != v:
                            errs.append(f"{cw}: value {v!r} disagrees with printed text {vt!r}")
                    except ValueError:
                        errs.append(f"{cw}: value {v!r} but printed text {vt!r} is not a number")
            else:
                if v is not None:
                    errs.append(f"{cw}: value_kind {kind!r} must have value null, got {v!r}")
                if vt in tokens and tokens[vt] != kind:
                    errs.append(f"{cw}: printed {vt!r} means {tokens[vt]!r}, not {kind!r}")
            if c.get("unit") != p.get("unit"):
                errs.append(f"{cw}: unit {c.get('unit')!r} differs from the table's {p.get('unit')!r}")
            if set(c["dims"]) != set(order):
                errs.append(f"{cw}: dims {sorted(c['dims'])} do not match order {order}")
                continue
            labels = c["printed"].get("row_labels", {})
            for d in order[:-1]:
                want = [a.strip() for a in labels.get(d, "").split(",")] if isinstance(c["dims"][d], list) \
                    else labels.get(d)
                if c["dims"][d] != want:
                    errs.append(f"{cw}: dims[{d!r}] {c['dims'][d]!r} disagrees with printed label {labels.get(d)!r}")
            if not set(labels) >= set(order[:-1]) or c["id"] != cell_id(pid, labels, order, c["dims"][order[-1]]):
                errs.append(f"{cw}: id {c['id']!r} does not match its printed labels and column")
            if sorted(c["keys"]) != sorted(cell_keys(c["dims"], order)):
                errs.append(f"{cw}: keys {c['keys']} are not the keys of its dims")
            marks_on_table = {t.get("mark") for t in p["table_footnotes"]}
            have = {cond.get("mark") for cond in c["conditions"] if cond.get("attached_to") == "table"}
            if marks_on_table - have:
                errs.append(f"{cw}: table footnote(s) {sorted(marks_on_table - have)} missing from conditions")
            for cond in c["conditions"]:
                if not p["conditions_loaded"] and cond.get("text") is not None:
                    errs.append(f"{cw}: condition {cond.get('mark')!r} has text but conditions_loaded is false")
                if p["conditions_loaded"] and not cond.get("text"):
                    errs.append(f"{cw}: conditions_loaded is true but condition {cond.get('mark')!r} has no text")
            if not c["keys"]:
                errs.append(f"{cw}: no lookup keys")
            for k in c["keys"]:
                if p["index"].get(k) != c["id"]:
                    errs.append(f"{cw}: key {k!r} is not indexed to this cell")
        for k, cid in p["index"].items():
            if cid not in cell_ids:
                errs.append(f"{where}.index[{k!r}]: points at missing cell {cid!r}")
            elif k not in cell_ids[cid]["keys"]:
                errs.append(f"{where}.index[{k!r}]: cell {cid!r} does not carry this key")
        if p["conditions_loaded"]:
            fns = (p.get("notes") or {}).get("footnotes", {})
            for c in p["cells"]:
                for cond in c.get("conditions", []):
                    fn = fns.get(cond.get("mark"))
                    if fn is None:
                        errs.append(f"{where}: condition {cond.get('mark')!r} has no footnote in the loaded notes")
                    elif cond.get("text") != fn.get("text"):
                        errs.append(f"{where}: condition {cond.get('mark')!r} text differs from its footnote")
            for mk, fn in fns.items():
                if fn.get("authority") != "code_text" or not isinstance((fn.get("source") or {}).get("line"), int):
                    errs.append(f"{where}: footnote {mk!r} needs code_text authority and a source line")
        for mark in p["table_footnotes"]:
            if not isinstance(mark.get("source"), dict):
                errs.append(f"{where}: table footnote {mark.get('mark')!r} has no source line")
    return errs
