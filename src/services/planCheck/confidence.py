"""POL-GEN-CONFIDENCE: a confidence level on every finding, from what its verdict rests on.

Confidence answers one question: how likely is this verdict to survive a reviewer with the full
drawing set? It is a level, not a score, and it is decided by named reasons only:

- start at High;
- a Fail whose only failing grounds are derived values (a sill worked out from head height minus
  window height) drops one level: the arithmetic is sound, but it rests on how head height was
  measured;
- a Fail that a document we do not have could reverse (an exception the code allows, not ruled
  out) drops one level;
- a verdict that rests on a repaired OCR reading of a room name drops one level;
- a verdict decided by guessing a room's use (an office, den or unknown name read as not a
  sleeping room) is Low outright: if the guess is wrong, a required opening goes unchecked;
- a room's Fail also takes on each lowered level of the failing windows it rests on, since both
  must hold for the correction to stand.

Nothing here changes a verdict.
"""
from __future__ import annotations

from .findings import CNE, FAIL, Finding, NA, PASS

HIGH, MEDIUM, LOW = "High", "Medium", "Low"
_LEVELS = (LOW, MEDIUM, HIGH)

# a room-name repair decides which rule applies; a repaired number already turns a Fail into CNE (POL-GEN-OCR)
_REPAIRED = ("ocr_room_name",)
# flags meaning the room's use was guessed
_USE_GUESSED = ("ambiguous_room", "unrecognised_room")   # a window marked egress there is evaluated anyway


def _down(level: str, steps: int = 1) -> str:
    return _LEVELS[max(0, _LEVELS.index(level) - steps)]


def _own(f: Finding) -> tuple[str, list[str]]:
    level, reasons = HIGH, []
    if f.verdict == FAIL:
        fails = [c for c in f.criteria if c.verdict == FAIL]
        if fails and all(c.basis == "derived" for c in fails):
            level = _down(level)
            reasons.append("it rests only on a derived value (" + "; ".join(c.brief or c.read for c in fails)
                           + "); confirm on the elevations that head height is measured to the top of the window")
        for u in f.unresolved:
            level = _down(level)
            reasons.append(f"it could be reversed by {u}")
    for fl in f.flags:
        if fl["code"] in _REPAIRED:
            level = _down(level)
            reasons.append(f"it rests on a repaired room name: {fl['message']}")
    if f.verdict in (NA, CNE, PASS) and any(fl["code"] in _USE_GUESSED for fl in f.flags):
        level = LOW
        reasons.append("it rests on a guess at the room's use; if the room is used for sleeping, it needs an "
                       "escape opening")
    return level, list(dict.fromkeys(reasons))


def assign(height: Finding, rooms: list[Finding], windows: list[Finding]) -> None:
    """Fill confidence and confidence_reasons on every finding, in place."""
    for f in [height, *windows]:
        f.confidence, f.confidence_reasons = _own(f)
    by_id = {w.id: w for w in windows}
    for r in rooms:
        level, reasons = _own(r)
        if r.verdict == FAIL:
            for wid in r.related:
                w = by_id.get(wid)
                if w is not None and w.verdict == FAIL and _LEVELS.index(w.confidence) < _LEVELS.index(HIGH):
                    level = _down(level, _LEVELS.index(HIGH) - _LEVELS.index(w.confidence))
                    reasons += [f"{w.id}: {x}" for x in w.confidence_reasons]
        r.confidence, r.confidence_reasons = level, list(dict.fromkeys(reasons))
