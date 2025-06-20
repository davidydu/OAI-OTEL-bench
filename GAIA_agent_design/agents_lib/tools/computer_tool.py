from __future__ import annotations

from agents import ComputerTool, LocalShellTool


def get_computer_tool() -> ComputerTool:
    """Return a basic ComputerTool for command execution."""
    return ComputerTool()


def get_local_shell_tool() -> LocalShellTool:
    """Return a LocalShellTool."""
    return LocalShellTool()
