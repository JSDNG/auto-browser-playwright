## CDP Tracking API – USPS + Playwright + FastAPI

FastAPI server dùng Playwright để kết nối tới Chrome đang chạy sẵn qua CDP và tự động kiểm tra trạng thái **USPS tracking** (đã delivered hay chưa) theo lô (batch).

> Lưu ý: Ngoài API USPS, repo hiện còn có script `src/app/cdp_connection.py` phục vụ việc kết nối Chrome qua CDP và mở URL (mặc định: https://grok.com/) để phục vụ các tác vụ như check TM trên Grok. Xem mục "Grok TM check (CDP script)" bên dưới để chạy nhanh.

### Tổng quan

- **Input**: Danh sách shipments với `shipment_id` và `tracking_link` (USPS URL).
- **Xử lý**: FastAPI gọi Playwright, kết nối Chrome qua CDP, mở từng link, đọc DOM và xác định delivered.
- **Output**: Danh sách kết quả dạng JSON:  
  `[{ "shipment_id": "...", "delivered": true|false, "delivered_at": "..." | null }, ...]`.

Chi tiết kiến trúc và luồng xử lý xem thêm trong `docs/implement.md` và `docs/tdd.md`.

### Yêu cầu hệ thống

- **Python**: 3.11+
- **Chrome**: Cài Chrome trên máy (dùng system Chrome, không dùng browser đi kèm Playwright).
- **CDP**: Chrome phải được khởi động với `--remote-debugging-port=9224`.

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
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224
```

- **Linux**:

```bash
google-chrome --remote-debugging-port=9224
```

- **Windows** (ví dụ path mặc định):

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9224 --user-data-dir="C:\temp\chrome-spy-etsy"
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

Server sẽ chạy ở `http://localhost:5675`:

- **Swagger UI**: `http://localhost:5675/docs`
- **ReDoc**: `http://localhost:5675/redoc`

---

## Grok TM check (CDP script)

- **Mục đích**: Kết nối Chrome đã mở sẵn qua CDP, điều hướng tới URL (mặc định: https://grok.com/) để thực hiện các thao tác check TM trên Grok bằng tay hoặc automation ở tầng cao hơn.
- **Chạy**:
  ```bash
  # Mặc định sẽ mở https://grok.com/
  python src/app/cdp_connection.py

  # Hoặc truyền URL khác nếu cần
  python src/app/cdp_connection.py "https://grok.com/"
  ```
- **Cách làm**: Script dùng `PlaywrightAutomation.connect_over_cdp` → điều hướng tới URL bạn cung cấp (mặc định là Grok) → giữ Chrome mở để bạn thao tác kiểm tra TM hoặc để các script khác tiếp tục làm việc.
- **Yêu cầu**: Chrome đã bật `--remote-debugging-port=9224` và đang mở, giống phần chuẩn bị ở trên.

---

## Hỗ trợ chạy trên Windows

- **Event loop cho asyncio**:  
  Trong `src/app/api_server.py` có đoạn:

  - Nếu hệ điều hành là Windows, cấu hình lại event loop policy để tương thích với Playwright và FastAPI.

- **Setup nhanh**:
  - Chạy `scripts\setup_windows.bat` để tạo venv, cài dependencies và Playwright.
  - Khởi động Chrome với CDP như hướng dẫn ở trên.
  - Kích hoạt venv: `venv\Scripts\activate`.
  - Chạy server: `uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5675`.

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
