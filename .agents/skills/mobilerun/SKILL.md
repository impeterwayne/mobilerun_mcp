---
name: mobilerun
description: >-
  Controls, inspects, and automates actions on connected Android devices using core mobilerun MCP tools.
  Use when controlling the phone, reading screens, launching apps, or running UI automation.
---

# Mobilerun Device Automation Skill

This skill guides automation, inspection, and interaction with Android devices using the **Mobilerun MCP** tool suite.

---

## 1. Architecture

The workspace provides the **`mobilerun`** MCP server containing 94 core device tools covering screen perception, input gestures, app lifecycle, `mobilerun-core` SDK methods, notifications, media, system intents, and diagnostics.

> Complete parameter-level specifications for all tools can be found in the [Tools Reference Catalog](references/tools_reference.md).

---

## 2. Tool Categories (The 94 Core Tools)

### A. Screen Perception & Visual Grounding (6 tools)
- **`read_screen`**: Generates a fast, lightweight ASCII/text-grid view of visible elements. Use this first when you only need to read text or understand layout without image generation overhead.
- **`perceive_screen`**: Captures an annotated screenshot and generates numbered Set-of-Marks (`som_id`). Use `detail="full"` if unlabelled icons need detection and OCR.
- **`get_ui_tree`**: Fetches the structured accessibility node hierarchy with class names, resource IDs, bounds, and interactive flags.
- **`get_screenshot` / `screenshot` / `screenshot_path`**: Plain screenshot captures without overlays, returned as images or saved to disk.

### B. Input Gestures & Hardware Navigation (18 tools)
- **`tap`**: Taps by coordinates `(x, y)` or element `som_id`.
- **`double_tap` / `long_press` / `long_press_at`**: Advanced tap gestures with duration controls.
- **`swipe`**: Precise coordinate drag from `(x1, y1)` to `(x2, y2)` over `duration_ms`.
- **`scroll_down` / `scroll_up` / `scroll_left` / `scroll_right` / `scroll` / `scroll_to`**: Directional scrolling. `scroll_down` reveals content below (swiping up).
- **`type_text`**: Enters text into the focused field (or pass `som_id`). Supports `clear=true` (replaces content) and `submit=true` (presses Enter).
- **`press_home` / `press_back` / `press_enter`**: Standard Android hardware buttons. `press_back` also closes soft keyboards.
- **`open_recent_apps`**: Opens the Android task switcher.
- **`key`**: Dispatches keycodes by name (`back`, `home`, `enter`, `delete`, `tab`, `space`, etc.).

### C. Application Lifecycle & Management (7 tools)
- **`launch_app`**: Opens an app by name (fuzzy matching e.g. `"YouTube"`, `"Chrome"`) or package ID.
- **`start_app`**: Starts an app by package ID, optionally launching a specific activity component.
- **`stop_app`**: Force-stops a running app (`app_id`). Pass `clear_data=true` to wipe app data/cache.
- **`lookup_app`**: Searches installed apps with fuzzy matching and returns matching candidate package IDs.
- **`list_apps`**: Lists installed packages on the device (`include_system_apps=false` by default).
- **`open_and_settle`**: Launches an application and blocks until it is in the foreground and idle.
- **`install_app` / `uninstall_app`**: Installs an APK from the host file system or uninstalls a package.

### D. Deep Links & Instant Navigation (3 tools)
- **`list_app_deeplinks`**: Discovers registered URI schemes, intent actions, and launcher shortcuts for a package.
- **`open_deeplink` / `open_deep_link`**: Jumps directly to an in-app screen or settings page (e.g. `android.settings.WIFI_SETTINGS` or `market://details?id=...`), bypassing manual UI navigation.
- **`resolve_deeplink`**: Verifies which app handles a URI before invoking it.

### E. Structured `mobilerun-core` SDK Automation (14 tools)
Direct programmatic access to the underlying `mobilerun-core` Python SDK:
- **`ui` / `ui_json` / `ui_with_recovery`**: Accessibility tree snapshots with resilient retry logic.
- **`find_nodes` / `find_nodes_on_screen`**: Queries nodes matching exact or substring filters (`text_contains`, `resource_id`, `class_name`).
- **`tap_text`**: Directly taps on-screen nodes matching specified text without requiring SOM IDs.
- **`tap_node`**: Taps a node dictionary returned by `find_nodes`.
- **`tap_and_wait`**: Taps text or node and waits until the screen settles into an idle state.
- **`scroll_until`**: Continuously scrolls until an element matching filters is visible on screen.
- **`clear_input`**: Clears the currently active input field.
- **`get_clipboard` / `set_clipboard`**: Interacts with the Android system clipboard.
- **`execute_script`**: Runs JavaScript inside foreground browser pages.
- **`grant_permission`**: Directly grants Android runtime permissions (e.g. `android.permission.POST_NOTIFICATIONS`).

### F. Assertions & Settling Waits (7 tools)
- **`assert_on`**: Fails immediately unless the expected package is in the foreground.
- **`assert_text_visible`**: Fails unless target text appears on screen within `timeout` seconds.
- **`wait_for_app`**: Polls until the specified app package reaches the foreground.
- **`wait_for_idle`**: Polls until UI animations and modifications cease.
- **`wait_for_screen_change`**: Waits until the accessibility hierarchy changes from baseline.
- **`wait_for_text` / `wait_for_nodes`**: Polls until matching elements appear in the accessibility tree.

