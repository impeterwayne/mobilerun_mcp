# Mobilerun MCP Tools Reference Catalog

This document provides a comprehensive reference of all **94 Core tools** available in the Mobilerun MCP server.

---

## 1. Device Tools (`mobilerun` - 94 Tools)

### 1.1 Perception & Screen Inspection (6 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `read_screen` | Generates a lightweight ASCII/text-grid view of the screen. Fast, cheap, and does not produce an image. Best for reading text and initial layout inspection. | `device` (optional) |
| `perceive_screen` | Captures an annotated screenshot and returns numbered marks (`som_id`) with bounding boxes and labels. Set `detail="full"` to enable icon detection and OCR. | `detail` ("fast" \| "full"), `include_screenshot`, `device` |
| `get_ui_tree` | Retrieves a compact accessibility node hierarchy with class names, resource IDs, text, bounds, and flags (Clickable, Long-clickable, Editable, Scrollable, etc.). | `device` |
| `get_screenshot` | Returns a clean screenshot as an image (JPEG/PNG) without annotations. | `device` |
| `screenshot` | Captures a plain screenshot with an option to hide the Portal element overlay. | `hide_overlay` (bool), `device` |
| `screenshot_path` | Takes a screenshot, saves it to a temporary file on the host machine, and returns the file path. | `device` |

### 1.2 Input Gestures & Hardware Keys (18 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `tap` | Taps at coordinates `(x, y)` or at the center of a `som_id`. | `som_id`, `x`, `y`, `device` |
| `double_tap` | Double-taps at coordinates `(x, y)` or at a `som_id`. | `som_id`, `x`, `y`, `device` |
| `long_press` | Long presses at `(x, y)`, `som_id`, or `index` for a specified duration (default 1000ms). | `som_id`, `x`, `y`, `duration_ms`, `device` |
| `long_press_at` | Agent-compatible long press at `(x, y)`. | `x`, `y`, `duration_ms`, `device` |
| `swipe` | Swipes between two points `(x1, y1)` to `(x2, y2)`. | `x1`, `y1`, `x2`, `y2`, `duration_ms`, `device` |
| `scroll_down` | Scrolls down (swipes up) to reveal content below. | `distance` (fraction), `device` |
| `scroll_up` | Scrolls up (swipes down) to reveal content above. | `distance` (fraction), `device` |
| `scroll_left` | Scrolls left to reveal content to the left. | `distance` (fraction), `device` |
| `scroll_right` | Scrolls right to reveal content to the right. | `distance` (fraction), `device` |
| `scroll` | General scroll in any direction (`"up"`, `"down"`, `"left"`, `"right"`). | `direction`, `distance`, `device` |
| `scroll_to` | Drags content between points or scrolls until an element is visible. | `x1`, `y1`, `x2`, `y2`, `device` |
| `type_text` | Types text into the currently focused field (or taps `som_id` first). Set `clear=true` to replace existing text; `submit=true` presses Enter. | `text`, `som_id`, `clear`, `submit`, `device` |
| `type` | Types text using index targeting or stealth typing. | `text`, `index`, `stealth`, `device` |
| `press_home` | Navigates to the home screen (KEYCODE_HOME). | `device` |
| `press_back` | Presses the Back button (KEYCODE_BACK); also closes soft keyboards. | `device` |
| `press_enter` | Presses the Enter button (KEYCODE_ENTER) to submit forms/search queries. | `device` |
| `open_recent_apps` | Opens the Android app switcher / recents overview. | `device` |
| `key` | Sends a named Android keycode (`"home"`, `"back"`, `"enter"`, `"delete"`, `"tab"`, `"space"`, etc.). | `key_name`, `device` |

### 1.3 Application Lifecycle & Deep Links (7 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `launch_app` | Launches an app by user-friendly name (e.g. `"YouTube"`, `"Spotify"`) or exact package name. Resolves fuzzy names. | `app_name`, `package_name`, `device` |
| `start_app` | Starts an app by package ID, optionally targeting an explicit activity. | `app_id`, `activity`, `device` |
| `lookup_app` | Searches installed applications with fuzzy matching and returns matching candidate package IDs. | `app_name`, `device` |
| `list_apps` | Lists installed packages (filters out system packages unless `include_system_apps=true`). | `include_system_apps`, `device` |
| `list_app_deeplinks` | Discovers available deep link templates and shortcuts for a package. | `package_name`, `device` |
| `resolve_deeplink` | Checks which package and activity handles a specific URI or intent action without executing it. | `uri`, `device` |
| `open_deeplink` | Opens a URI, app shortcut, or intent action directly, bypassing navigation steps. | `uri`, `package_name`, `device` |

