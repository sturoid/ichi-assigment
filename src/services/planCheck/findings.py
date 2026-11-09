"""The finding model. The report, findings.json and the eval scorer all render from it."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

PASS, FAIL, CNE, NA = "Pass", "Fail", "Could Not Evaluate", "Not Applicable"
VERDICTS = (PASS, FAIL, CNE, NA)
_RANK = {FAIL: 3, CNE: 2, PASS: 1, NA: 0}


def worst(verdicts: list[str]) -> str:
    """Fail beats Could Not Evaluate beats Pass. Not Applicable only when nothing else."""
    vs = [v for v in verdicts if v in VERDICTS]
    if not vs:
        return CNE
    return max(vs, key=lambda v: _RANK[v])


@dataclass
class Criterion:
    requirement: str               # "Net clear opening >= 5.7 sq ft"
    code: str                      # "IBC 1030.2 (file line 35)"
    read: str                      # what was read / derived, with working
    verdict: str
    reason: str
    policies: list[str] = field(default_factory=list)
    settle: str = ""               # what document would settle a Could Not Evaluate
    brief: str = ""                # short plain statement for the report ("frame sill 50 in, above 44")
    flags: list[dict] = field(default_factory=list)   # raised onto the window finding


@dataclass
class Finding:
    id: str                        # stable: H-1, W-<mark>, R-<room key>
    check: str                     # height | egress_window | egress_room
    subject: str
    verdict: str
    summary: str                   # one line: why
    code_refs: list[str]
    evidence: list[dict]           # {"label", "value", "source"}
    criteria: list[Criterion] = field(default_factory=list)
    working: list[str] = field(default_factory=list)
    flags: list[dict] = field(default_factory=list)   # {"code", "message"}
    policies: list[str] = field(default_factory=list)
    interpretations: list[str] = field(default_factory=list)
    settle: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.verdict not in VERDICTS:
            raise ValueError(f"{self.id}: verdict {self.verdict!r} is not one of {VERDICTS}")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Attention:
    """Something the plan checker should look at that is not itself a verdict."""
    code: str
    title: str
    detail: str
    related: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
