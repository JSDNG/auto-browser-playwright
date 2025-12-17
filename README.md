## CDP Tracking API – USPS + Playwright + FastAPI

FastAPI server dùng Playwright để kết nối tới Chrome đang chạy sẵn qua CDP và tự động kiểm tra trạng thái **USPS tracking** (đã delivered hay chưa) theo lô (batch).

> Lưu ý: Ngoài API USPS, repo hiện còn có script `src/app/cdp_connection.py` phục vụ việc thu thập dữ liệu HeyEtsy qua Chrome đã mở sẵn (CDP). Xem mục "HeyEtsy data capture" bên dưới để chạy nhanh.

### Tổng quan

- **Input**: Danh sách shipments với `shipment_id` và `tracking_link` (USPS URL).
- **Xử lý**: FastAPI gọi Playwright, kết nối Chrome qua CDP, mở từng link, đọc DOM và xác định delivered.
- **Output**: Danh sách kết quả dạng JSON:  
  `[{ "shipment_id": "...", "delivered": true|false, "delivered_at": "..." | null }, ...]`.

Chi tiết kiến trúc và luồng xử lý xem thêm trong `docs/implement.md` và `docs/tdd.md`.

### Yêu cầu hệ thống

- **Python**: 3.11+
- **Chrome**: Cài Chrome trên máy (dùng system Chrome, không dùng browser đi kèm Playwright).
- **CDP**: Chrome phải được khởi động với `--remote-debugging-port=9222`.

---

## Cách chạy server

### 1. Cài dependencies

```bash
pip install -r requirements.txt
```

Trên Windows bạn có thể dùng script:

```bat
scripts\setup_windows.bat
```

Script sẽ:

- Tạo virtualenv `venv`
- Cài dependencies từ `requirements.txt`
- Cài Playwright Chromium (`python -m playwright install chromium`)

### 2. Khởi động Chrome với CDP

Chọn một trong các lệnh tương ứng hệ điều hành (có thể tùy chỉnh path nếu Chrome ở vị trí khác):

- **macOS**:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

- **Linux**:

```bash
google-chrome --remote-debugging-port=9222
```

- **Windows** (ví dụ path mặc định):

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

Giữ cửa sổ Chrome này mở trong suốt quá trình gọi API.

### 3. Chạy FastAPI server (uvicorn)

Khuyến nghị dùng `uvicorn` để chạy app (cross‑platform).

- **Unix (macOS/Linux)**:

```bash
uvicorn src.app.api_server:app --reload --host 0.0.0.0
```

- **Windows (PowerShell / CMD, sau khi kích hoạt venv)**:

```bat
uvicorn src.app.api_server:app --reload --host 0.0.0.0
```

Hoặc bạn cũng có thể chạy trực tiếp file:

```bash
python src/app/api_server.py
```

Server sẽ chạy ở `http://localhost:5674`:

- **Swagger UI**: `http://localhost:5674/docs`
- **ReDoc**: `http://localhost:5674/redoc`

---

## HeyEtsy data capture (CDP script)

- **Mục đích**: Kết nối Chrome đã mở sẵn qua CDP, duyệt kết quả tìm kiếm Etsy và trích dữ liệu từ overlay HeyEtsy.
- **Chạy**:
  ```bash
  # keyword mặc định "t-shirt", pages mặc định 5
  python src/app/cdp_connection.py "<keyword>" <pages>
  ```
- **Cách làm**: Script dùng `PlaywrightAutomation.connect_over_cdp` → điều hướng từng trang tìm kiếm Etsy → đợi trang ổn định → `extract_heyetsy_data` (trong `src/utils/heyetsy_parser.py`) để lọc listing (bỏ video, yêu cầu `total_sold > 5`) → ghi kết quả duy nhất theo `listing_id` vào `captured_data.json` bằng `save_json` (trong `src/models/output.py`).
- **Yêu cầu**: Chrome đã bật `--remote-debugging-port=9222` và đang mở, giống phần chuẩn bị ở trên.

---

## Endpoint chính

### POST `/api/v1/cdp/auto-check-tracking`

**Mục đích**: Nhận danh sách USPS tracking links, trả về trạng thái delivered cho từng shipment.

**Request body (ví dụ)**:

```json
[
  {
    "shipment_id": "123",
    "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
  },
  {
    "shipment_id": "456",
    "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858308"
  }
]
```

**Response (ví dụ)**:

```json
[
  {
    "shipment_id": "123",
    "delivered": true,
    "delivered_at": "2025-12-13T05:01:00Z"
  },
  {
    "shipment_id": "456",
    "delivered": false,
    "delivered_at": null
  }
]
```

Các rule validate, logging, và luồng xử lý được mô tả chi tiết trong `docs/implement.md` và `docs/tdd.md`.

---

## Hỗ trợ chạy trên Windows

- **Event loop cho asyncio**:  
  Trong `src/app/api_server.py` có đoạn:

  - Nếu hệ điều hành là Windows, cấu hình lại event loop policy để tương thích với Playwright và FastAPI.

- **Setup nhanh**:
  - Chạy `scripts\setup_windows.bat` để tạo venv, cài dependencies và Playwright.
  - Khởi động Chrome với CDP như hướng dẫn ở trên.
  - Kích hoạt venv: `venv\Scripts\activate`.
  - Chạy server: `uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674`.

---

## Cấu trúc project (rút gọn)

```text
src/
├── app/
│   ├── __init__.py        # export FastAPI app
│   ├── api_server.py      # CDP Tracking API (FastAPI)
│   └── cdp_connection.py  # Hàm connect_to_chrome_via_cdp (dùng Playwright)
├── core/
│   ├── __init__.py        # export PlaywrightAutomation
│   └── automation.py      # Playwright wrapper: connect_over_cdp, navigate, detach
├── models/
│   ├── __init__.py        # export models & helpers dùng nội bộ
│   ├── input.py           # ViewportConfig, SearchInput (CLI)
│   └── output.py          # save_json helper
└── utils/
    └── heyetsy_parser.py  # extract_heyetsy_data helper
```

Các phần cũ liên quan tới n8n, Amazon search, Docker, test suite cũ... đã được loại bỏ khỏi code chính. Tài liệu chi tiết cho kiến trúc mới nằm trong thư mục `docs/`.