### 1.4 Structured `mobilerun-core` Device API (31 tools)
Direct bindings to the `mobilerun-core` Python SDK `Device` instance:
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `ui` | Returns a structured raw UI snapshot containing the accessibility tree, phone state, and device context. | `filter` (bool), `device` |
| `ui_json` | Returns the accessibility UI snapshot serialized as formatted JSON text. | `filter`, `indent`, `device` |
| `ui_with_recovery` | Takes a UI snapshot with automatic retry logic if the tree is empty or lagging. | `filter`, `device` |
| `capabilities` | Queries supported device capabilities, backend type, and available actions. | `device` |
| `supports` | Checks whether the device backend supports a specific action (e.g. `execute_script`, `get_clipboard`). | `action`, `device` |
| `screen_size` | Returns device screen dimensions `[width, height]` in pixels. | `device` |
| `current_app_id` | Returns the package name / bundle ID of the currently active foreground app. | `device` |
| `time` | Returns the current system clock time on the device. | `device` |
| `find_nodes` | Queries the full accessibility tree matching filters (`text`, `resource_id`, `class_name`, `*_contains`). Includes off-screen nodes. | `text`, `resource_id`, `class_name`, `text_contains`, `tree`, `device` |
| `find_nodes_on_screen` | Filters accessibility nodes matching criteria that are strictly inside visible screen bounds. | `text`, `resource_id`, `class_name`, `text_contains`, `device` |
| `tap_text` | Taps the first visible element on screen matching or containing the given text. | `text`, `device` |
| `tap_node` | Taps the center coordinates of a structured node dictionary returned from `find_nodes`. | `node`, `stealth`, `device` |
| `tap_and_wait` | Taps text or node and waits until the screen settles into an idle state. | `target`, `idle` (seconds), `device` |
| `scroll_until` | Automatically scrolls in a direction until a matching node appears on screen. | `text`, `resource_id`, `direction`, `max_swipes`, `device` |
| `clear_input` | Wipes the contents of the currently active focused input field. | `device` |
| `assert_on` | Asserts that a specific `app_id` (package) is in the foreground, raising an error otherwise. | `app_id`, `device` |
| `assert_text_visible` | Asserts that specific text appears on the visible screen within a timeout period. | `text`, `timeout`, `device` |
| `wait_for_app` | Polls until a specific app package is in the foreground. | `app_id`, `timeout`, `poll`, `device` |
| `wait_for_idle` | Polls until UI modifications cease and the screen is completely stationary. | `timeout`, `poll`, `device` |
| `wait_for_screen_change` | Polls until the accessibility tree changes from the initial baseline. | `timeout`, `poll`, `device` |
| `wait_for_text` | Polls until a node containing the given text exists in the accessibility hierarchy. | `text`, `timeout`, `poll`, `device` |
| `wait_for_nodes` | Polls find_nodes with given filters until at least one matching node is found. | `text`, `resource_id`, `on_screen`, `timeout`, `device` |
| `open_and_settle` | Launches an application package and blocks until it is in the foreground and idle. | `app_id`, `timeout`, `idle`, `device` |
| `stop_app` | Force-stops an application package. Set `clear_data=true` to wipe storage/cache. | `app_id`, `clear_data`, `device` |
| `install_app` | Installs an APK from the host file system onto the target device. | `path`, `replace`, `grant_permissions`, `device` |
| `uninstall_app` | Uninstalls an application package from the device. | `app_id`, `device` |
| `grant_permission` | Grants a runtime Android permission (e.g. `android.permission.POST_NOTIFICATIONS`) to an app. | `package`, `permission`, `device` |
| `open_deep_link` | Low-level dispatch of an intent/URI, optionally pinned to a package or action. | `deep_link`, `package_name`, `action`, `device` |
| `execute_script` | Executes JavaScript inside a foreground browser page and returns evaluation results. | `js`, `device` |
| `get_clipboard` | Reads current text content from the Android clipboard. | `device` |
| `set_clipboard` | Copies text to the Android clipboard. | `value`, `device` |