### G. System Intents & Shortcuts (2 tools)
- **`system_intent`**: Dispatches system-level verbs directly:
  - `set_alarm(hour, minute, label)`
  - `set_timer(seconds, label)`
  - `dial(phone_number)`
  - `compose_sms(phone_number, body)`
  - `add_calendar_event(title, start, end, location, notes)`
  - `share_text(text, subject)`
  - `navigate(destination, mode)`
- **`resolve_contact`**: Queries contacts by partial name to retrieve associated phone numbers.

### H. Notifications & Media Playback (8 tools)
- **`read_notifications`**: Reads active status-bar notifications with titles, text, and action buttons without opening notification shade.
- **`dismiss_notification`**: Dismisses notifications by key or package name, or dismisses all clearable notifications.
- **`notification_action`**: Interacts with notification action buttons directly (e.g. reply, pause, mark read) without opening the app.
- **`get_media_sessions`**: Inspects active playback sessions, artist, track, and playback state.
- **`media_control`**: Controls playback globally or per-app (`play`, `pause`, `play_pause`, `next`, `previous`, `stop`).
- **`volume_up` / `volume_down` / `mute`**: Controls media volume stream levels.

### I. Device Diagnostics & Setup (9 tools)
- **`get_device_status`**: Queries battery level, screen state, foreground app, resolution, IP addresses, and volume.
- **`list_devices`**: Lists available ADB devices.
- **`ping_device` / `echo`**: Verifies ADB and Portal transport connectivity.
- **`connect_device` / `disconnect_device`**: Manages device ADB connection lifecycle.
- **`setup_portal`**: Installs and enables the Mobilerun Portal service APK.
- **`doctor`**: Runs full diagnostic suite across ADB, USB/TCP connection, and Portal service permissions.
- **`capabilities` / `supports` / `screen_size` / `current_app_id` / `time`**: Device inspection queries.

### J. Plan Ledger & Session Tracking (6 tools)
- **`set_plan`**: Registers multi-step plan milestones (`steps`, `goal`, `target_count`).
- **`mark_step`**: Updates status of a milestone (`pending`, `in_progress`, `done`, `skipped`, `failed`).
- **`record_finding`**: Records verified facts (requires quoting text present on the live screen).
- **`end_session`**: Signals task completion (`outcome="success"` requires evidence verification).
- **`get_usage_guide`**: Built-in interactive guidance topics.
- **`web_search`**: Searches online documentation for app-specific navigation steps.

### K. Device Storage & Files (2 tools)
- **`find_files`**: Searches indexed device files (images, audio, downloads) by filename.
- **`open_file`**: Opens a file via content URI in its default Android application.

---

## 3. Tool Selection Decision Tree

To maximize speed, accuracy, and reliability, choose tools following this hierarchy:

```
Goal: Perform an Action or Navigate
├── Need system action (alarm, timer, call, SMS, nav)?
│   └──> Use `system_intent` (instant, no UI navigation)
├── Need to jump to a specific app screen or settings?
│   └──> Use `list_app_deeplinks` -> `open_deeplink`
├── Need to open or close an application?
│   ├── Open: `launch_app(app_name="...")` or `open_and_settle(...)`
│   └── Close: `stop_app(app_id="...")`
├── Need to read or verify what is on screen?
│   ├── Fast text check: `read_screen`
│   ├── Visual inspection with numbered clickable marks: `perceive_screen`
│   └── Programmatic node inspection: `find_nodes_on_screen` or `current_app_id`
├── Need to tap an element?
│   ├── Known exact/partial text: `tap_text(text="...")`
│   ├── After perceive_screen: `tap(som_id=...)`
│   └── Structured node: `tap_node(node=...)`
└── Need to type text?
    └──> Tap field -> `type_text(text="...", clear=True, submit=True)`
```

---

## 4. The Golden Rules of Mobilerun Automation

1. **SOM IDs are Single-Use & Ephemeral**:
   - Numbered marks (`som_id`) returned by `perceive_screen` belong strictly to that single frame.
   - Any action (tap, swipe, scroll, type, keypress) invalidates all existing IDs (`stale_som_id`).
   - Never re-use an old `som_id`. Call `read_screen` or `perceive_screen` again if needed.

2. **Inspect `post_action_observation` Before Acting Again**:
   - Every state-changing tool settles and returns `post_action_observation` (`foreground_app`, `element_count`, `keyboard_visible`, `screen_changed`).
   - Check this observation to confirm success instead of wasting extra turns re-reading the screen.

3. **Never Guess Coordinates**:
   - Screen resolution and layout vary across devices and orientations.
   - Always rely on `tap_text`, `som_id`, or `find_nodes_on_screen` rather than hardcoding `(x, y)` pixels.

4. **Prefer Direct Typed Tools Over Tapping**:
   - `system_intent`, `open_deeplink`, `read_notifications`, and `media_control` execute in a single round-trip without multi-step screen navigation.

5. **Stop Apps Cleanly**:
   - To close an app, use `stop_app(app_id="com.example.app")` rather than pressing Back repeatedly.

---

## 5. Troubleshooting & Health Checks

- **Check ADB Connection**:
  ```powershell
  adb devices -l
  ```
- **Verify Portal Accessibility Service**:
  ```powershell
  adb shell settings get secure enabled_accessibility_services
  ```
  Should contain `com.mobilerun.portal/com.mobilerun.portal.service.MobilerunAccessibilityService`.
- **Run Diagnostics via MCP**:
  - Call `doctor()` or `get_device_status()` to inspect connection health and Portal readiness.
