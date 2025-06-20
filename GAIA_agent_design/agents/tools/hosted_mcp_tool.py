from __future__ import annotations

from agents import HostedMCPTool


def get_hosted_mcp_tool(server_url: str) -> HostedMCPTool:
    """Return a HostedMCPTool configured with the given server URL."""
    return HostedMCPTool(server_url=server_url)
