"""Specs for known code tables. Each states the dimensions of one table once; the
parser verifies the HTML against it (stub count, unique keys, numeric values)."""
from __future__ import annotations

import re

from .matrix import MatrixSpec


def construction_type_key(path: list[str]) -> str:
    """['TYPE I', 'A'] -> 'I-A';  ['TYPE IV', 'HT'] -> 'IV-HT'."""
    parts = [re.sub(r"^TYPE\s+", "", p.strip(), flags=re.IGNORECASE) for p in path]
    return "-".join(p.upper() for p in parts if p)


IBC2018_TABLE_504_3 = MatrixSpec(
    table_id="IBC:2018:T504.3",
    short_name="Table 504.3",
    title="Allowable Building Height in Feet Above Grade Plane",
    unit="ft",
    row_dims=["occupancy", "sprinkler"],
    col_dim="construction",
    multi_value_dims={"occupancy"},
    column_key=construction_type_key,
    tokens={"UL": "unlimited"},
    # "(a)" on the printed title; the scrape dropped the title row
    table_footnotes=["a"],
    table_footnotes_source={"file": "code/table-504.3-notes.md", "line": 1},
)

SPECS: dict[str, MatrixSpec] = {
    "ibc2018-504.3": IBC2018_TABLE_504_3,
}
