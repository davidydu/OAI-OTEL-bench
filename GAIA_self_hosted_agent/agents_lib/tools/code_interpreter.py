from __future__ import annotations

from agents import CodeInterpreterTool

_DEFAULT_CONFIG = {
    "type": "code_interpreter",
    "container": {"type": "auto"},
}

def get_code_interpreter_tool() -> CodeInterpreterTool:
    """Return the CodeInterpreterTool."""
    return CodeInterpreterTool(tool_config=_DEFAULT_CONFIG)
