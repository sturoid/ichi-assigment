"""Phase 2: load a code table's notes file (caption, legend, footnotes, shorthand).

The notes file is code text (the brief: "the code files are the source of truth").
Every item keeps its line number, and every reference it makes ("Section 903.2.8",
"Chapters 4 and 5", "the International Existing Building Code") is linked to a
manifest document id, so a check can say "IBC 903.2.8, not provided".

Nothing here interprets what a footnote *means* for a verdict; that is check policy.
"""
from __future__ import annotations

import re
from pathlib import Path

_FOOTNOTE = re.compile(r"^([a-z])\.\s+(.+)$")
_HEADING = re.compile(r"^#{2,}\s*(.+?)\s*$")
_LEGEND_ITEM = re.compile(r"^\s*([A-Z0-9]+)\s*=\s*(.+?)\s*$")
_SHORTHAND = re.compile(r"^-\s*Section\s+(\d+(?:\.\d+)+)\s+is\s+an?\s+(NFPA\s+\w+)\s+system\.?\s*$", re.I)


def extract_references(text: str) -> list[str]:
    """Normalised reference strings, in order of appearance, without duplicates.

    'IBC 903.2.8', 'IBC CH 4', 'IEBC', 'IFC 1103.5', 'NFPA 13D'.
    """
    found: list[tuple[int, str]] = []
    for m in re.finditer(r"\bChapters?\s+(\d+)((?:\s*(?:,|and)\s*\d+)*)", text):
        for n in re.findall(r"\d+", m.group(0)):
            found.append((m.start(), f"IBC CH {n}"))
    for m in re.finditer(r"\bSections?\s+(\d+(?:\.\d+)*)((?:\s*(?:,|and|or)\s*\d+(?:\.\d+)*)*)"
                         r"(\s+of\s+the\s+International\s+Fire\s+Code)?", text):
        book = "IFC" if m.group(3) else "IBC"
        for n in re.findall(r"\d+(?:\.\d+)*", m.group(1) + (m.group(2) or "")):
            found.append((m.start(), f"{book} {n}"))
    for m in re.finditer(r"International Existing Building Code", text):
        found.append((m.start(), "IEBC"))
    for m in re.finditer(r"\bNFPA\s+(13[RD]?)\b", text):
        found.append((m.start(), f"NFPA {m.group(1)}"))
    out: list[str] = []
    for _, ref in sorted(found, key=lambda x: x[0]):
        if ref not in out:
            out.append(ref)
    return out


def link_reference(ref: str, documents: list[dict]) -> dict:
    """Match a normalised reference to the manifest document whose ``covers`` pattern
    matches it most specifically (longest pattern). Unmatched references are kept
    and marked ``unlisted``: we don't know whether we have them."""
    best, best_len = None, -1
    for d in documents:
        for pat in d.get("covers", []):
            if re.search(pat, ref) and len(pat) > best_len:
                best, best_len = d, len(pat)
    if best is None:
        return {"ref": ref, "document": None, "status": "unlisted"}
    return {"ref": ref, "document": best["id"], "status": best["status"]}


def load_table_notes(path: Path, rel_path: str, documents: list[dict]) -> dict:
    """Parse the notes file into footnotes, legend and sprinkler shorthand, each with its line."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    section = None
    footnotes: dict[str, dict] = {}
    legend: dict[str, dict] = {}
    shorthand: list[dict] = []
    for n, raw in enumerate(lines, start=1):
        line = raw.strip()
        h = _HEADING.match(line)
        if h:
            section = h.group(1).lower()
            continue
        if not line:
            continue
        src = {"file": rel_path, "line": n}
        if section == "footnotes":
            m = _FOOTNOTE.match(line)
            if m:
                text = m.group(2)
                footnotes[m.group(1)] = {"mark": m.group(1), "text": text, "source": src, "authority": "code_text",
                                         "references": [link_reference(r, documents) for r in extract_references(text)]}
        elif section == "legend":
            for part in line.split(";"):
                m = _LEGEND_ITEM.match(part.strip().rstrip("."))
                if m:
                    text = m.group(2)
                    legend[m.group(1)] = {"token": m.group(1), "text": text, "source": src, "authority": "code_text",
                                          "references": [link_reference(r, documents)
                                                         for r in extract_references(text)]}
        elif section and section.startswith("sprinkler system shorthand"):
            m = _SHORTHAND.match(line)
            if m:
                std = " ".join(m.group(2).split()).upper()
                shorthand.append({"section": m.group(1), "standard": std, "source": src, "authority": "code_text",
                                  "supplementary": True,
                                  "references": [link_reference(f"IBC {m.group(1)}", documents),
                                                 link_reference(std, documents)]})
    return {"file": rel_path, "footnotes": footnotes, "legend": legend, "sprinkler_shorthand": shorthand}
