"""Trace a simple source formula in a local CSV or xlsx file.

The tool deliberately supports a narrow formula shape: a single-sheet SUM(range).
It reports a clean refusal for anything it cannot verify instead of guessing.
"""

from __future__ import annotations

import csv
import json
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"m": MAIN_NS}
CELL_REF_RE = re.compile(r"^\$?([A-Za-z]{1,3})\$?([1-9][0-9]*)$")
CELL_TOKEN_RE = re.compile(r"(?P<col_abs>\$?)(?P<col>[A-Z]{1,3})(?P<row_abs>\$?)(?P<row>[1-9][0-9]*)")
SUM_RANGE_RE = re.compile(
    r"^SUM\(\s*(?:(?P<sheet>'(?:[^']|'')+'|[^!]+)!)?"
    r"(?P<start>\$?[A-Za-z]{1,3}\$?[1-9][0-9]*):"
    r"(?P<end>\$?[A-Za-z]{1,3}\$?[1-9][0-9]*)\s*\)$",
    re.IGNORECASE,
)
MAX_WORKBOOK_BYTES = 20 * 1024 * 1024
MAX_MEMBER_BYTES = 10 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200


class TraceError(Exception):
    """A safe, user-facing input or parser failure."""


class UsageError(Exception):
    """A command-line or reference syntax error."""


@dataclass(frozen=True)
class SpreadsheetCell:
    coordinate: str
    value: str | None
    numeric_value: Decimal | None
    formula: str | None


@dataclass(frozen=True)
class TraceInput:
    cell: str
    value: str


@dataclass(frozen=True)
class TraceResult:
    file_name: str
    sheet: str
    figure_asked: str
    value_raw: str
    formula: str
    inputs: list[TraceInput]
    recomputed_from_inputs: str
    verdict: str
    reason: str | None


def normalize_cell_reference(reference: str) -> str:
    match = CELL_REF_RE.fullmatch(reference.strip())
    if not match:
        raise UsageError("Use a cell like F14 or Sheet1!F14")
    return f"{match.group(1).upper()}{match.group(2)}"


def split_reference(reference: str) -> tuple[str | None, str]:
    raw = reference.strip()
    if not raw:
        raise UsageError("Use a cell like F14 or Sheet1!F14")
    if "!" not in raw:
        return None, normalize_cell_reference(raw)
    sheet_name, cell = raw.rsplit("!", 1)
    sheet_name = unquote_sheet_name(sheet_name)
    if not sheet_name:
        raise UsageError("Use a sheet name before !")
    return sheet_name, normalize_cell_reference(cell)


def unquote_sheet_name(name: str) -> str:
    value = name.strip()
    if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def col_row(reference: str) -> tuple[int, int]:
    normalized = normalize_cell_reference(reference)
    match = CELL_REF_RE.fullmatch(normalized)
    assert match is not None
    column = 0
    for char in match.group(1).upper():
        column = column * 26 + (ord(char) - ord("A") + 1)
    return column, int(match.group(2))


def col_name(column: int) -> str:
    out = ""
    while column:
        column, remainder = divmod(column - 1, 26)
        out = chr(ord("A") + remainder) + out
    return out


def cell_name(column: int, row: int) -> str:
    return f"{col_name(column)}{row}"


def decimal_from(value: str | None) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def compact_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def parse_xml(data: bytes, member_name: str) -> ET.Element:
    if b"<!DOCTYPE" in data.upper():
        raise TraceError(f"Workbook XML with a DTD is not supported: {member_name}")
    try:
        return ET.fromstring(data)
    except ET.ParseError as error:
        raise TraceError(f"Invalid workbook XML: {member_name}") from error


def validate_zip(zf: zipfile.ZipFile) -> None:
    total_size = 0
    for info in zf.infolist():
        total_size += info.file_size
        if info.file_size > MAX_MEMBER_BYTES:
            raise TraceError("Workbook contains a member that is too large to inspect safely")
        if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
            raise TraceError("Workbook compression ratio is too high to inspect safely")
    if total_size > MAX_WORKBOOK_BYTES:
        raise TraceError("Workbook is too large to inspect safely")


