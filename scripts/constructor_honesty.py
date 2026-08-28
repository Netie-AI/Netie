"""xyflow is an editor. Constructor compiles Cortex IR.

Do not replace compileIR with @xyflow/react. npm i @xyflow/react only if
the canvas must feel like React Flow. Score stays 2/10 editor, 4/10
compiler. This module is the gate, not the canvas.
"""

from __future__ import annotations

EDITORS = frozenset(
    {
        "xyflow",
        "@xyflow/react",
        "react-flow",
        "reactflow",
        "react_flow",
    }
)
COMPILERS = frozenset({"compileir", "constructor", "engine.js", "engine"})


class CompileDenied(PermissionError):
    """Editor is not the Cortex IR compiler."""


def compile_graph(*, engine: str) -> dict[str, str]:
    name = (engine or "").strip().lower()
    if name in EDITORS or "xyflow" in name or "react-flow" in name:
        raise CompileDenied("xyflow is the editor; Cortex IR is the compiler")
    if name not in COMPILERS:
        raise CompileDenied(f"unknown compiler {engine or 'none'}")
    return {
        "engine": "compileIR",
        "score_editor": "2/10",
        "score_compiler": "4/10",
    }
