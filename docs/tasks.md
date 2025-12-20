# Tasks - CDP Tracking API (USPS)

## 🎯 Project Overview

Xây dựng FastAPI server với Playwright để:

-   **CDP Connection**: Kết nối Chrome đang chạy qua CDP
-   **USPS Tracking**: Tự động mở tracking links USPS và kiểm tra trạng thái delivered
-   **Batch Processing**: Nhận danh sách shipments và trả về kết quả tương ứng
-   **Simple JSON Output**: Trả về `{ shipment_id, delivered, delivered_at }` cho từng shipment

## 📋 Task List

### Phase 1: Server Foundation - ✅ COMPLETED

| Task ID | Task Description                         | Status |
| ------- | ---------------------------------------- | ------ |
| T1.1    | Setup FastAPI server structure           | ✅     |
| T1.2    | Tạo basic endpoints (health, root)       | ✅     |
| T1.3    | Thêm FastAPI, uvicorn, playwright vào requirements | ✅ |

### Phase 2: CDP & USPS Logic - ✅ COMPLETED

| Task ID | Task Description                                      | Status |
| ------- | ----------------------------------------------------- | ------ |
| T2.1    | Implement `PlaywrightAutomation.connect_over_cdp`     | ✅     |
| T2.2    | Implement `connect_to_chrome_via_cdp`                 | ✅     |
| T2.3    | Đọc body USPS, check cụm từ delivered                 | ✅     |
| T2.4    | Extract `delivered_date` từ `.delivered-status .tb-date` | ✅  |

### Phase 3: API Endpoint - ✅ COMPLETED

| Task ID | Task Description                                      | Status |
| ------- | ----------------------------------------------------- | ------ |
| T3.1    | Tạo models `ShipmentItem`, `ShipmentTrackingResponse` | ✅     |
| T3.2    | Implement `POST /api/v1/cdp/auto-check-tracking`     | ✅     |
| T3.3    | Validate input (shipment_id, tracking_link)          | ✅     |
| T3.4    | Log chi tiết từng shipment                           | ✅     |

### Phase 4: Documentation - ✅ COMPLETED

| Task ID | Task Description                             | Status |
| ------- | -------------------------------------------- | ------ |
| D4.1    | Viết `API_GUIDE.md`                          | ✅     |
| D4.2    | Viết `CDP_CONNECTION.md`                     | ✅     |
| D4.3    | Cập nhật `README.md` đúng kiến trúc mới      | ✅     |

## 🏗️ Current Implementation Status

-   **Server chính**: `src/app/api_server.py`
-   **CDP helper / HeyEtsy scraper**: `src/app/cdp_connection.py` (kết nối Chrome qua CDP, duyệt Etsy, lưu `captured_data.json`)
-   **Core automation**: `src/core/automation.py`
-   **Models & helpers**: `src/models/input.py`, `src/models/output.py`
-   **Etsy parser helper**: `src/utils/heyetsy_parser.py`

Toàn bộ phần cũ về n8n, Amazon search, `server_playwright.py`, `main.py`, `actions.py`, `extractor.py` đã được loại bỏ và không còn áp dụng cho project hiện tại.
