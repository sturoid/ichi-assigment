"""Resolver: project wording -> Table 504.3 values, by cited rules (DESIGN.md format).

The store matches exactly ("R-3" is not "R"). This layer maps what the architect wrote
to a table value, and every mapping names the rule it used and what that rule cites.
A rule citing anything other than code text is an *interpretation* and is reported as
one. A rule without ``cites`` is refused at import time.

Results are never guesses: when no rule applies, or rules disagree, the result is
``unresolved`` with the reason, and the check says Could Not Evaluate.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

NOTES = "code/table-504.3-notes.md"
T504 = "IBC:2018:T504.3"

RULES: list[dict] = [
    # -- occupancy --------------------------------------------------------------
    {"id": "occupancy.exact", "dimension": "occupancy", "match": {"in_table": True}, "maps_to": "{value}",
     "authority": "code_text",
     "cites": {"document": T504, "file": "table-504.3.html", "what": "the table's printed row labels"}},
    {"id": "occupancy.numbered_group", "dimension": "occupancy",
     "match": {"regex": r"^([A-Z])-\d+$", "unless_in_table": True}, "maps_to": "{1}",
     "authority": "challenge_brief",
     "cites": {"document": "BRIEF", "file": "instructions/README.md", "lines": [54]},
     "unavailable": ["IBC:2018:310"],
     "note": "IBC 310 (occupancy classification) is not provided; the brief's rule places a numbered group "
             "in its letter's row unless the table gives the numbered group its own row (as for H and I)."},
    # -- construction type ------------------------------------------------------
    {"id": "construction.exact", "dimension": "construction", "match": {"in_table": True}, "maps_to": "{value}",
     "authority": "code_text",
     "cites": {"document": T504, "file": "table-504.3.html", "what": "column headers TYPE OF CONSTRUCTION / TYPE n / A|B|HT"}},
    {"id": "construction.normalise", "dimension": "construction",
     "match": {"regex": r"^(?:TYPE\s*)?(I{1,3}|IV|V)\s*[-–]?\s*(A|B|HT)$"}, "maps_to": "{1}-{2}",
     "authority": "code_text",
     "cites": {"document": T504, "file": "table-504.3.html",
               "what": "column headers TYPE OF CONSTRUCTION / TYPE n / A|B|HT (the column key is 'n-A')"}},
    # -- sprinklers (legend line 15; shorthand lines 37-39) ---------------------
    {"id": "sprinkler.partial", "dimension": "sprinkler",
     "match": {"contains_any": ["PARTIAL", "PARTIALLY", "EXCEPT", "ONLY", "PORTION", "PORTIONS"]},
     "maps_to": None, "authority": "code_text",
     "cites": {"document": T504, "file": NOTES, "lines": [15]},
     "note": "the legend's S, S13R and S13D all require a building 'equipped throughout'; partial coverage "
             "does not resolve to any sprinklered sub-row"},
    {"id": "sprinkler.nfpa13d", "dimension": "sprinkler", "match": {"contains_any": ["NFPA 13D", "903.3.1.3"]},
     "maps_to": "S13D", "authority": "code_text", "cites": {"document": T504, "file": NOTES, "lines": [15, 39]}},
    {"id": "sprinkler.nfpa13r", "dimension": "sprinkler", "match": {"contains_any": ["NFPA 13R", "903.3.1.2"]},
     "maps_to": "S13R", "authority": "code_text", "cites": {"document": T504, "file": NOTES, "lines": [15, 38]}},
    {"id": "sprinkler.nfpa13", "dimension": "sprinkler", "match": {"contains_any": ["NFPA 13", "903.3.1.1"]},
     "maps_to": "S", "authority": "code_text", "cites": {"document": T504, "file": NOTES, "lines": [15, 37]}},
    {"id": "sprinkler.none", "dimension": "sprinkler",
     "match": {"contains_any": ["NONE", "NOT SPRINKLERED", "NON-SPRINKLERED", "NONSPRINKLERED", "UNSPRINKLERED",
                                "NO SPRINKLERS", "NO SPRINKLER", "NOT REQUIRED"], "or_exact": ["NO", "N", "NS"]},
     "maps_to": "NS", "authority": "code_text", "cites": {"document": T504, "file": NOTES, "lines": [15]}},
]

for _r in RULES:
    if not _r.get("cites"):
        raise ValueError(f"resolver rule {_r['id']} has no cites; every rule must cite its source")


def norm(text: str) -> str:
    return " ".join((text or "").upper().replace("–", "-").split())


def _contains(text: str, phrase: str) -> bool:
    """Word-boundary containment: 'NFPA 13' does not match inside 'NFPA 13D'."""
    return re.search(r"(?<![A-Z0-9.])" + re.escape(phrase) + r"(?![A-Z0-9]|\.\d)", text) is not None


@dataclass
class Resolution:
    dimension: str
    input: str
    status: str                      # resolved | unresolved
    value: str | None = None
    rules: list[dict] = field(default_factory=list)   # the rules that fired (copies)
    reason: str = ""

    @property
    def interpretations(self) -> list[dict]:
        return [r for r in self.rules if r["authority"] != "code_text"]

    def to_dict(self) -> dict:
        return {"dimension": self.dimension, "input": self.input, "status": self.status, "value": self.value,
                "rules": [{k: r[k] for k in ("id", "authority", "cites", "note") if k in r} for r in self.rules],
                "interpretations": [r["id"] for r in self.interpretations], "reason": self.reason}


def _apply(rule: dict, text: str, allowed: set[str]) -> str | None | bool:
    """The value a rule maps to, None if it doesn't match, or False for a matching guard rule."""
    m = rule["match"]
    if m.get("in_table"):
        return text if text in allowed else None
    if "regex" in m:
        if m.get("unless_in_table") and text in allowed:
            return None
        mm = re.match(m["regex"], text)
        if not mm:
            return None
        out = rule["maps_to"]
        for i, g in enumerate(mm.groups(), start=1):
            out = out.replace("{%d}" % i, g)
        return out
    if "contains_any" in m:
        hit = any(_contains(text, p) for p in m["contains_any"]) or text in m.get("or_exact", [])
        if not hit:
            return None
        return False if rule["maps_to"] is None else rule["maps_to"]
    return None


