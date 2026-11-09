"""Feet-and-inches parsing for OCR'd drawings. Never repairs silently.

``parse_length("3' - O\"")`` returns inches=36 with an ``ocr_repair`` flag saying the
letter O was read as zero. The check decides what a repaired value may support.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction

# characters OCR commonly puts in place of digits, inside a number position only
_OCR_DIGITS = {"O": "0", "o": "0", "D": "0", "l": "1", "I": "1", "|": "1", "S": "5", "B": "8"}
_DIG = r"[0-9OoDlI|SB]"
_FT_IN = re.compile(
    rf"(?<![\d.])(?P<ft>{_DIG}+(?:\.\d+)?)\s*(?:'|’|′|FT\.?|FEET)\s*(?:-|–)?\s*"
    rf"(?:(?P<in>{_DIG}+(?:\.\d+)?)(?:\s+(?P<frac>\d+/\d+))?\s*(?:\"|”|″|''|IN\.?|INCHES)?)?",
    re.IGNORECASE)
_IN_ONLY = re.compile(rf"(?<![0-9'.])(?P<in>{_DIG}*\d{_DIG}*(?:\.\d+)?)(?:\s+(?P<frac>\d+/\d+))?\s*(?:\"|”|″|IN\.?\b|INCHES)",
                      re.IGNORECASE)


@dataclass
class Length:
    text: str
    status: str                 # parsed | unparsed | empty
    inches: float | None = None
    matched: str = ""
    flags: list[dict] = field(default_factory=list)  # ocr_repair, trailing_text ...

    @property
    def ocr_repaired(self) -> bool:
        return any(f["code"] == "ocr_repair" for f in self.flags)

    @property
    def feet(self) -> float | None:
        return None if self.inches is None else self.inches / 12

    def to_dict(self) -> dict:
        return {"text": self.text, "status": self.status, "inches": self.inches, "matched": self.matched,
                "flags": self.flags}


def _digits(tok: str, what: str, flags: list[dict]) -> float:
    if re.fullmatch(r"\d+\.\d+", tok):
        return float(tok)  # decimal feet or inches: 12.5'
    fixed = "".join(_OCR_DIGITS.get(ch, ch) for ch in tok)
    if fixed != tok:
        flags.append({"code": "ocr_repair", "message": f"{what} {tok!r} read as {fixed!r} "
                      "(a letter where a digit belongs; OCR damage)"})
    return int(fixed)


def parse_length(text: str | None) -> Length:
    t = (text or "").strip()
    if not t:
        return Length(text or "", "empty")
    flags: list[dict] = []
    m = next((x for x in _FT_IN.finditer(t)
              if any(ch.isdigit() for ch in x.group("ft") + (x.group("in") or ""))), None)
    if m:
        ft = _digits(m.group("ft"), "feet", flags)
        inch = _digits(m.group("in"), "inches", flags) if m.group("in") else 0
        frac = float(Fraction(m.group("frac"))) if m.group("frac") else 0.0
        if not m.group("in"):
            flags.append({"code": "no_inches", "message": "no inches given; read as 0"})
        total = ft * 12 + inch + frac
        if m.group("in") and inch >= 12:
            flags.append({"code": "inches_over_11", "message": f"inches part {inch} is 12 or more"})
        rest = (t[:m.start()] + t[m.end():]).strip()
        if rest:
            flags.append({"code": "trailing_text", "message": f"text besides the dimension: {rest!r}"})
        return Length(t, "parsed", total, m.group(0).strip(), flags)
    m = _IN_ONLY.search(t)
    if m:
        inch = _digits(m.group("in"), "inches", flags)
        frac = float(Fraction(m.group("frac"))) if m.group("frac") else 0.0
        rest = (t[:m.start()] + t[m.end():]).strip()
        if rest:
            flags.append({"code": "trailing_text", "message": f"text besides the dimension: {rest!r}"})
        return Length(t, "parsed", inch + frac, m.group(0).strip(), flags)
    return Length(t, "unparsed", flags=[{"code": "unparsed", "message": f"no feet-and-inches value in {t!r}"}])


def fmt_in(inches: float | None) -> str:
    """36 -> 3'-0\"; a 41 ft 6 in height is passed as 498 in -> 41'-6\"."""
    if inches is None:
        return "?"
    neg = inches < 0
    inches = abs(inches)
    ft, rem = divmod(round(inches * 8) / 8, 12)
    rem_s = f"{rem:g}"
    return f"{'-' if neg else ''}{int(ft)}'-{rem_s}\""
