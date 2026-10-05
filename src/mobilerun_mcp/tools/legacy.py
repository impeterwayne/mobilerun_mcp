"""Tools kept from the first version of this server."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from fastmcp import FastMCP

from ..errors import fail
from ..observe import mutate
from ..session import Runtime
from .common import Device, get_session

KEYS = ("home", "back", "enter")
GOAL = re.compile(r"(Goal (?:achieved|failed): .*)")


def _mobilerun_cmd(configured: str | None) -> list[str]:
    """Resolve the command to invoke mobilerun CLI.

    Checks:
    1. Configured path.
    2. System PATH.
    3. Python virtualenv bin/scripts directory.
    4. ~/.local/bin/mobilerun.
    5. Fallback: sys.executable -m mobilerun (bundled module).
    """
    if configured:
        return [configured]
    which = shutil.which("mobilerun")
    if which:
        return [which]
    venv_bin = Path(sys.executable).parent / ("mobilerun.exe" if sys.platform == "win32" else "mobilerun")
    if venv_bin.is_file():
        return [str(venv_bin)]
    local_bin = Path.home() / ".local/bin/mobilerun"
    if local_bin.is_file():
        return [str(local_bin)]
    return [sys.executable, "-m", "mobilerun"]


def _mobilerun_bin(configured: str | None) -> str:
    cmd = _mobilerun_cmd(configured)
    return cmd[0]


def register(mcp: FastMCP, rt: Runtime) -> None:
    @mcp.tool(tags={"write"})
    async def press(button: str, device: Device = None) -> dict:
        """Press home, back or enter (kept for old clients; prefer press_home/back/enter)."""
        if button not in KEYS:
            fail("invalid_argument", "button must be home, back or enter")
        session = get_session(rt, device)
        return await mutate(session, lambda: session.press(button), {"action": f"press_{button}"})
