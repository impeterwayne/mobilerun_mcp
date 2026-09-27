"""Mobilerun Cloud MCP server (mobilerun-cloud-mcp)."""

from __future__ import annotations

from .server import build_cloud_server, run_server_cli


def main(argv: list[str] | None = None) -> None:
    run_server_cli(
        prog="mobilerun-cloud-mcp",
        server_factory=build_cloud_server,
        argv=argv,
        default_port=4818,
    )


if __name__ == "__main__":
    main()