### 1.5 System Intents & Shortcuts (2 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `system_intent` | Dispatches common Android system actions without navigating UI: `set_alarm`, `set_timer`, `dial`, `compose_sms`, `add_calendar_event`, `share_text`, `navigate`. | `action` / `verb`, `hour`, `minute`, `seconds`, `label`, `phone_number`, `body`, `destination`, etc. |
| `resolve_contact` | Looks up contacts in the device address book by partial name and returns matching phone numbers. | `name`, `device` |

### 1.6 Notifications & Media Management (8 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `read_notifications` | Reads all active status-bar notifications with titles, text, packages, and available action buttons. | `device` |
| `dismiss_notification` | Dismisses a notification by key, package, or dismisses all clearable notifications. | `key`, `package`, `all`, `device` |
| `notification_action` | Triggers a notification action button directly (e.g. reply, dismiss, archive) without launching the app. | `key`, `action_id`, `reply_text`, `device` |
| `get_media_sessions` | Returns active media playback sessions, track title, artist, playback state, and media volume. | `device` |
| `media_control` | Controls playback globally or per-app (`play`, `pause`, `play_pause`, `next`, `previous`, `stop`). | `action`, `package_name`, `device` |
| `volume_up` | Increases media volume by N steps. | `steps`, `device` |
| `volume_down` | Decreases media volume by N steps. | `steps`, `device` |
| `mute` | Toggles media volume mute state. | `muted` (bool), `device` |

### 1.7 Device Diagnostics & Setup (9 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `get_device_status` | Comprehensive status: battery, screen power, foreground app, screen size, IP addresses, volume. | `device` |
| `list_devices` | Lists connected local ADB devices or cloud virtual devices. | `scope` ("local" \| "cloud") |
| `ping_device` | Pings the device and checks connectivity across ADB and Portal transports. | `device` |
| `connect_device` | Re-establishes ADB and Portal connections for a specified device serial or host:port. | `device` |
| `disconnect_device` | Disconnects a TCP/IP ADB device and clears session state. | `device` |
| `setup_portal` | Installs, updates, or configures the Mobilerun Portal APK and accessibility service on the device. | `path`, `device` |
| `doctor` | Runs health diagnostics across ADB, USB/TCP connection, and Portal service permissions. | `device` |
| `request_screen_capture_permission` | Compatibility check for screenshot capture permissions. | `device` |
| `echo` | Tests MCP communication loopback without accessing the device. | `message` |

### 1.8 Files & Storage (2 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `find_files` | Searches the device media store / download folders by query, returning media URIs. | `query`, `media_type`, `limit`, `device` |
| `open_file` | Opens a media content URI in its system default viewer app. | `uri`, `device` |

### 1.9 Waiting, Events & Validation (4 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `wait_for` | Waits for long asynchronous operations (e.g. downloads, background sync) by condition. | `condition`, `timeout_seconds`, `device` |
| `watch_device_events` | Streams accessibility and system events from Portal for a duration. | `timeout_seconds`, `event_types`, `device` |
| `validate_action` | Pre-checks an action against safety policies before execution. | `gesture_type`, `target`, `device` |
| `verify_action` | Confirms the expected post-condition on screen (`text_visible`, `text_gone`, `app_matches`). | `kind`, `target`, `device` |

### 1.10 Plan Ledger & Execution Tracking (6 tools)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `set_plan` | Registers a multi-step execution checklist with goal, deliverable, and target item count. | `steps`, `goal`, `deliverable`, `target_count` |
| `mark_step` | Updates the status of a plan step (`pending`, `in_progress`, `done`, `skipped`, `failed`). | `step_index`, `status`, `notes` |
| `record_finding` | Logs a verified fact found on screen; requires an exact quotation from the current screen. | `item`, `quote` |
| `end_session` | Formally completes an automation session, validating findings against targets. | `outcome` ("success" \| "partial" \| "failed"), `reason` |
| `get_usage_guide` | Retrieves built-in guidance topics (`overview`, `shortcuts`, `text_entry`, `failures`, `safety`). | `topic` |
| `web_search` | Performs a targeted search for application UI flows or procedures. | `query` |

### 1.11 Legacy Compatibility (1 tool)
| Tool | Description | Primary Arguments |
| :--- | :--- | :--- |
| `press` | Legacy button press for `"home"`, `"back"`, or `"enter"`. Kept for backward compatibility. | `button`, `device` |

