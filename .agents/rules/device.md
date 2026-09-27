---
name: device-automation-guidelines
trigger: always_on
---

# Device Automation Guidelines

When performing automation or calling MCP tools on the connected device:

1. **Target Identification**:
   - The target device is auto-detected via ADB or specified via `MOBILERUN_DEVICE`.
   - Ensure the target device is awake and unlocked before executing interaction flows.

2. **Perception Ground Truth**:
   - Never assume coordinates or guess layout positions without observing.
   - Always run `read_screen` or `perceive_screen` before tapping or clicking.
   - SOM IDs (`som_id`) are ephemeral and only valid for the specific screen observation in which they were captured.

3. **Settling & Verification**:
   - After interacting with UI components, read the `post_action_observation` to confirm UI update or app launch.
   - If an action fails or is blocked, re-observe the screen instead of repeating the same tap.
