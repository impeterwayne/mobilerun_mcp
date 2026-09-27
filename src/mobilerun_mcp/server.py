"""FastMCP server assembly."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from . import guide as guide_mod
from .config import Config
from .marks import format_marks
from .session import Runtime
from .tools import (
    adbtool,
    apps,
    core,
    device,
    files,
    legacy,
    media,
    notifications,
    perception,
    plan,
    waiting,
)
from .tools import input as input_tools
from .tools import intents as intent_tools

CORE_MODULES = (
    perception,
    input_tools,
    apps,
    device,
    legacy,
    notifications,
    media,
    files,
    intent_tools,
    waiting,
    plan,
    core,
)

CORE_INSTRUCTIONS = """\
You control a phone (Android over adb, iOS, or Portal HTTP) through numbered marks
and typed actions.

Loop: read_screen or perceive_screen -> act -> read the post_action_observation -> repeat.
- read_screen draws the screen as a text grid; perceive_screen returns numbered marks (som_id) and
  an annotated screenshot (detail="full" adds icon detection for unlabelled icons). ids describe ONE
  captured screen; every gesture, launch, scroll or key press makes them stale (stale_som_id).
  Perceive again before tapping something new.
- Every state-changing tool settles first, then returns post_action_observation (foreground app,
  element count, keyboard, top labels, screen_changed). Read it instead of re-perceiving.
- The screen is ground truth. Never tap coordinates from memory.

Prefer typed tools over tapping through apps: system_intent (alarm, timer, dial, sms, calendar,
share, navigate), read_notifications / notification_action, media_control, open_deeplink,
launch_app by name.

Core device API: use mobilerun-core Device tools (ui, find_nodes, tap_text, wait_for_app,
get_clipboard, execute_script, etc.) for direct, structured device interaction.

Text entry: focus the field first (tap or som_id), type_text, and confirm the value read back.
Search bars submit with press_enter.

