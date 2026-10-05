# Mobilerun MCP

***English** · [Tiếng Việt](README.vi.md)*

A host-side Model Context Protocol (MCP) server that connects AI clients to Android (physical phones, emulators, redroid) over ADB and iOS through ios-portal. It focuses on device automation, screen perception, gestures, app management, and system intents — with all heavy lifting executed on the host, so nothing ARM-only has to run on the device.

This repo contains two cooperating pieces:

- an MCP server providing 94 tools exposed over stdio or HTTP
- the [Mobilerun Portal](https://github.com/droidrun/mobilerun-portal) accessibility service running on the Android device

## Highlights

- Host-side architecture: zero ARM-only dependency on device; runs seamlessly on physical devices, x86_64 emulators, and redroid containers
- Zero-setup runner via `npx` with automatic Python runtime, virtual environment, and dependency provisioning
- 94 exposed tools covering screen perception, gestures, apps, intents, notifications, media, and device control
- Set-of-Mark (SoM) visual perception with numbered labels (`som_id`), accessibility tree, and OCR (Tesseract / OmniParser v2)
- Built-in verification loop: every state-changing tool waits for the screen to settle and returns a `post_action_observation`
- Direct compatibility with droidrun's `mobilerun-core` Device API for programmatic automation
- Works over any network reachability supported by ADB (USB, Wi-Fi, LAN, VPN, `adb connect`)
- Built-in configurable safety policies (`off`, `standard`, `strict`) protecting sensitive personal and financial data

## Requirements

- Node.js `>=18` (for zero-setup execution via `npx`)
- `adb` (Android Debug Bridge, via [platform-tools](https://developer.android.com/tools/releases/platform-tools))
- An Android device or emulator with USB debugging enabled
- Python `3.10+` (optional, only needed for local source development)
- Tesseract OCR (optional, for OCR on screens with sparse accessibility trees)

## Installation and setup

### 1. Configure your AI client

#### Claude Code / Claude Desktop / VS Code / Cursor / Antigravity

Same server entry for all of them; only the file differs:

- Claude Code — `.mcp.json` in your project root
- Claude Desktop — `claude_desktop_config.json`
- Cursor — `.cursor/mcp.json`
- VS Code — `.vscode/mcp.json` (VS Code names the top-level key `servers`, not `mcpServers`)
- Antigravity — MCP settings panel (MCP Store -> **View raw config**), backed by `~/.gemini/config/mcp_config.json`, or `.agents/mcp_config.json` for a single workspace

```json
{
  "mcpServers": {
    "mobilerun": {
      "command": "npx",
      "args": ["-y", "@impeterwayne/mobilerun-mcp@latest"],
      "env": {
        "MOBILERUN_DEVICE": "<serial>"
      }
    }
  }
}
```

Or via Claude Code CLI:
```bash
claude mcp add --scope user mobilerun -e MOBILERUN_DEVICE=<serial> -- npx -y @impeterwayne/mobilerun-mcp@latest
```

> **Note:** `MOBILERUN_DEVICE` is optional if only one device is connected via ADB.

#### Codex CLI

`~/.codex/config.toml`:

```toml
[mcp_servers.mobilerun]
command = "npx"
args = ["-y", "@impeterwayne/mobilerun-mcp@latest"]
env = { MOBILERUN_DEVICE = "<serial>" }
```

#### OpenCode

`opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "mobilerun": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "@impeterwayne/mobilerun-mcp@latest"
      ],
      "environment": {
        "MOBILERUN_DEVICE": "<serial>"
      },
      "enabled": true
    }
  }
}
```

### 2. Device setup and Portal install

Download and install the **[Mobilerun Portal APK](https://github.com/droidrun/mobilerun-portal/releases)** on your Android device:

```bash
adb install -r <portal.apk>
```

Then enable the **Mobilerun Portal** accessibility service under **Settings > Accessibility**.

<details>
<summary>Manual Python / source setup</summary>

```bash
git clone https://github.com/Hi-im-Connect/mobilerun-mcp.git && cd mobilerun-mcp
uv venv --python 3.13 .venv && uv pip install -e .
```
On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.

In your MCP client configuration:
```json
{
  "mcpServers": {
    "mobilerun": {
      "command": "/path/to/mobilerun-mcp/.venv/bin/python",
      "args": ["-m", "mobilerun_mcp"],
      "env": { "MOBILERUN_DEVICE": "<serial>" }
    }
  }
}
```

</details>

## Available tools

94 tools covering screen perception, gestures, system control, notifications, media, and automation.

### Screen perception and reading

| Tool | What it does |
|------|--------------|
| `perceive_screen` | Captures an annotated screenshot with numbered marks (`som_id`) and list of interactive elements. |
| `read_screen` | ASCII/text grid representation of the screen and elements (settles screen before reading). |
| `get_ui_tree` | Compact accessibility hierarchy tree (classes, resource IDs, labels, flags, bounds). |
| `get_screenshot` | Returns current screenshot as base64 image data. |
| `screenshot` | Plain screenshot with optional overlay suppression. |
| `screenshot_path` | Takes a screenshot, saves it to a PNG file on disk, and returns the path. |

### Gestures, typing and input

| Tool | What it does |
|------|--------------|
| `tap` | Tap at coordinates `(x, y)` or on a numbered element mark (`som_id`). |
| `double_tap` | Double-tap at `(x, y)` or on a numbered mark (`som_id`). |
| `long_press` | Press and hold at `(x, y)` or on a numbered mark (`som_id`) with configurable duration. |
| `long_press_at` | Long press at precise `(x, y)` coordinates. |
| `swipe` | Swipe between two coordinates `(x1, y1)` to `(x2, y2)` with duration control. |
| `scroll_down` | Scroll content downward (revealing content below). |
| `scroll_up` | Scroll content upward (revealing content above). |
| `scroll_left` | Scroll content to the left. |
| `scroll_right` | Scroll content to the right. |
| `scroll` | Directional scroll by custom fraction of the screen. |
| `scroll_to` | Scroll until target text or coordinates become visible. |
| `type_text` | Type text into the currently focused input field or target `som_id`. |
| `type` | Types text with optional typing speed (WPM) and clear options. |
| `clear_input` | Clears text from the currently focused input field. |
| `press_home` | Simulates pressing the physical/virtual Home button. |
| `press_back` | Simulates pressing the Back button (closes keyboards and popups). |
| `press_enter` | Simulates pressing Enter / Search / Submit. |
| `open_recent_apps` | Opens the recent applications overview switcher. |
| `key` | Dispatches hardware key codes or named keys (`back`, `home`, `volume_up`, `wakeup`, etc.). |
| `press` | Legacy button press helper (`home`, `back`, `enter`). |

### Apps and deep links

| Tool | What it does |
|------|--------------|
| `launch_app` | Launch an application by fuzzy name or exact package name, waiting for foreground. |
| `start_app` | Starts an app by package ID and optional specific activity. |
| `lookup_app` | Search installed apps by name or package; returns ranked candidates with scores. |
| `list_apps` | Lists installed applications (user-installed and optional system apps). |
| `list_app_deeplinks` | Discovers available deep links and shortcuts for an app. |
| `resolve_deeplink` | Resolves which application handles a given URI or intent action. |
| `open_deeplink` | Opens a screen directly via URI, app shortcut, or intent action. |

### System intents, contacts, files and media

| Tool | What it does |
|------|--------------|
| `system_intent` | Executes common Android intents (set alarm, navigate, dial phone, open browser). |
| `resolve_contact` | Finds contacts by partial name and returns phone numbers. |
| `find_files` | Searches the device media store (downloads, pictures, documents, videos). |
| `open_file` | Opens a file on device in its default application. |
| `get_media_sessions` | Retrieves active media playback sessions, track metadata, and volume. |
| `media_control` | Controls media playback (play, pause, next, previous, stop, rewind, fast forward). |
| `volume_up` | Increases media volume. |
| `volume_down` | Decreases media volume. |
| `mute` | Toggles media mute state. |

### Notifications

| Tool | What it does |
|------|--------------|
| `read_notifications` | Reads active status-bar notifications with titles, text, and action buttons. |
| `dismiss_notification` | Dismisses a specific notification or clears all dismissible ones. |
| `notification_action` | Triggers a notification action button or sends an inline reply. |

### mobilerun-core Device API

| Tool | What it does |
|------|--------------|
| `ui` | Full UI state snapshot (`a11y_tree`, phone state, device context). |
| `ui_json` | Serialized JSON string of the device UI hierarchy. |
| `ui_with_recovery` | UI snapshot with automatic retry logic for transient/reloading view hierarchies. |
| `capabilities` | Queries supported backend capabilities, actions, and platform information. |
| `supports` | Checks whether a specific action is supported on the target device. |
| `screen_size` | Returns device screen width and height in pixels. |
| `current_app_id` | Package name of the current foreground application. |
| `time` | Current device system time. |
| `find_nodes` | Finds nodes matching filters (text, ID, class, substring), including off-screen. |
| `find_nodes_on_screen` | Finds nodes matching filters strictly within visible screen bounds. |
| `tap_text` | Finds and taps the first visible node containing specific text. |
| `tap_node` | Taps the center of a node object returned from `find_nodes`. |
| `tap_and_wait` | Taps target element and waits for UI to become idle. |
| `scroll_until` | Continuously scrolls until an element matching criteria appears on screen. |
| `assert_on` | Asserts that a specific app package is currently in the foreground. |
| `assert_text_visible` | Asserts that expected text is visible within a timeout. |
| `wait_for_app` | Waits until the specified app package reaches the foreground. |
| `wait_for_idle` | Waits for screen animations and UI updates to finish settling. |
| `wait_for_screen_change` | Waits until UI changes from its current state. |
| `wait_for_text` | Waits until an element containing the specified text appears. |
| `wait_for_nodes` | Polls until nodes matching filters are detected. |
| `open_and_settle` | Launches an app and waits until it is fully loaded and idle. |
| `stop_app` | Force-stops an application with optional data clearing. |
| `install_app` | Installs an APK file from host storage onto the device. |
| `uninstall_app` | Uninstalls an application package. |
| `grant_permission` | Grants runtime permission (`android.permission.*`) to an app. |
| `open_deep_link` | Dispatches a deep link or view intent pinned to a package. |
| `execute_script` | Executes JavaScript within the foreground browser page. |
| `get_clipboard` | Reads current clipboard text content. |
| `set_clipboard` | Writes text content to the device clipboard. |

### Device management and connection

| Tool | What it does |
|------|--------------|
| `get_device_status` | Comprehensive status: battery, screen state, foreground app, storage, IP. |
| `list_devices` | Lists available connected ADB devices and emulators. |
| `ping_device` | Verifies low-latency reachability of the device and Portal service. |
| `connect_device` | Re-establishes ADB and Portal connection for a target device. |
| `disconnect_device` | Disconnects a network/TCP ADB device and cleans up session state. |
| `setup_portal` | Installs and initializes the Mobilerun Portal service on the device. |
| `doctor` | Runs health diagnostics across ADB, device authorization, and the Portal. |
| `request_screen_capture_permission` | Compatibility check for screenshot capture permissions. |
| `echo` | Simple round-trip ping verifying MCP transport responsiveness. |
| `adb` | Executes raw ADB commands (disabled by default; requires `MOBILERUN_MCP_ENABLE_ADB=1`). |

### Planning, verification and research

| Tool | What it does |
|------|--------------|
| `verify_action` | Verifies post-action outcomes against expected text or UI element state. |
| `validate_action` | Pre-validates planned actions against safety policy before execution. |
| `wait_for` | Configurable wait for long-running operations (downloads, uploads, page loads). |
| `watch_device_events` | Listens to device events (foreground app changes, notifications, keyboard). |
| `web_search` | Searches the web for application UI instructions and workflows. |
| `set_plan` | Initializes an execution plan checklist with goals and deliverables. |
| `mark_step` | Updates the status of a plan step (`pending`, `in_progress`, `done`, `failed`). |
| `record_finding` | Records key data points and evidence extracted during device interaction. |
| `end_session` | Concludes automation session and reports summary results. |
| `get_usage_guide` | Returns best practice instructions and tips for controlling devices. |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MOBILERUN_DEVICE` | First connected device | Target ADB serial, network address (`host:port`), or `ios` |
| `MOBILERUN_MCP_POLICY` | `off` | Safety policy: `off`, `standard` (blocks banking/auth), `strict` (blocks credentials/PINs) |
| `MOBILERUN_MCP_SCOPES` | `read,write` | Tool scope restriction (`read` exposes only read-only inspection tools) |
| `MOBILERUN_MCP_ENABLE_ADB` | `0` | Set to `1` to expose raw `adb` shell execution tool |
| `BRAVE_API_KEY` | unset | API key for Brave search via `web_search` (defaults to DuckDuckGo) |
| `TAVILY_API_KEY` | unset | API key for Tavily search via `web_search` |
| `MOBILERUN_DETECTOR_MODEL` | Auto-downloaded | Local path override for OmniParser icon detection ONNX model |
| `MOBILERUN_MCP_HTTP_HOST` | `127.0.0.1` | Host address for HTTP MCP mode (`--http`) |
| `MOBILERUN_MCP_HTTP_PORT` | `4816` | Port for HTTP MCP mode (`--http`) |
| `MOBILERUN_ADB_BIN` | `adb` on PATH | Custom path to `adb` binary |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `[device_unreachable] no device selected` | Run `adb devices`, then set `MOBILERUN_DEVICE=<serial>` in your client config |
| `adb devices` shows `unauthorized` | Unlock the phone and tap **Allow** on the USB debugging authorization prompt |
| `adb devices` is empty or `offline` | Reconnect USB cable or run `adb connect <host>:<port>` for wireless/network devices |
| `adb: command not found` | Install platform-tools or specify binary location with `MOBILERUN_ADB_BIN` |
| `Mobilerun Portal is not enabled` | Enable in **Settings > Accessibility > Mobilerun Portal**, or run `mobilerun setup -d <serial>` |
| `[stale_som_id]` error | The screen changed after the last action; call `perceive_screen` or `read_screen` to refresh IDs |
| Client lists no `mobilerun` tools | Check client config file syntax and paths; restart the AI client |

## License

MIT. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
