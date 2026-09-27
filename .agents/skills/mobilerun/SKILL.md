---
name: mobilerun
description: >-
  Controls, inspects, and automates actions on connected Android devices using core mobilerun MCP tools.
  Use when controlling the phone, reading screens, launching apps, or running UI automation.
---

# Mobilerun Device Control Skill

Use this skill to control the connected Android device using core mobilerun MCP tools.

## Device Context
- **Target**: Connected Android device (physical device or emulator)
- **Service**: Mobilerun Portal (`com.mobilerun.portal`) installed and active.

## Core Interaction Loop

1. **Observe the Screen**:
   - Call `read_screen()` to inspect the current screen layout as a quick text grid.
   - Or call `perceive_screen()` to retrieve clickable elements and SOM IDs (`som_id`).
   - Or call `ui()` / `find_nodes_on_screen()` to query the accessibility node tree.

2. **Execute Action**:
   - Tap element: `tap(som_id=...)` or `tap(x=..., y=...)` or `tap_text(text="...")`.
   - Enter text: Focus input and call `type_text(text="...")` or `clear_input()`.
   - Hardware keys: `press_home()`, `press_back()`, or `press_enter()`.
   - Launch application: `launch_app(app_name="...")`, `launch_app(package_name="...")`, or `open_deeplink(uri="...")`.

3. **Check Observation**:
   - Inspect the `post_action_observation` returned by the tool (`package`, `keyboard_visible`, `screen_changed`).
   - Verify that the action took effect before sending the next command.

## Troubleshooting

- **Check ADB Connection**:
  ```powershell
  adb devices -l
  ```
- **Verify Portal Accessibility Service**:
  ```powershell
  adb shell settings get secure enabled_accessibility_services
  ```
  Should contain `com.mobilerun.portal/com.mobilerun.portal.service.MobilerunAccessibilityService`.
- **Run Live Health Check**:
  ```powershell
  cmd /c "set MOBILERUN_DEVICE=<device_serial> && .\.venv\Scripts\pytest -m live tests\live\test_m5_live.py -k test_device_argument_forms -v"
  ```
