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

### Phase 5: Dead Code Cleanup (2026-08-05) - ✅ COMPLETED

| Task ID | Task Description                                                                    | Status |
| ------- | ------------------------------------------------------------------------------------ | ------ |
| C5.1    | Xoá `config.py` (root) — generic automation config không còn dùng                    | ✅     |
| C5.2    | Xoá `AutomationInput`/`ActionConfig`/`ExtractConfig`, chỉ giữ `ViewportConfig`        | ✅     |
| C5.3    | Xoá `PlaywrightAutomation.launch()` / `launch_with_profile()` (không dùng trong luồng CDP) | ✅ |
| C5.4    | Xoá `src/gui/` (GUI app cũ, chỉ còn `__pycache__` mồ côi)                            | ✅     |
| C5.5    | Xoá `build.spec`, `build/`, `dist/` (build PyQt6 "EtsyCrawlerDragonMedia" cũ)         | ✅     |
| C5.6    | Xoá `scripts/test_cli.sh` (test CLI `src.cli` không còn tồn tại)                     | ✅     |
| C5.7    | Đồng bộ `.env` / `.env-example`, ghi chú rõ các biến hiện không được code đọc         | ✅     |
| C5.8    | Cập nhật `README.md`, `implement.md`, `tdd.md`, `API_GUIDE.md` khớp code mới          | ✅     |

### Phase 6: Env-based Config (2026-08-05) - ✅ COMPLETED

| Task ID | Task Description                                                                    | Status |
| ------- | ------------------------------------------------------------------------------------ | ------ |
| E6.1    | Dọn field cũ (n8n/generic-automation/DOLPHIN_API_TOKEN) khỏi `.env`/`.env-example`, thay bằng field thật sự dùng cho check tracking | ✅ |
| E6.2    | Viết lại `config.py` (root), dùng `python-dotenv` đọc `API_HOST`, `API_PORT`, `CDP_ENDPOINT`, `WAIT_TIME_SECONDS`, `REQUIRED_PHRASES` từ `.env`, fallback default nếu thiếu | ✅ |
| E6.3    | `api_server.py` và `cdp_connection.py` import config từ `config.py` thay vì hardcode `CONFIG_*`/`DEFAULT_*` | ✅ |
| E6.4    | Thêm `python-dotenv` vào `requirements.txt`                                          | ✅     |
| E6.5    | Cập nhật `README.md`, `implement.md`, `tdd.md` mô tả cơ chế config qua `.env`         | ✅     |

## 🏗️ Current Implementation Status

-   **Config**: `config.py` (root) — đọc từ `.env`, xem `.env-example`
-   **Server chính**: `src/app/api_server.py`
-   **CDP helper**: `src/app/cdp_connection.py`
-   **Core automation**: `src/core/automation.py` (`connect_over_cdp`, `navigate`, `wait_for_selector`, `close`, `detach`)
-   **Models**: `src/models/input.py` (`ViewportConfig`)

Toàn bộ phần cũ về n8n, Amazon search, `server_playwright.py`, `main.py`, `actions.py`, `extractor.py`, `output.py`, GUI app (PyQt6/PyInstaller), multi-profile/HideMyAcc automation, CLI cũ đã được loại bỏ và không còn áp dụng cho project hiện tại.
