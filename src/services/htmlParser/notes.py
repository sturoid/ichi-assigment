"""Coded parser warnings.

A ParserWarning is a str (so `"ragged" in w` keeps working) that also carries a
stable ``code``. Serialised output turns each one into {"code", "message"} so
scripts can count and filter warnings across many files. Warnings are internal:
they are for improving the parser, not for the plan-check report.
"""
from __future__ import annotations


class ParserWarning(str):
    code: str

    def __new__(cls, code: str, message: str) -> "ParserWarning":
        obj = super().__new__(cls, message)
        obj.code = code
        return obj

    def prefixed(self, prefix: str) -> "ParserWarning":
        return ParserWarning(self.code, prefix + str(self))


W = ParserWarning


def warning_dicts(warnings: list[str]) -> list[dict]:
    return [{"code": getattr(w, "code", "unclassified"), "message": str(w)} for w in warnings]