When something fails, change strategy: re-perceive, scroll, press_back and try another path,
then ask the user. A policy_blocked error is a decision, never an obstacle to route around.
Use set_plan / mark_step / record_finding for multi-step goals and end_session honestly.
"""

INSTRUCTIONS = CORE_INSTRUCTIONS

POLICY_TEXT = """\
Safety policy modes (MOBILERUN_MCP_POLICY): off (default) | standard | strict.
standard blocks banking/payment/wallet, authenticator and password-manager apps, payment card
numbers and card security codes. strict also refuses password/PIN fields and national-id numbers.
Blocked actions fail with [policy_blocked]; that is a decision, not an obstacle. The adb tool is
disabled while a policy is on because it cannot be policed.
"""


def register_resources(mcp: FastMCP, runtime: Runtime) -> None:
    @mcp.resource("mobilerun://guide")
    def guide_resource() -> str:
        """Usage guide for this server."""
        return guide_mod.guide()

    @mcp.resource("mobilerun://policy")
    def policy_resource() -> str:
        """Safety policy boundaries and the active mode."""
        return f"active mode: {runtime.config.policy}\n\n{POLICY_TEXT}"

    @mcp.resource("mobilerun://ledger")
    async def ledger_resource() -> dict:
        """The current plan and recorded findings for the default device."""
        return runtime.session().ledger.to_dict()

    @mcp.resource("mobilerun://device/snapshot")
    async def snapshot_resource() -> str:
        """A live text snapshot of the default device's screen."""
        screen, marks = await runtime.session().perceive()
        return (
            f"{screen.phone.app} ({screen.phone.package}) keyboard={screen.phone.keyboard_visible}\n"
            + format_marks(marks)
        )

    @mcp.prompt(name="automate_task")
    def automate_task(request: str) -> str:
        """Plan and run a phone-automation task end-to-end with the right tools, safely."""
        return (
            f"Task: {request}\n\n"
            "Work the device in a loop, one consequential action per turn; the screen is ground truth.\n"
            "1. Find the app: lookup_app if you only have a name.\n"
            "2. Prefer a deep link: list_app_deeplinks(package_name), then open_deeplink(uri). "
            "Prefer typed tools (system_intent, media_control, read_notifications) over tapping.\n"
            "3. Otherwise launch_app, then read_screen and act by som_id (perceive_screen when you "
            "need to see it, detail='full' for unlabelled icons).\n"
            "4. Read each post_action_observation instead of re-checking; change strategy when "
            "something fails twice.\n"
            "5. validate_action before anything sensitive; policy_blocked is final.\n"
            "6. Verify the goal on screen, then end_session(reason, outcome, goal_type)."
        )

    @mcp.prompt(name="open_app")
    def open_app_prompt(app_name: str) -> str:
        """Open an app by name the reliable way: resolve, policy-check, launch or deep-link, confirm."""
        return (
            f'Open "{app_name}":\n'
            f'1. lookup_app(app_name="{app_name}") to get the package.\n'
            f'2. validate_action(gesture_type="launch_app", target="{app_name}"); if blocked, stop '
            "and tell the user.\n"
            "3. For a specific screen use list_app_deeplinks(package_name) and open_deeplink; "
            "otherwise launch_app(package_name=...).\n"
            "4. Confirm from the post_action_observation (read_screen if unclear) that the app is in "
            "front and loaded before the next action."
        )

    @mcp.prompt
    def perceive_act_verify(goal: str) -> str:
        """Work toward a goal on the device one verified step at a time."""
        return (
            f"Goal: {goal}\n\nStart with perceive_screen. Act with one tool, read its "
            "post_action_observation, and confirm the outcome before the next step. Re-perceive before "
            "tapping anything new (ids go stale). If an approach fails, change strategy."
        )

    @mcp.prompt
    def research_then_act(goal: str, app: str) -> str:
        """Look up the flow first, then execute it against the live screen."""
        return (
            f"Goal: {goal} (in {app}).\n\nFirst web_search 'how to <task> in {app} android', turn the "
            "answer into set_plan steps, then execute them. The screen overrules the article."
        )


def _apply_scopes(mcp: FastMCP, config: Config) -> None:
    if "write" not in config.scopes:
        mcp.disable(tags={"write"})
    if "read" not in config.scopes:
        mcp.disable(tags={"read"})


def build_core_server(config: Config | None = None) -> FastMCP:
    """Build the primary mobilerun-mcp server: core device API and device control."""
    config = config or Config.from_env()
    runtime = Runtime(config)

    @asynccontextmanager
    async def lifespan(_: FastMCP) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await runtime.aclose()

    mcp = FastMCP("mobilerun", instructions=CORE_INSTRUCTIONS, lifespan=lifespan)
    for module in CORE_MODULES:
        module.register(mcp, runtime)
    if config.enable_adb:
        adbtool.register(mcp, runtime)
    register_resources(mcp, runtime)
    _apply_scopes(mcp, config)
    return mcp


def build_server(config: Config | None = None, mode: str | None = None) -> FastMCP:
    """Factory creating the mobilerun server."""
    return build_core_server(config)


def main(argv: list[str] | None = None) -> None:
    """stdio by default; ``--http`` serves streamable HTTP at http://127.0.0.1:4816/mcp
    (MOBILERUN_MCP_HTTP_HOST / MOBILERUN_MCP_HTTP_PORT, or --host / --port)."""
    import argparse

    parser = argparse.ArgumentParser(prog="mobilerun-mcp")
    parser.add_argument("--http", action="store_true", help="serve over HTTP instead of stdio")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    config = Config.from_env()
    server = build_server(config)
    if args.http:
        server.run(
            transport="http",
            host=args.host or config.http_host,
            port=args.port or config.http_port,
            path="/mcp",
        )
    else:
        server.run()


if __name__ == "__main__":
    main()
