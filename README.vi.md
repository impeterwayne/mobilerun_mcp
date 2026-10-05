# Mobilerun MCP

*[English](README.md) · **Tiếng Việt***

Model Context Protocol (MCP) server chạy trên máy host giúp các AI client điều khiển trực tiếp điện thoại Android (máy thật, giả lập, redroid) qua ADB và iOS qua ios-portal. Server tập trung vào việc tự động hóa thiết bị, đọc màn hình, thực hiện thao tác vuốt chạm, quản lý ứng dụng và system intent — toàn bộ tác vụ xử lý nặng đều nằm trên máy host, không đòi hỏi thư viện ARM riêng biệt trên thiết bị.

Repo gồm hai phần hoạt động cùng nhau:

- MCP server cung cấp 94 tool qua stdio hoặc HTTP
- Dịch vụ trợ năng [Mobilerun Portal](https://github.com/droidrun/mobilerun-portal) chạy trên thiết bị Android

## Tính năng nổi bật

- Kiến trúc Host-side: không phụ thuộc vào native ARM trên máy; tương thích hoàn hảo với máy thật, giả lập x86_64 và container redroid
- Chạy trực tiếp không cần cài đặt phức tạp qua `npx`, tự động khởi tạo môi trường Python và cài đặt thư viện phụ thuộc
- 94 tool hỗ trợ nhận diện màn hình, thao tác cử chỉ, ứng dụng, intent, thông báo, media và điều khiển thiết bị
- Nhận diện trực quan Set-of-Mark (SoM) với nhãn đánh số (`som_id`), cây trợ năng (accessibility tree) và OCR (Tesseract / OmniParser v2)
- Vòng lặp xác minh tích hợp: mọi tool thay đổi trạng thái đều chờ màn hình ổn định và trả về `post_action_observation`
- Tương thích trực tiếp với Device API của `mobilerun-core` để lập trình kịch bản tự động hóa
- Hoạt động qua mọi kết nối mạng mà ADB hỗ trợ (USB, Wi-Fi, LAN, VPN, `adb connect`)
- Tích hợp sẵn chính sách an toàn linh hoạt (`off`, `standard`, `strict`) giúp bảo vệ dữ liệu nhạy cảm và thông tin cá nhân

## Yêu cầu

- Node.js `>=18` (để chạy trực tiếp qua `npx`)
- `adb` (Android Debug Bridge, đi kèm trong [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools))
- Thiết bị Android hoặc máy giả lập đã bật USB debugging
- Python `3.10+` (tuỳ chọn, chỉ cần khi muốn phát triển mã nguồn trực tiếp)
- Tesseract OCR (tuỳ chọn, dùng cho OCR trên các màn hình có cây trợ năng thưa)

## Cài đặt và thiết lập

### 1. Cấu hình AI client

#### Claude Code / Claude Desktop / VS Code / Cursor / Antigravity

Nội dung cấu hình giống nhau trên mọi client, chỉ khác đường dẫn file:

- Claude Code — `.mcp.json` ở thư mục gốc của project
- Claude Desktop — `claude_desktop_config.json`
- Cursor — `.cursor/mcp.json`
- VS Code — `.vscode/mcp.json` (VS Code dùng key ngoài cùng là `servers` thay vì `mcpServers`)
- Antigravity — mở bảng cài đặt MCP (MCP Store -> **View raw config**), tương ứng file `~/.gemini/config/mcp_config.json`, hoặc `.agents/mcp_config.json` cho từng workspace

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

Hoặc thêm nhanh qua Claude Code CLI:
```bash
claude mcp add --scope user mobilerun -e MOBILERUN_DEVICE=<serial> -- npx -y @impeterwayne/mobilerun-mcp@latest
```

> **Lưu ý:** `MOBILERUN_DEVICE` là tuỳ chọn nếu chỉ có duy nhất một thiết bị đang kết nối ADB.

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

### 2. Thiết lập thiết bị và cài đặt Portal

Tải và cài đặt file **[Mobilerun Portal APK](https://github.com/droidrun/mobilerun-portal/releases)** trên thiết bị Android của bạn:

```bash
adb install -r <portal.apk>
```

Sau đó kích hoạt dịch vụ trợ năng **Mobilerun Portal** trong **Cài đặt > Hỗ trợ tiếp cận (Accessibility)**.

<details>
<summary>Cài đặt thủ công bằng Python / mã nguồn</summary>

```bash
git clone https://github.com/Hi-im-Connect/mobilerun-mcp.git && cd mobilerun-mcp
uv venv --python 3.13 .venv && uv pip install -e .
```
Trên Windows, sử dụng `.venv\Scripts\python.exe` thay vì `.venv/bin/python`.

Cấu hình trong AI client:
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

## Danh sách tool

94 tool bao quát toàn bộ thao tác màn hình, cử chỉ, điều khiển hệ thống, thông báo, media và tự động hóa.

### Nhận diện và đọc màn hình

| Tool | Chức năng |
|------|-----------|
| `perceive_screen` | Chụp ảnh màn hình có đánh số các phần tử (`som_id`) và danh sách phần tử tương tác được. |
| `read_screen` | Biểu diễn giao diện dạng bảng ký tự text/ASCII (chờ màn hình ổn định trước khi đọc). |
| `get_ui_tree` | Cây phân cấp trợ năng thu gọn (class, ID tài nguyên, nhãn, cờ, toạ độ khung). |
| `get_screenshot` | Trả về ảnh chụp màn hình hiện tại dưới dạng dữ liệu base64. |
| `screenshot` | Chụp ảnh màn hình với tuỳ chọn ẩn overlay. |
| `screenshot_path` | Chụp ảnh màn hình, lưu thành file PNG trên ổ cứng và trả về đường dẫn file. |

### Cử chỉ, nhập liệu và phím cứng

| Tool | Chức năng |
|------|-----------|
| `tap` | Chạm vào toạ độ `(x, y)` hoặc vào phần tử được đánh số (`som_id`). |
| `double_tap` | Chạm đúp vào toạ độ `(x, y)` hoặc phần tử `som_id`. |
| `long_press` | Nhấn giữ tại toạ độ `(x, y)` hoặc phần tử `som_id` với thời gian tuỳ chỉnh. |
| `long_press_at` | Nhấn giữ tại toạ độ `(x, y)` chính xác. |
| `swipe` | Vuốt giữa hai điểm `(x1, y1)` đến `(x2, y2)` với thời gian chỉ định. |
| `scroll_down` | Cuộn màn hình xuống dưới (để hiển thị nội dung bên dưới). |
| `scroll_up` | Cuộn màn hình lên trên (để hiển thị nội dung bên trên). |
| `scroll_left` | Cuộn màn hình sang trái. |
| `scroll_right` | Cuộn màn hình sang phải. |
| `scroll` | Cuộn theo hướng chỉ định theo tỉ lệ màn hình. |
| `scroll_to` | Cuộn cho tới khi văn bản hoặc toạ độ mục tiêu xuất hiện. |
| `type_text` | Nhập văn bản vào ô nhập liệu đang focus hoặc theo `som_id`. |
| `type` | Gõ văn bản với tuỳ chọn tốc độ gõ (WPM) và xoá trước khi gõ. |
| `clear_input` | Xoá toàn bộ nội dung trong ô nhập liệu đang focus. |
| `press_home` | Nhấn nút Home vật lý/ảo. |
| `press_back` | Nhấn nút Back (hỗ trợ đóng bàn phím và popup). |
| `press_enter` | Nhấn phím Enter / Search / Gửi. |
| `open_recent_apps` | Mở màn hình chuyển đổi ứng dụng gần đây. |
| `key` | Gửi mã phím phần cứng hoặc tên phím (`back`, `home`, `volume_up`, `wakeup`, v.v.). |
| `press` | Helper bấm phím phiên bản cũ (`home`, `back`, `enter`). |

### Ứng dụng và deep link

| Tool | Chức năng |
|------|-----------|
| `launch_app` | Mở ứng dụng theo tên tìm kiếm gần đúng hoặc package name chính xác. |
| `start_app` | Khởi chạy ứng dụng theo package ID và activity chỉ định. |
| `lookup_app` | Tìm kiếm ứng dụng đã cài đặt theo tên hoặc package, trả về danh sách xếp hạng. |
| `list_apps` | Liệt kê các ứng dụng đã cài đặt trên máy. |
| `list_app_deeplinks` | Khám phá các deep link và phím tắt hỗ trợ trong ứng dụng. |
| `resolve_deeplink` | Kiểm tra ứng dụng nào sẽ xử lý URI hoặc intent action cho trước. |
| `open_deeplink` | Mở trực tiếp màn hình qua URI, phím tắt hoặc intent action. |

### System intent, danh bạ, tệp tin và media

| Tool | Chức năng |
|------|-----------|
| `system_intent` | Thực hiện các intent Android phổ biến (đặt báo thức, dẫn đường, gọi điện, mở web). |
| `resolve_contact` | Tìm kiếm danh bạ theo tên và trả về số điện thoại. |
| `find_files` | Tìm kiếm tệp tin trong bộ nhớ (tải về, ảnh, tài liệu, video). |
| `open_file` | Mở tệp tin trên thiết bị bằng ứng dụng mặc định. |
| `get_media_sessions` | Lấy thông tin phiên phát media đang hoạt động, thông tin bài hát và âm lượng. |
| `media_control` | Điều khiển phát nhạc/video (play, pause, next, previous, stop, rewind, tua nhanh). |
| `volume_up` | Tăng âm lượng media. |
| `volume_down` | Giảm âm lượng media. |
| `mute` | Bật/tắt chế độ tắt tiếng media. |

### Thông báo (Notifications)

| Tool | Chức năng |
|------|-----------|
| `read_notifications` | Đọc các thông báo trên thanh trạng thái kèm tiêu đề, nội dung và nút bấm hành động. |
| `dismiss_notification` | Đóng một thông báo cụ thể hoặc đóng toàn bộ thông báo cho phép xoá. |
| `notification_action` | Nhấn nút hành động trên thông báo hoặc gửi phản hồi trực tiếp (inline reply). |

### Device API của mobilerun-core

| Tool | Chức năng |
|------|-----------|
| `ui` | Trích xuất toàn bộ ảnh chụp trạng thái UI (`a11y_tree`, phone state, device context). |
| `ui_json` | Chuỗi JSON đã serialize của cây phân cấp UI thiết bị. |
| `ui_with_recovery` | Trích xuất UI kèm logic tự động thử lại khi cây trợ năng bị tải lại hoặc trống. |
| `capabilities` | Truy vấn các khả năng backend, hành động và nền tảng được hỗ trợ. |
| `supports` | Kiểm tra thiết bị mục tiêu có hỗ trợ hành động cụ thể hay không. |
| `screen_size` | Trả về độ phân giải màn hình (chiều rộng, chiều cao tính theo pixel). |
| `current_app_id` | Package name của ứng dụng đang chạy ở foreground. |
| `time` | Thời gian hệ thống hiện tại của thiết bị. |
| `find_nodes` | Tìm các node thoả mãn bộ lọc (text, ID, class, chứa chuỗi), bao gồm cả ngoài màn hình. |
| `find_nodes_on_screen` | Tìm các node thoả mãn bộ lọc hiển thị trong phạm vi màn hình. |
| `tap_text` | Tìm và chạm vào node đầu tiên trên màn hình có chứa văn bản chỉ định. |
| `tap_node` | Chạm vào tâm của đối tượng node trả về từ `find_nodes`. |
| `tap_and_wait` | Chạm vào phần tử mục tiêu và chờ cho UI hoàn tất chuyển động. |
| `scroll_until` | Cuộn liên tục cho tới khi phần tử thoả điều kiện xuất hiện trên màn hình. |
| `assert_on` | Kiểm tra ứng dụng chỉ định có đang chạy ở foreground hay không. |
| `assert_text_visible` | Kiểm tra văn bản kỳ vọng có xuất hiện trên màn hình trong thời gian chờ. |
| `wait_for_app` | Chờ cho tới khi ứng dụng chỉ định mở lên foreground. |
| `wait_for_idle` | Chờ hoạt ảnh và thay đổi UI dừng lại hoàn toàn. |
| `wait_for_screen_change` | Chờ cho tới khi UI có sự thay đổi so với trạng thái hiện tại. |
| `wait_for_text` | Chờ cho tới khi xuất hiện node chứa văn bản chỉ định. |
| `wait_for_nodes` | Lặp lại kiểm tra cho tới khi tìm thấy node khớp bộ lọc. |
| `open_and_settle` | Mở ứng dụng và chờ cho tới khi tải xong hoàn toàn và ổn định. |
| `stop_app` | Buộc dừng ứng dụng (force-stop) kèm tuỳ chọn xoá dữ liệu. |
| `install_app` | Cài đặt file APK từ máy host vào thiết bị. |
| `uninstall_app` | Gỡ cài đặt ứng dụng. |
| `grant_permission` | Cấp quyền runtime (`android.permission.*`) cho ứng dụng. |
| `open_deep_link` | Gửi deep link hoặc view intent gắn với một package. |
| `execute_script` | Thực thi mã JavaScript trong trang trình duyệt đang mở ở foreground. |
| `get_clipboard` | Đọc nội dung văn bản hiện tại trong clipboard thiết bị. |
| `set_clipboard` | Ghi nội dung văn bản vào clipboard thiết bị. |

### Quản lý thiết bị và kết nối

| Tool | Chức năng |
|------|-----------|
| `get_device_status` | Trạng thái toàn diện: pin, màn hình, ứng dụng foreground, dung lượng, IP. |
| `list_devices` | Liệt kê các thiết bị ADB và máy giả lập đang kết nối. |
| `ping_device` | Kiểm tra độ trễ và khả năng kết nối tới thiết bị cùng dịch vụ Portal. |
| `connect_device` | Kết nối lại ADB và Portal cho thiết bị mục tiêu. |
| `disconnect_device` | Ngắt kết nối thiết bị ADB qua mạng (TCP) và dọn dẹp phiên. |
| `setup_portal` | Cài đặt và khởi chạy dịch vụ Mobilerun Portal trên thiết bị. |
| `doctor` | Chẩn đoán sức khoẻ tổng thể giữa ADB, uỷ quyền thiết bị và Portal. |
| `request_screen_capture_permission` | Kiểm tra tính tương thích của quyền chụp màn hình. |
| `echo` | Phản hồi thông điệp để kiểm tra đường truyền MCP hoạt động tốt. |
| `adb` | Chạy lệnh ADB trực tiếp (mặc định tắt; cần bật `MOBILERUN_MCP_ENABLE_ADB=1`). |

### Lập kế hoạch, xác minh và nghiên cứu

| Tool | Chức năng |
|------|-----------|
| `verify_action` | Xác minh kết quả sau thao tác dựa trên văn bản hoặc trạng thái UI kỳ vọng. |
| `validate_action` | Kiểm tra trước tính hợp lệ của hành động theo chính sách an toàn trước khi chạy. |
| `wait_for` | Chờ các thao tác kéo dài (tải tệp, đồng bộ, xử lý dữ liệu nặng). |
| `watch_device_events` | Theo dõi sự kiện hệ thống (chuyển đổi ứng dụng, thông báo, bàn phím). |
| `web_search` | Tìm kiếm hướng dẫn thao tác ứng dụng trên web. |
| `set_plan` | Khởi tạo danh sách các bước thực hiện cùng mục tiêu và kết quả kỳ vọng. |
| `mark_step` | Cập nhật tiến độ bước (`pending`, `in_progress`, `done`, `failed`). |
| `record_finding` | Ghi lại phát hiện và bằng chứng quan trọng thu thập được trong quá trình chạy. |
| `end_session` | Kết thúc phiên tự động hóa và tổng kết báo cáo kết quả. |
| `get_usage_guide` | Hướng dẫn thực hành tốt nhất khi điều khiển thiết bị di động. |

## Cấu hình

| Biến môi trường | Mặc định | Ý nghĩa |
|-----------------|----------|---------|
| `MOBILERUN_DEVICE` | Thiết bị đầu tiên kết nối | Serial ADB mục tiêu, địa chỉ mạng (`host:port`), hoặc `ios` |
| `MOBILERUN_MCP_POLICY` | `off` | Chính sách an toàn: `off`, `standard` (chặn app tài chính/auth), `strict` (chặn mật khẩu/PIN) |
| `MOBILERUN_MCP_SCOPES` | `read,write` | Giới hạn quyền tool (`read` chỉ mở các tool đọc dữ liệu) |
| `MOBILERUN_MCP_ENABLE_ADB` | `0` | Đặt thành `1` để mở tool thực thi lệnh `adb` trực tiếp |
| `BRAVE_API_KEY` | Chưa đặt | API key cho Brave search khi dùng `web_search` (mặc định là DuckDuckGo) |
| `TAVILY_API_KEY` | Chưa đặt | API key cho Tavily search khi dùng `web_search` |
| `MOBILERUN_DETECTOR_MODEL` | Tự động tải | Đường dẫn override file model ONNX nhận diện icon OmniParser |
| `MOBILERUN_MCP_HTTP_HOST` | `127.0.0.1` | Địa chỉ host khi chạy MCP dạng HTTP (`--http`) |
| `MOBILERUN_MCP_HTTP_PORT` | `4816` | Cổng khi chạy MCP dạng HTTP (`--http`) |
| `MOBILERUN_ADB_BIN` | `adb` trong PATH | Đường dẫn tuỳ chỉnh tới file thực thi `adb` |

## Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| `[device_unreachable] no device selected` | Chạy `adb devices`, sau đó cấu hình `MOBILERUN_DEVICE=<serial>` trong client |
| `adb devices` hiển thị `unauthorized` | Mở khoá điện thoại và nhấn **Cho phép** (Allow) ở hộp thoại USB debugging |
| `adb devices` trống hoặc `offline` | Cắm lại cáp USB hoặc chạy `adb connect <host>:<port>` cho thiết bị qua mạng |
| `adb: command not found` | Cài đặt platform-tools hoặc cấu hình đường dẫn với `MOBILERUN_ADB_BIN` |
| `Mobilerun Portal is not enabled` | Bật trong **Cài đặt > Hỗ trợ tiếp cận > Mobilerun Portal**, hoặc chạy `mobilerun setup -d <serial>` |
| Lỗi `[stale_som_id]` | Màn hình đã thay đổi sau thao tác trước; gọi `perceive_screen` hoặc `read_screen` để làm mới ID |
| Client không thấy danh sách tool `mobilerun` | Kiểm tra lại cú pháp file cấu hình và đường dẫn; khởi động lại AI client |

## Giấy phép

MIT. Xem [LICENSE](LICENSE) và [NOTICE](NOTICE).
