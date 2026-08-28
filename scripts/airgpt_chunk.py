"""AirGPT table-chunk corpus. Owned splitter, not ChatGPT, not LlamaIndex yet.

AirGPT rag/ingest.py is UNVERIFIABLE here. This is the corpus that HEAD must pass:
repeated headers are not extra rows, ragged rows do not invent cells, # labels
become metadata. retrieve_space cites only complete chunks labeled for that
Space. Unlabeled and incomplete rows are not evidence.
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
        too_long = len(cells) > expected
        too_short = len(cells) < expected
        if too_long:
            cells = cells[:expected]
        incomplete = too_long or too_short
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


def _space_of(chunk: Chunk) -> str:
    for lab in chunk.labels:
        if ":" in lab:
            return lab.split(":", 1)[1].strip()
        if lab.strip():
            return lab.strip()
    return ""


def retrieve_space(chunks: list[Chunk], *, space: str, query: str) -> dict:
    """Cite only complete chunks labeled for this Space. No cross-space leak.

    Unlabeled and incomplete rows are not evidence. Empty query abstains.
    """
    want = (space or "").strip()
    needle = (query or "").strip().lower()
    if not want:
        return {"status": "ABSTAIN", "reason": "no space", "chunks": []}
    if not needle:
        return {"status": "ABSTAIN", "reason": "no query", "chunks": []}
    hits: list[Chunk] = []
    for chunk in chunks:
        if chunk.incomplete:
            continue
        if _space_of(chunk) != want:
            continue
        if needle not in chunk.text.lower():
            continue
        hits.append(chunk)
    if not hits:
        return {
            "status": "ABSTAIN",
            "reason": f"space {want} has no cite for {query.strip()}",
            "chunks": [],
        }
    return {"status": "OK", "space": want, "chunks": list(hits)}
