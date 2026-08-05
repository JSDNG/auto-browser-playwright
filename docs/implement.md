# Implementation Plan - CDP Tracking API (USPS)

## 1. Kiến trúc hệ thống (rút gọn)

FastAPI server nhỏ, chỉ tập trung vào một use case:

- Nhận danh sách shipments (ID + USPS tracking link)
- Kết nối Chrome đang chạy sẵn qua CDP
- Mở từng tracking link, đọc DOM
- Xác định shipment đã delivered hay chưa, và nếu có thì lấy thời gian delivered

Sơ đồ đơn giản:

```
Client ──▶ FastAPI (`api_server.py`) ──▶ Chrome (CDP) ──▶ USPS Tracking Page
```

## 2. Các thành phần chính

- `config.py` (root): đọc `API_HOST`, `API_PORT`, `CDP_ENDPOINT`, `WAIT_TIME_SECONDS`, `REQUIRED_PHRASES` từ `.env` (dùng `python-dotenv`), fallback về giá trị mặc định nếu thiếu
- `src/app/api_server.py`: FastAPI app, định nghĩa endpoint `POST /api/v1/cdp/auto-check-tracking`, dùng config từ `config.py`
- `src/app/cdp_connection.py`: Hàm `connect_to_chrome_via_cdp` dùng Playwright để nói chuyện với Chrome qua CDP, dùng config từ `config.py`
- `src/core/automation.py`: Lớp `PlaywrightAutomation` với method `connect_over_cdp` (attach vào Chrome đang chạy sẵn), `navigate`, `wait_for_selector`, `close`, `detach`
- `src/models/input.py`: `ViewportConfig` — Pydantic model duy nhất còn dùng, cấu hình viewport mặc định cho browser context

## 3. Project structure (hiện tại)

```
config.py                  # Đọc config từ .env
.env-example                # Template cho .env
src/
├── app/
│   ├── __init__.py        # export FastAPI app
│   ├── api_server.py      # CDP Tracking API
│   └── cdp_connection.py  # CDP helper
├── core/
│   ├── __init__.py        # export PlaywrightAutomation
│   └── automation.py      # Playwright wrapper (connect_over_cdp, navigate, ...)
├── models/
│   ├── __init__.py        # export ViewportConfig
│   └── input.py           # ViewportConfig
└── utils/
    └── __init__.py        # (trống, để dành cho tương lai)
```

## 4. Luồng xử lý endpoint chính

### 4.1. Endpoint `POST /api/v1/cdp/auto-check-tracking`

1. Nhận body là mảng `ShipmentItem`:
   - `shipment_id`: int hoặc string
   - `tracking_link`: USPS tracking URL
2. Validate:
   - Mảng không rỗng
   - `shipment_id` không null / rỗng
   - `tracking_link` không rỗng
3. Với từng shipment:
   - Gọi `connect_to_chrome_via_cdp(url=tracking_link, cdp_endpoint="http://localhost:9222", wait_time=2)`
   - Đọc kết quả `{ success, is_delivered, delivered_date, ... }`
   - Chuẩn hóa về `ShipmentTrackingResponse` `{ shipment_id, delivered, delivered_at }`
4. Trả về danh sách kết quả theo đúng thứ tự input.

Chi tiết request/response và ví dụ gọi đã được mô tả đầy đủ trong `API_GUIDE.md`.

## 5. Kết nối CDP (tóm tắt)

- Chrome phải được khởi động với `--remote-debugging-port=9222`
- `PlaywrightAutomation.connect_over_cdp` nhận endpoint (ví dụ `http://localhost:9222`), tạo `browser`, `context`, `page`
- `connect_to_chrome_via_cdp` dùng `PlaywrightAutomation` để:
  - Điều hướng tới URL
  - Chờ trang load
  - Đọc `document.body.innerText` để kiểm tra các cụm từ delivered
  - Tìm element `.delivered-status .tb-date` để lấy thời gian delivered nếu có

Chi tiết hơn xem `CDP_CONNECTION.md` và code trong `src/app/cdp_connection.py`.

## 6. Ghi chú refactor

Toàn bộ phần cũ liên quan tới:

- `server_playwright.py`, `main.py`
- `actions.py`, `extractor.py`
- `models/output.py` (AutomationOutput, ErrorResponse)
- n8n workflows, Amazon product search, browser session management
- Generic automation models (`AutomationInput`, `ActionConfig`, `ExtractConfig`) — không còn dùng, đã xoá (`config.py` root sau đó được viết lại để đọc config CDP/tracking từ `.env`, xem mục 2)
- `PlaywrightAutomation.launch()` / `launch_with_profile()` (multi-profile, proxy, HideMyAcc/Marco browser) — không còn được gọi trong luồng CDP hiện tại, đã xoá; chỉ giữ `connect_over_cdp()`
- GUI app (PyQt6) và `build.spec` (PyInstaller) — sản phẩm cũ "EtsyCrawlerDragonMedia", không liên quan tới CDP Tracking API, đã xoá cùng `src/gui/` và artifact `build/`, `dist/`
- `scripts/test_cli.sh` — test cho CLI cũ (`python -m src.cli`) không còn tồn tại, đã xoá

đã được loại bỏ khỏi code và tài liệu; file này chỉ mô tả kiến trúc và luồng xử lý cho CDP Tracking API hiện tại.
