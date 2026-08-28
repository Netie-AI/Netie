"""AirGPT RAG corpus. Not ChatGPT memory, not NVIDIA_RAG_EVAL."""

from __future__ import annotations

import netie._scripts  # noqa: F401

from airgpt_chunk import Chunk, ChunkDenied, MAX_RETRIEVE_CHARS, chunk_table, retrieve_space

__all__ = (
    "Chunk",
    "ChunkDenied",
    "MAX_RETRIEVE_CHARS",
    "chunk_table",
    "retrieve_space",
)
