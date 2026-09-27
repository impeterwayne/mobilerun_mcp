"""Parity with the upstream projects: any call valid for the mobilerun-core Device API
must be valid here.

Specs live in src/mobilerun_mcp/upstream/ (extracted from upstream sources).
"""

from __future__ import annotations

import asyncio
import json
from importlib import resources

import pytest
from fastmcp import Client

from mobilerun_mcp.config import Config
from mobilerun_mcp.server import build_server

TYPES = {
    "number": {"number", "integer"},
    "integer": {"integer", "number"},
    "string": {"string"},
    "boolean": {"boolean"},
    "array": {"array"},
    "object": {"object"},
}


def spec(name: str) -> dict:
    return json.loads((resources.files("mobilerun_mcp.upstream") / name).read_text())


async def _surface() -> tuple[dict[str, dict], set[str], set[str]]:
    cfg = Config(enable_adb=True, device="x:1")
    async with Client(build_server(cfg)) as client:
        tools = {
            t.name: (getattr(t, "input_schema", None) or t.inputSchema)
            for t in await client.list_tools()
        }
        uris = {str(r.uri) for r in await client.list_resources()}
        prompts = {p.name for p in await client.list_prompts()}
    return tools, uris, prompts


@pytest.fixture(scope="module")
def surface():
    return asyncio.run(_surface())


def test_every_mobilerun_core_device_method_is_a_tool(surface):
    tools, _, _ = surface
    api = spec("mobilerun_api.json")
    problems = []
    for method, params in api["device_api"].items():
        if method == "center_of":  # static geometry helper, not a device operation
            continue
        if method not in tools:
            problems.append(f"missing core method tool {method}")
            continue
        props = tools[method].get("properties", {})
        problems += [f"{method}: missing parameter {p!r}" for p in params if p not in props]
    assert not problems, "\n".join(problems)


def test_core_server_surface():
    cfg = Config(enable_adb=True)

    async def run():
        async with Client(build_server(cfg)) as client:
            return {t.name for t in await client.list_tools()}

    tools = asyncio.run(run())
    assert "ui" in tools and "tap" in tools and "adb" in tools
    assert "get_state" not in tools and "click" not in tools
    assert "create_device" not in tools and "manage_device" not in tools
    assert "run_task" not in tools
