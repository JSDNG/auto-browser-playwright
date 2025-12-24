# Implementation Plan - Grok Video Generation API

## 1. Kiến trúc hệ thống (rút gọn)

- **FastAPI (Grok)**: Nhận text prompt, launch Chrome (hoặc kết nối qua CDP), navigate đến Grok Imagine và nhập prompt để gen video.
- **CLI Grok Video Generator**: Script `src/app/cdp_connection.py` kết nối Chrome qua CDP, navigate đến Grok Imagine và nhập prompt để gen video.

Sơ đồ đơn giản:

```
Client/CLI ──▶ PlaywrightAutomation ──▶ Chrome (CDP/Direct) ──▶ Grok Imagine
```

## 2. Các thành phần chính

- `src/app/api_server.py`: FastAPI app, định nghĩa endpoint `POST /api/v1/grok/launch`
- `src/app/cdp_connection.py`: CLI/CDP helper để gen video với Grok
- `src/core/automation.py`: Lớp `PlaywrightAutomation` với method `connect_over_cdp` và `launch`
- `src/models/input.py`: Các Pydantic models dùng nội bộ cho automation (GrokInput, ViewportConfig)

## 3. Project structure (hiện tại)

```
src/
├── app/
│   ├── __init__.py        # export FastAPI app
│   ├── api_server.py      # Grok Video Generation API
│   └── cdp_connection.py  # CDP helper / Grok video generator
├── core/
│   ├── __init__.py        # export PlaywrightAutomation
│   └── automation.py      # Playwright wrapper
├── models/
│   ├── __init__.py        # export ViewportConfig, GrokInput, save_json
│   ├── input.py           # ViewportConfig, GrokInput
│   └── output.py          # save_json helper
└── utils/
    └── (utility helpers)
```

## 4. Luồng xử lý endpoint chính

### 4.1. Endpoint `POST /api/v1/grok/launch`

1. Nhận body là `GrokInput`:
   - `text`: string (required) - Prompt text để tạo video
2. Validate:
   - `text` không được để trống
3. Gọi `grok_gen_video_direct(text)` từ `cdp_connection.py`:
   - Launch Chrome trực tiếp (không qua CDP)
   - Navigate đến `https://grok.com/imagine`
   - Chờ 5 giây để trang load
   - Tìm và click vào element cụ thể
   - Đợi 2 giây
   - Tìm input field và nhập prompt text
   - Detach automation (giữ browser mở)
4. Trả về kết quả `GrokLaunchResponse` với `{ success, message, url, error }`

Chi tiết request/response và ví dụ gọi đã được mô tả đầy đủ trong `API_GUIDE.md`.

## 5. Kết nối CDP (tóm tắt)

- Chrome có thể được khởi động với `--remote-debugging-port=9224` (tùy chọn, cho CLI)
- `PlaywrightAutomation.connect_over_cdp` nhận endpoint (ví dụ `http://localhost:9224`), tạo `browser`, `context`, `page`
- `grok_gen_video_via_cdp` dùng `PlaywrightAutomation` để:
  - Kết nối với Chrome đang chạy qua CDP
  - Navigate đến `https://grok.com/imagine`
  - Thực hiện các bước tương tự như direct launch

Chi tiết hơn xem `CDP_CONNECTION.md` và code trong `src/app/cdp_connection.py`.

## 6. Grok Video Generation (src/app/cdp_connection.py)

### 6.1. Direct Launch (khuyến nghị)

- Nhận `text` prompt từ CLI hoặc API
- Launch Chrome trực tiếp (`PlaywrightAutomation.launch`)
- Navigate đến `https://grok.com/imagine`
- Chờ trang load (5 giây)
- Tìm và click vào element cụ thể (input field wrapper)
- Đợi 2 giây sau khi click
- Tìm input field (textarea hoặc contenteditable)
- Nhập prompt text vào input field
- Giữ browser mở để tiếp tục sử dụng

### 6.2. CDP Connection (tùy chọn)

- Yêu cầu Chrome đã chạy với `--remote-debugging-port=9224`
- Kết nối với Chrome qua CDP (`PlaywrightAutomation.connect_over_cdp`)
- Thực hiện các bước tương tự như Direct Launch

## 7. Helper Function

### `_grok_imagine_interact(automation, text, logger=None)`

Helper function xử lý logic chính:
- Navigate đến Grok Imagine
- Chờ trang load (5 giây)
- Tìm và click element cụ thể
- Đợi 2 giây
- Tìm và nhập text vào input field

Được sử dụng bởi cả `grok_gen_video_via_cdp` và `grok_gen_video_direct`.

## 8. Ghi chú refactor

Toàn bộ phần cũ liên quan tới n8n, Amazon search, Etsy scraping, USPS tracking, `server_playwright.py`, `main.py`, `actions.py`, `extractor.py` đã được loại bỏ khỏi code và tài liệu; file này chỉ mô tả kiến trúc và luồng xử lý hiện tại (Grok Video Generation).
