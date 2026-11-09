"""Room names -> sleeping / ambiguous / not sleeping, and room identity.

The vocabulary is general (any project), not this fixture's rooms. An OCR-damaged
word within one edit of a sleeping word ("BEDROM") counts, and the match is
reported. A name the vocabulary doesn't know is *ambiguous*, never "not sleeping":
the brief says to say so rather than quietly guess.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

SLEEPING_WORDS = ("BEDROOM", "BED", "BDRM", "BEDRM", "BR", "SLEEPING", "BUNK", "NURSERY", "DORM", "DORMITORY")
SLEEPING_PHRASES = ("BED RM", "BED ROOM", "GUEST BED", "SLEEPING ROOM", "SLEEPING AREA")
AMBIGUOUS_WORDS = ("DEN", "OFFICE", "LOFT", "STUDY", "BONUS", "FLEX", "PLAYROOM", "LIBRARY", "GAME", "MEDIA",
                   "RECREATION", "REC", "SUNROOM", "ATTIC", "STUDIO", "GUEST")
NOT_SLEEPING_WORDS = ("LIVING", "KITCHEN", "LAUNDRY", "BATH", "BATHROOM", "TOILET", "WC", "POWDER", "HALL",
                      "HALLWAY", "CORRIDOR", "STAIR", "STAIRS", "STAIRWAY", "GARAGE", "DINING", "CLOSET", "CLO",
                      "WIC", "ENTRY", "FOYER", "MUDROOM", "MUD", "PANTRY", "UTILITY", "MECH", "MECHANICAL",
                      "STORAGE", "PORCH", "DECK", "VESTIBULE", "NOOK", "GREAT", "FAMILY", "LANDING")
# BR alone is too short for an edit-distance match; only these are checked for OCR near-misses
_NEAR_MATCH_TARGETS = ("BEDROOM", "SLEEPING")


def _edit_distance_le1(a: str, b: str) -> bool:
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diffs = [i for i in range(la) if a[i] != b[i]]
        if len(diffs) == 1:
            return True
        # one transposition of adjacent letters
        return len(diffs) == 2 and diffs[1] == diffs[0] + 1 and a[diffs[0]] == b[diffs[1]] and a[diffs[1]] == b[diffs[0]]
    if la > lb:
        a, b = b, a
    i = j = skipped = 0
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            if skipped:
                return False
            skipped = 1
            j += 1
        else:
            i += 1
            j += 1
    return True


@dataclass
class RoomClass:
    name: str
    kind: str                    # sleeping | ambiguous | not_sleeping
    basis: str                   # what matched
    flags: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "kind": self.kind, "basis": self.basis, "flags": self.flags}


def words(name: str) -> list[str]:
    return re.findall(r"[A-Z]+", (name or "").upper())


def classify(name: str) -> RoomClass:
    up = " ".join((name or "").upper().split())
    ws = words(up)
    for ph in SLEEPING_PHRASES:
        if re.search(rf"\b{re.escape(ph)}\b", up):
            return RoomClass(name, "sleeping", f"phrase {ph!r}")
    other = [w for w in ws if w in NOT_SLEEPING_WORDS]
    for w in ws:
        if w in SLEEPING_WORDS:
            if other:  # "BEDROOM BATH": the bath of a bedroom, or a bedroom? Say so rather than guess.
                return RoomClass(name, "ambiguous", f"word {w!r} with {other[0]!r}", [{
                    "code": "ambiguous_room",
                    "message": f"name {name!r} has a sleeping word ({w!r}) and a non-sleeping word ({other[0]!r}); "
                               "not treated as a sleeping room. Confirm the use on the floor plan."}])
            return RoomClass(name, "sleeping", f"word {w!r}")
    for w in ws:
        for target in _NEAR_MATCH_TARGETS:
            if len(w) >= 6 and _edit_distance_le1(w, target):
                return RoomClass(name, "sleeping", f"{w!r} read as {target!r}", [{
                    "code": "ocr_room_name",
                    "message": f"room name {w!r} is one character from {target!r}; read as a sleeping room "
                               "(likely OCR damage; confirm on the floor plan)"}])
    for w in ws:
        if w in AMBIGUOUS_WORDS:
            return RoomClass(name, "ambiguous", f"word {w!r}", [{
                "code": "ambiguous_room",
                "message": f"{w!r} rooms are sometimes used for sleeping; not treated as a sleeping room. "
                           "Confirm the use on the floor plan."}])
    for w in ws:
        if w in NOT_SLEEPING_WORDS:
            return RoomClass(name, "not_sleeping", f"word {w!r}")
    return RoomClass(name, "ambiguous", "name not recognised", [{
        "code": "unrecognised_room",
        "message": f"room name {name!r} is not recognised; its use (sleeping or not) is unknown"}])


def room_key(name: str) -> str:
    """Rooms are identified by their room number when the name has one ('BEDROM 12' and
    'BEDROOM 12' are one room); otherwise by the normalised name, with a word one
    character from a sleeping word spelled out ('BEDROM 2' = 'BEDROOM 2', but 'BED 2'
    and 'BATH 2' stay apart: single-digit numbers repeat across room types)."""
    up = " ".join((name or "").upper().split())
    m = re.findall(r"\b([A-Z]?\d{2,4}[A-Z]?)\b", up)
    if m:
        return m[-1]
    out = []
    for w in up.split():
        hit = next((t for t in _NEAR_MATCH_TARGETS if len(w) >= 6 and _edit_distance_le1(w, t)), None)
        out.append(hit or w)
    return " ".join(out)
