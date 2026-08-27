"""AirGPT table-chunk corpus. Owned splitter, not ChatGPT, not LlamaIndex yet.

AirGPT rag/ingest.py is UNVERIFIABLE here. This is the corpus that HEAD must pass:
repeated headers are not extra rows, ragged rows do not invent cells, # labels
become metadata. Space isolation is still a dms/AirGPT caller problem.
"""

from __future__ import annotations

from dataclasses import dataclass


CORPUS_REPEATED_HEADER = """item,qty
a,1
item,qty
b,2
"""

CORPUS_RAGGED = """sku|qty|dest
A1|12|KL
B2|3
C3|9|JB|extra
"""

CORPUS_LABELED = """# warehouse: north
sku,qty
A,1
# warehouse: south
sku,qty
B,2
"""


@dataclass(frozen=True)
class Chunk:
    text: str
    header: str
    incomplete: bool
    labels: tuple[str, ...]


def _split_row(line: str, delim: str) -> list[str]:
    return [c.strip() for c in line.split(delim)]


def chunk_table(text: str) -> list[Chunk]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    delim = "|" if lines[0].count("|") >= lines[0].count(",") else ","
    header = ""
    labels: list[str] = []
    out: list[Chunk] = []
    for line in lines:
        if line.startswith("#"):
            labels = [line.lstrip("#").strip()]
            continue
        cells = _split_row(line, delim)
        if not header:
            header = delim.join(cells)
            continue
        if delim.join(cells) == header:
            continue
        expected = header.count(delim) + 1
        incomplete = len(cells) != expected
        body = delim.join(cells)
        out.append(
            Chunk(
                text=f"{header}\n{body}",
                header=header,
                incomplete=incomplete,
                labels=tuple(labels),
            )
        )
    return out
