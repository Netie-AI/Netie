"""Read one cell from a CSV or xlsx. Print a Number Trace block. No guessing."""

from __future__ import annotations

import csv
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def col_row(ref: str) -> tuple[int, int]:
    ref = ref.strip().upper().split("!")[-1]
    i = 0
    while i < len(ref) and ref[i].isalpha():
        i += 1
    if i == 0 or i == len(ref) or not ref[i:].isdigit():
        raise SystemExit("Use a cell like F14 or Sheet1!F14")
    col = 0
    for ch in ref[:i]:
        col = col * 26 + (ord(ch) - 64)
    return col, int(ref[i:])


def from_csv(path: Path, ref: str) -> tuple[str, str]:
    col, row = col_row(ref)
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if row < 1 or row > len(rows) or col < 1 or col > len(rows[row - 1]):
        return "", "cannot be traced"
    value = rows[row - 1][col - 1]
    if value == "":
        return "", "cannot be traced"
    return value, "typed, no formula"


def shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    out: list[str] = []
    for si in root.findall("m:si", NS):
        out.append("".join(t.text or "" for t in si.findall(".//m:t", NS)))
    return out


def from_xlsx(path: Path, ref: str) -> tuple[str, str]:
    raw = ref.strip()
    sheet_name = None
    cell = raw
    if "!" in raw:
        sheet_name, cell = raw.split("!", 1)
    cell = cell.upper()
    with zipfile.ZipFile(path) as zf:
        strings = shared_strings(zf)
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        sheets = wb.findall("m:sheets/m:sheet", NS)
        if not sheets:
            return "", "cannot be traced"
        target = sheets[0]
        if sheet_name:
            hit = [s for s in sheets if s.get("name") == sheet_name]
            if not hit:
                return "", "cannot be traced"
            target = hit[0]
        rid = target.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        target_path = None
        for rel in rels:
            if rel.get("Id") == rid:
                target_path = "xl/" + rel.get("Target").lstrip("/")
                if rel.get("Target", "").startswith("/"):
                    target_path = rel.get("Target").lstrip("/")
                elif rel.get("Target", "").startswith("worksheets"):
                    target_path = "xl/" + rel.get("Target")
                break
        if not target_path or target_path not in zf.namelist():
            # common path
            target_path = "xl/worksheets/sheet1.xml"
        if target_path not in zf.namelist():
            return "", "cannot be traced"
        root = ET.fromstring(zf.read(target_path))
        c = root.find(f".//m:c[@r='{cell}']", NS)
        if c is None:
            return "", "cannot be traced"
        formula_el = c.find("m:f", NS)
        formula = formula_el.text if formula_el is not None and formula_el.text else "typed, no formula"
        v = c.find("m:v", NS)
        if v is None or v.text is None:
            return "", "cannot be traced"
        value = v.text
        if c.get("t") == "s":
            try:
                value = strings[int(value)]
            except (ValueError, IndexError):
                return "", "cannot be traced"
        return value, formula


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python scripts/trace_number.py FILE CELL")
    path = Path(sys.argv[1])
    ref = sys.argv[2]
    if not path.is_file():
        raise SystemExit(f"Missing file: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        value, formula = from_csv(path, ref)
    elif suffix == ".xlsx":
        value, formula = from_xlsx(path, ref)
    else:
        raise SystemExit("File must be .csv or .xlsx")
    verdict = "Cannot be traced" if formula == "cannot be traced" or value == "" else "Traced"
    print("NETIE NUMBER TRACE")
    print(f"File name: {path.name}")
    print(f"Figure asked: {ref}")
    print(f"Value as shown in the file: {value or '(empty)'}")
    print(f"Formula (or typed, no formula): {formula}")
    print(f"Verdict: {verdict}")
    print("I only used the file you sent.")


if __name__ == "__main__":
    main()