def read_member(zf: zipfile.ZipFile, member_name: str) -> bytes:
    try:
        return zf.read(member_name)
    except KeyError as error:
        raise TraceError(f"Workbook is missing {member_name}") from error


def shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = parse_xml(read_member(zf, "xl/sharedStrings.xml"), "xl/sharedStrings.xml")
    return ["".join(item.text or "" for item in si.findall(".//m:t", NS)) for si in root.findall("m:si", NS)]


def workbook_sheets(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = parse_xml(read_member(zf, "xl/workbook.xml"), "xl/workbook.xml")
    relationships = parse_xml(
        read_member(zf, "xl/_rels/workbook.xml.rels"),
        "xl/_rels/workbook.xml.rels",
    )
    relation_targets = {
        relationship.get("Id"): relationship.get("Target")
        for relationship in relationships
        if relationship.get("Id") and relationship.get("Target")
    }
    sheets: list[tuple[str, str]] = []
    for sheet in workbook.findall("m:sheets/m:sheet", NS):
        name = sheet.get("name")
        relation_id = sheet.get(f"{{{REL_NS}}}id")
        target = relation_targets.get(relation_id)
        if not name or not target:
            continue
        member_name = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
        if not member_name.startswith("xl/") or member_name not in zf.namelist():
            continue
        sheets.append((name, member_name))
    if not sheets:
        raise TraceError("Workbook has no readable worksheets")
    return sheets


def choose_sheet(sheets: list[tuple[str, str]], requested_name: str | None) -> tuple[str, str]:
    if requested_name is None:
        return sheets[0]
    matches = [(name, path) for name, path in sheets if name.casefold() == requested_name.casefold()]
    if not matches:
        raise TraceError(f"Sheet not found: {requested_name}")
    return matches[0]


def translate_formula(formula: str, source_cell: str, destination_cell: str) -> str:
    source_col, source_row = col_row(source_cell)
    destination_col, destination_row = col_row(destination_cell)
    col_delta = destination_col - source_col
    row_delta = destination_row - source_row

    def replace(match: re.Match[str]) -> str:
        column, row = col_row(f"{match.group('col')}{match.group('row')}")
        if not match.group("col_abs"):
            column += col_delta
        if not match.group("row_abs"):
            row += row_delta
        if column < 1 or row < 1:
            raise TraceError("Shared formula points outside the worksheet")
        return (
            f"{match.group('col_abs')}{col_name(column)}"
            f"{match.group('row_abs')}{row}"
        )

    return CELL_TOKEN_RE.sub(replace, formula)


def formula_for_cell(
    element: ET.Element,
    coordinate: str,
    shared_formula_masters: dict[str, tuple[str, str]],
) -> str | None:
    formula_element = element.find("m:f", NS)
    if formula_element is None:
        return None
    formula_text = (formula_element.text or "").strip()
    if formula_element.get("t") == "shared":
        shared_index = formula_element.get("si")
        if formula_text and shared_index:
            shared_formula_masters[shared_index] = (coordinate, formula_text)
        elif not formula_text and shared_index in shared_formula_masters:
            source_coordinate, source_formula = shared_formula_masters[shared_index]
            formula_text = translate_formula(source_formula, source_coordinate, coordinate)
        elif not formula_text:
            return None
    if not formula_text:
        return None
    return "=" + formula_text.lstrip("=")


def value_for_cell(element: ET.Element, strings: list[str]) -> tuple[str | None, Decimal | None]:
    cell_type = element.get("t")
    if cell_type == "inlineStr":
        inline_text = "".join(item.text or "" for item in element.findall(".//m:is//m:t", NS))
        return inline_text or None, None
    value_element = element.find("m:v", NS)
    raw_value = value_element.text if value_element is not None else None
    if raw_value is None:
        return None, None
    if cell_type == "s":
        try:
            return strings[int(raw_value)], None
        except (IndexError, ValueError) as error:
            raise TraceError("Workbook has an invalid shared-string index") from error
    if cell_type == "b":
        return ("TRUE" if raw_value == "1" else "FALSE"), None
    return raw_value, decimal_from(raw_value)


def worksheet_cells(zf: zipfile.ZipFile, member_name: str, strings: list[str]) -> dict[str, SpreadsheetCell]:
    root = parse_xml(read_member(zf, member_name), member_name)
    raw_cells = root.findall(".//m:c", NS)
    shared_formula_masters: dict[str, tuple[str, str]] = {}
    for element in raw_cells:
        coordinate = element.get("r")
        formula_element = element.find("m:f", NS)
        if (
            coordinate
            and formula_element is not None
            and formula_element.get("t") == "shared"
            and (formula_element.text or "").strip()
            and formula_element.get("si")
        ):
            shared_formula_masters[formula_element.get("si") or ""] = (
                normalize_cell_reference(coordinate),
                (formula_element.text or "").strip(),
            )
    cells: dict[str, SpreadsheetCell] = {}
    for element in raw_cells:
        coordinate = element.get("r")
        if not coordinate:
            continue
        normalized = normalize_cell_reference(coordinate)
        value, numeric_value = value_for_cell(element, strings)
        formula = formula_for_cell(element, normalized, shared_formula_masters)
        cells[normalized] = SpreadsheetCell(
            coordinate=normalized,
            value=value,
            numeric_value=numeric_value,
            formula=formula,
        )
    return cells


def sum_range_inputs(
    formula: str,
    sheet_name: str,
    cells: dict[str, SpreadsheetCell],
) -> tuple[list[TraceInput] | None, Decimal | None, str | None]:
    match = SUM_RANGE_RE.fullmatch(formula.lstrip("="))
    if not match:
        return None, None, "Formula shape is not supported for input resolution."
    formula_sheet = match.group("sheet")
    if formula_sheet and unquote_sheet_name(formula_sheet).casefold() != sheet_name.casefold():
        return None, None, "Formula uses another sheet, which this sample does not resolve."
    start_col, start_row = col_row(match.group("start"))
    end_col, end_row = col_row(match.group("end"))
    if start_col > end_col or start_row > end_row:
        return None, None, "Formula range is reversed."
    inputs: list[TraceInput] = []
    total = Decimal("0")
    for row in range(start_row, end_row + 1):
        for column in range(start_col, end_col + 1):
            coordinate = cell_name(column, row)
            source = cells.get(coordinate)
            if source is None or source.value is None or source.numeric_value is None:
                return None, None, f"Input {sheet_name}!{coordinate} is not a numeric cell."
            inputs.append(TraceInput(cell=f"{sheet_name}!{coordinate}", value=source.value))
            total += source.numeric_value
    return inputs, total, None


def cannot_trace(
    path: Path,
    requested_reference: str,
    sheet_name: str,
    coordinate: str,
    cell: SpreadsheetCell | None,
    reason: str,
) -> TraceResult:
    return TraceResult(
        file_name=path.name,
        sheet=sheet_name,
        figure_asked=requested_reference,
        value_raw=cell.value if cell and cell.value is not None else "(empty)",
        formula=cell.formula if cell and cell.formula else "typed, no formula",
        inputs=[],
        recomputed_from_inputs="not applicable",
        verdict="Cannot be traced",
        reason=reason,
    )


def trace_xlsx(path: Path, requested_reference: str, requested_sheet: str | None, coordinate: str) -> TraceResult:
    try:
        with zipfile.ZipFile(path) as zf:
            validate_zip(zf)
            strings = shared_strings(zf)
            sheet_name, member_name = choose_sheet(workbook_sheets(zf), requested_sheet)
            cells = worksheet_cells(zf, member_name, strings)
    except zipfile.BadZipFile as error:
        raise TraceError("File has a .xlsx suffix but is not a readable xlsx workbook") from error

    cell = cells.get(coordinate)
    if cell is None:
        return cannot_trace(path, requested_reference, sheet_name, coordinate, None, "Cell is empty or does not exist.")
    if cell.value is None:
        return cannot_trace(path, requested_reference, sheet_name, coordinate, cell, "Cell has no cached value to verify.")
    if cell.formula is None:
        return cannot_trace(path, requested_reference, sheet_name, coordinate, cell, "Selected cell has no formula.")
    if cell.numeric_value is None:
        return cannot_trace(path, requested_reference, sheet_name, coordinate, cell, "Formula result is not numeric.")

    inputs, recomputed, reason = sum_range_inputs(cell.formula, sheet_name, cells)
    if inputs is None or recomputed is None:
        return cannot_trace(path, requested_reference, sheet_name, coordinate, cell, reason or "Formula cannot be traced.")
    if recomputed != cell.numeric_value:
        return cannot_trace(
            path,
            requested_reference,
            sheet_name,
            coordinate,
            cell,
            f"Cached value disagrees with recomputed value ({compact_decimal(recomputed)}).",
        )
    return TraceResult(
        file_name=path.name,
        sheet=sheet_name,
        figure_asked=requested_reference,
        value_raw=cell.value,
        formula=cell.formula,
        inputs=inputs,
        recomputed_from_inputs=f"{compact_decimal(recomputed)} (matches cached value)",
        verdict="Traced",
        reason=None,
    )


def trace_csv(path: Path, requested_reference: str, requested_sheet: str | None, coordinate: str) -> TraceResult:
    if requested_sheet is not None:
        raise TraceError("CSV files do not have sheets; use a cell like F14")
    column, row = col_row(coordinate)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    value = ""
    if 1 <= row <= len(rows) and 1 <= column <= len(rows[row - 1]):
        value = rows[row - 1][column - 1]
    cell = SpreadsheetCell(coordinate=coordinate, value=value or None, numeric_value=decimal_from(value), formula=None)
    if not value:
        return cannot_trace(path, requested_reference, "CSV", coordinate, cell, "Cell is empty or does not exist.")
    return cannot_trace(path, requested_reference, "CSV", coordinate, cell, "CSV cells do not contain formulas.")


def trace(path: Path, requested_reference: str) -> TraceResult:
    requested_sheet, coordinate = split_reference(requested_reference)
    if not path.is_file():
        raise TraceError(f"Missing file: {path}")
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return trace_xlsx(path, requested_reference, requested_sheet, coordinate)
    if suffix == ".csv":
        return trace_csv(path, requested_reference, requested_sheet, coordinate)
    raise UsageError("File must be .csv or .xlsx")


def print_human(result: TraceResult) -> None:
    print("NETIE SOURCE TRACE")
    print(f"File name: {result.file_name}")
    print(f"Sheet: {result.sheet}")
    print(f"Figure asked: {result.figure_asked}")
    print(f"Value (raw; display format not applied): {result.value_raw}")
    print(f"Formula: {result.formula}")
    print("Inputs:")
    if result.inputs:
        for source in result.inputs:
            print(f"- {source.cell} = {source.value}")
    else:
        print("- not available")
    print(f"Recomputed from inputs: {result.recomputed_from_inputs}")
    print(f"Verdict: {result.verdict}")
    if result.reason:
        print(f"Reason: {result.reason}")
    print("I only used the local file you selected.")


def parse_arguments(arguments: list[str]) -> tuple[Path, str, bool]:
    json_output = False
    if "--json" in arguments:
        arguments = list(arguments)
        arguments.remove("--json")
        json_output = True
    if len(arguments) != 2:
        raise UsageError("Usage: python scripts/trace_number.py FILE CELL [--json]")
    return Path(arguments[0]), arguments[1], json_output


def main(arguments: list[str] | None = None) -> int:
    try:
        path, requested_reference, json_output = parse_arguments(list(sys.argv[1:] if arguments is None else arguments))
        result = trace(path, requested_reference)
    except UsageError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 64
    except (OSError, TraceError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 65
    if json_output:
        print(json.dumps(asdict(result), default=str, indent=2))
    else:
        print_human(result)
    return 0 if result.verdict == "Traced" else 2


if __name__ == "__main__":
    raise SystemExit(main())