def resolve(dimension: str, text: str | None, allowed: list[str]) -> Resolution:
    """Map project wording for one Table 504.3 dimension to a table value."""
    raw = text or ""
    t = norm(raw)
    allowed_n = {norm(a): a for a in allowed}
    if not t:
        return Resolution(dimension, raw, "unresolved", reason="no value given")
    if dimension == "occupancy" and t not in allowed_n:
        # one occupancy group token, ignoring a trailing description: "R-3 (SINGLE FAMILY)"
        groups = re.findall(r"\b([ABEFHIMRSU](?:-\d+)?)\b", re.sub(r"\(.*?\)", "", t))
        groups = list(dict.fromkeys(g for g in groups if g != "A" or t.startswith("A")))
        if len(groups) > 1:
            return Resolution(dimension, raw, "unresolved",
                              reason=f"several occupancy groups ({', '.join(groups)}); each needs its own check")
        if groups:
            t = groups[0]
    if dimension == "construction":
        t = re.sub(r"\(.*?\)", "", t).strip()
    hits: list[tuple[dict, str | bool]] = []
    for rule in (r for r in RULES if r["dimension"] == dimension):
        v = _apply(rule, t, set(allowed_n))
        if v is None:
            continue
        hits.append((rule, v))
        if rule["match"].get("in_table") or "regex" in rule["match"]:
            break  # an exact or normalising rule is final for this dimension
    guards = [r for r, v in hits if v is False]
    if guards:
        return Resolution(dimension, raw, "unresolved", rules=[dict(r) for r in guards], reason=guards[0]["note"])
    values = list(dict.fromkeys(v for _, v in hits))
    fired = [dict(r) for r, _ in hits]
    if not values:
        why = {"sprinkler": "the sprinkler standard is not stated (S, S13R and S13D give different limits)"
               if any(_contains(t, w) for w in ("YES", "SPRINKLERED", "SPRINKLER", "AUTOMATIC")) else
               "no rule recognises this wording"}.get(dimension, "no rule recognises this wording")
        return Resolution(dimension, raw, "unresolved", reason=why)
    if len(values) > 1:
        return Resolution(dimension, raw, "unresolved", rules=fired,
                          reason=f"rules disagree: {', '.join(values)} ({', '.join(r['id'] for r in fired)})")
    value = allowed_n.get(norm(values[0]))
    if value is None:
        return Resolution(dimension, raw, "unresolved", rules=fired,
                          reason=f"{values[0]!r} is not a {dimension} in Table 504.3")
    return Resolution(dimension, raw, "resolved", value=value, rules=fired)
