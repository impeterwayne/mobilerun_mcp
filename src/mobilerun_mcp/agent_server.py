"""Mobilerun Agent MCP server (mobilerun-agent-mcp)."""

from __future__ import annotations

from .server import build_agent_server, run_server_cli


def main(argv: list[str] | None = None) -> None:
    run_server_cli(
        prog="mobilerun-agent-mcp",
        server_factory=build_agent_server,
        argv=argv,
        default_port=4817,
    )


if __name__ == "__main__":
    main()
