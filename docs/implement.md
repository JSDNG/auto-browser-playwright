# Implementation Plan - CDP Tracking API (USPS) & HeyEtsy scraper

## 1. Kiến trúc hệ thống (rút gọn)

- **FastAPI (USPS)**: Nhận danh sách shipments, kết nối Chrome qua CDP, mở tracking link USPS và trả về trạng thái delivered.
- **CLI HeyEtsy scraper**: Script `src/app/cdp_connection.py` kết nối Chrome qua CDP, duyệt kết quả tìm kiếm Etsy, trích overlay HeyEtsy và lưu vào `captured_data.json`.

Sơ đồ đơn giản:

```
Client/CLI ──▶ PlaywrightAutomation ──▶ Chrome (CDP) ──▶ Target page
```

## 2. Các thành phần chính

- `src/app/api_server.py`: FastAPI app, định nghĩa endpoint `POST /api/v1/cdp/auto-check-tracking`
- `src/app/cdp_connection.py`: CLI/CDP helper để scrape HeyEtsy
- `src/core/automation.py`: Lớp `PlaywrightAutomation` với method `connect_over_cdp`
- `src/models/input.py`: Các Pydantic models dùng nội bộ cho automation (viewport, timeout, ...)

## 3. Project structure (hiện tại)

```
src/
├── app/
│   ├── __init__.py        # export FastAPI app
│   ├── api_server.py      # CDP Tracking API (USPS)
│   └── cdp_connection.py  # CDP helper / HeyEtsy scraper
├── core/
│   ├── __init__.py        # export PlaywrightAutomation
│   └── automation.py      # Playwright wrapper
├── models/
│   ├── __init__.py        # export ViewportConfig, SearchInput, save_json
│   ├── input.py           # ViewportConfig, SearchInput (CLI)
│   └── output.py          # save_json helper
└── utils/
    └── heyetsy_parser.py  # extract_heyetsy_data helper
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
   - Gọi `connect_to_chrome_via_cdp(url=tracking_link, cdp_endpoint="http://localhost:9224", wait_time=2)`
   - Đọc kết quả `{ success, is_delivered, delivered_date, ... }`
   - Chuẩn hóa về `ShipmentTrackingResponse` `{ shipment_id, delivered, delivered_at }`
4. Trả về danh sách kết quả theo đúng thứ tự input.

Chi tiết request/response và ví dụ gọi đã được mô tả đầy đủ trong `API_GUIDE.md`.

## 5. Kết nối CDP (tóm tắt)

- Chrome phải được khởi động với `--remote-debugging-port=9224`
- `PlaywrightAutomation.connect_over_cdp` nhận endpoint (ví dụ `http://localhost:9224`), tạo `browser`, `context`, `page`
- `connect_to_chrome_via_cdp` dùng `PlaywrightAutomation` để:
  - Điều hướng tới URL
  - Chờ trang load
  - Đọc `document.body.innerText` để kiểm tra các cụm từ delivered
  - Tìm element `.delivered-status .tb-date` để lấy thời gian delivered nếu có

Chi tiết hơn xem `CDP_CONNECTION.md` và code trong `src/app/cdp_connection.py`.

## 6. HeyEtsy scraper (src/app/cdp_connection.py)

- Nhận `keyword` (mặc định "t-shirt") và `pages` (mặc định 5) từ CLI.
- Kết nối Chrome đang chạy qua CDP (`PlaywrightAutomation.connect_over_cdp`).
- Điều hướng từng trang tìm kiếm Etsy, đợi trang ổn định.
- Dùng `extract_heyetsy_data` (trong `src/utils/heyetsy_parser.py`) để trích overlay HeyEtsy, bỏ video và bỏ listing có `total_sold <= 5`.
- Gộp kết quả duy nhất theo `listing_id` và lưu vào `captured_data.json` bằng `save_json` (trong `src/models/output.py`).

## 7. Ghi chú refactor

Toàn bộ phần cũ liên quan tới n8n, Amazon search, `server_playwright.py`, `main.py`, `actions.py`, `extractor.py` đã được loại bỏ khỏi code và tài liệu; file này chỉ mô tả kiến trúc và luồng xử lý hiện tại (USPS API + HeyEtsy scraper).
