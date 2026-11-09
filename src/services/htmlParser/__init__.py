"""Reliable HTML table parsing for building-code tables and OCR'd project schedules.

Layers:
  grid.py     HTML -> resolved grid (rowspan/colspan, <sup> footnotes, line-break candidates)
  headers.py  title / header / separator / data rows, per-column header paths
  matrix.py   code tables -> keyed cell records + exact lookup
  records.py  project tables -> row records / key-value entries
"""
from .grid import Cell, Grid, Slot, parse_table, parse_tables
from .headers import Column, Layout, detect_layout
from .matrix import MatrixError, MatrixSpec, MatrixTable, render_sentence
from .notes import ParserWarning, warning_dicts
from .records import KeyValueSheet, RecordTable
from .specs import SPECS

SCHEMA_VERSION = "1.1"  # 1.1: coded warnings, conditions, table_index, no timestamps

__all__ = [
    "Cell", "Grid", "Slot", "parse_table", "parse_tables",
    "Column", "Layout", "detect_layout",
    "MatrixError", "MatrixSpec", "MatrixTable", "render_sentence", "ParserWarning", "warning_dicts",
    "KeyValueSheet", "RecordTable", "SPECS", "SCHEMA_VERSION",
]
