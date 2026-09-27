# mobilerun-mcp Workspace Instructions

This workspace configures the **mobilerun** MCP servers and device automation harness for Antigravity at workspace scope.

## Architecture & Detached Servers

The server suite is modularized into three dedicated MCP servers:

1. **`mobilerun` (Core Device Server, default)**:
   - Contains 94 core tools covering `mobilerun-core` Device API (`ui`, `find_nodes`, `tap_text`, `wait_for_app`, `get_clipboard`), screen perception (`read_screen`, `perceive_screen`), input gestures (`tap`, `swipe`, `type_text`, `press_home`), system intents, notifications, and media.
   - Run: `python -m mobilerun_mcp.server` (or `mobilerun-mcp.exe`)

2. **`mobilerun-agent` (Agent Server)**:
   - Contains the `mobilerun` agent action set (`get_state`, `click`, `type_secret`), local CLI agent runs (`run_task`, `list_tasks`), and macro replay.
   - Run: `python -m mobilerun_mcp.agent_server` (or `mobilerun-agent-mcp.exe`)

3. **`mobilerun-cloud` (Cloud Server)**:
   - Contains Mobilerun Cloud platform tools (`create_device`, `manage_device`, credentials, flows, workflows).
   - Run: `python -m mobilerun_mcp.cloud_server` (or `mobilerun-cloud-mcp.exe`)

All three are registered at workspace scope in [.agents/mcp_config.json](file:///d:/Quest/mobilerun-mcp/.agents/mcp_config.json).

## Connected Device Target

- **Target Device**: Connected Android device (auto-detected via `adb devices`, or specified via `MOBILERUN_DEVICE`)
- **Accessibility Service**: `com.mobilerun.portal` (installed and active)

## Core Interaction Workflow

When operating the phone using core mobilerun MCP tools:

1. **Perception**:
   - `read_screen`: Generates an ASCII/text grid representation of the screen.
   - `perceive_screen`: Returns numbered marks (`som_id`) and UI tree elements. Use `detail="full"` if unlabelled icons need detection.
   - Note: Numbered IDs (`som_id`) represent a single captured frame. Any action or state change invalidates previous IDs.

2. **Actions**:
   - Use `tap(som_id=...)` or `tap(x=..., y=...)` to tap an element.
   - Use `type_text(text=..., som_id=...)` to input text into the focused field.
   - Use `press_home()`, `press_back()`, or `press_enter()` for hardware navigation.
   - Direct core controls: `tap_text(text=...)`, `find_nodes_on_screen(...)`, `open_deeplink(uri=...)`, `launch_app(app_name=...)`.

3. **Verification**:
   - Every state-changing tool returns `post_action_observation` (`package`, `element_count`, `keyboard`, `screen_changed`).
   - Inspect this observation to confirm success before taking subsequent steps.

## Testing & Execution Commands

- Test device connectivity:
  ```powershell
  cmd /c "set MOBILERUN_DEVICE=<device_serial> && .\.venv\Scripts\pytest -m live tests\live\test_m5_live.py -v"
  ```
- Run core server manually (stdio):
  ```powershell
  .\.venv\Scripts\python.exe -m mobilerun_mcp.server
  ```
- Run core server over HTTP:
  ```powershell
  .\.venv\Scripts\python.exe -m mobilerun_mcp.server --http --port 4816
  ```
- Run agent server manually:
  ```powershell
  .\.venv\Scripts\python.exe -m mobilerun_mcp.agent_server
  ```
- Run cloud server manually:
  ```powershell
  .\.venv\Scripts\python.exe -m mobilerun_mcp.cloud_server
  ```
