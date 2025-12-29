## SpyEtsy – Etsy Product Spy Tool

FastAPI server dùng Playwright để kết nối tới Chrome đang chạy sẵn qua CDP và tự động spy dữ liệu sản phẩm từ **Etsy** bằng extension **HeyEtsy**.

### Tổng quan

- **Input**: Từ khóa tìm kiếm (`keyword`) và số trang (`pages`) cần spy.
- **Xử lý**: FastAPI gọi Playwright, kết nối Chrome qua CDP, duyệt từng trang tìm kiếm Etsy, trích xuất dữ liệu từ overlay HeyEtsy.
- **Output**: Dữ liệu sản phẩm (listing_id, title, image, views, sold, favorites, created date...) được gửi tới webhook `https://spyetsy.supover.com/webhook`.

Chi tiết kiến trúc và API endpoints xem thêm trong `docs/ETSY_SPY_API.md`.

### Yêu cầu hệ thống

- **Python**: 3.11+
- **Chrome**: Cài Chrome trên máy (dùng system Chrome, không dùng browser đi kèm Playwright).
- **Extension HeyEtsy**: Cần cài đặt extension HeyEtsy trong Chrome profile để hiển thị dữ liệu sản phẩm trên trang Etsy.
- **CDP**: Chrome phải được khởi động với `--remote-debugging-port=9223`.

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

**Lưu ý**: Chrome cần có extension **HeyEtsy** đã được cài đặt.

Chọn một trong các lệnh tương ứng hệ điều hành (có thể tùy chỉnh path nếu Chrome ở vị trí khác):

- **macOS**:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
```

- **Linux**:

```bash
google-chrome --remote-debugging-port=9223
```

- **Windows** (ví dụ path mặc định):

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\temp\chrome-spy-etsy"
```

Giữ cửa sổ Chrome này mở trong suốt quá trình gọi API.

### 3. Chạy FastAPI server (uvicorn)

Khuyến nghị dùng `uvicorn` để chạy app (cross‑platform).

- **Unix (macOS/Linux)**:

```bash
uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674
```

- **Windows (PowerShell / CMD, sau khi kích hoạt venv)**:

```bat
uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674
```

Hoặc bạn cũng có thể chạy trực tiếp file:

```bash
python src/app/api_server.py
```

Server sẽ chạy ở `http://localhost:5674`:

- **Swagger UI**: `http://localhost:5674/docs`
- **ReDoc**: `http://localhost:5674/redoc`

---

## Sử dụng SpyEtsy

### Chạy qua CLI

```bash
# keyword mặc định "t-shirt", pages mặc định 5
python src/app/cdp_connection.py "handmade bag" 5
```

### Chạy qua API

API hiện tại cung cấp endpoint:

- **POST `/api/v1/etsy/spy`**: Spy Etsy qua CDP connection (yêu cầu Chrome đã chạy với CDP)

**Request body** (optional - nếu không gửi sẽ đọc từ `config.ini`):
```json
{
    "keyword": "handmade bag",
    "pages": 5,
    "config": {
        "created_date": 2
    }
}
```

**Response**:
```json
{
    "success": true,
    "message": "Đã spy xong 150 sản phẩm từ 5 trang.",
    "count": 150,
    "error": null
}
```

**Luồng xử lý**: 
1. Kết nối Chrome qua CDP (`http://localhost:9223`)
2. Điều hướng từng trang tìm kiếm Etsy (page 1 đến page N)
3. Chờ 10 giây để trang tải ổn định (Etsy là SPA)
4. Trích xuất dữ liệu HeyEtsy từ HTML bằng `extract_heyetsy_data`
5. Lọc theo ngày đăng (nếu có config)
6. Deduplicate theo `listing_id`
7. Gửi dữ liệu tới webhook `https://spyetsy.supover.com/webhook`

Xem `docs/ETSY_SPY_API.md` để biết chi tiết về request/response format và các tùy chọn khác.

---

## GUI Application

Dự án cũng cung cấp GUI desktop app với PyQt6:

- **Tính năng**: Form config, tự động launch Chrome với CDP, hiển thị log real-time, system tray icon
- **Cách chạy**: Xem `README_GUI.md` để biết chi tiết
- **Build**: App được đóng gói thành `.exe` (Windows) và `.dmg` (macOS) trong thư mục `installer/`

## Hỗ trợ chạy trên Windows

- **Event loop cho asyncio**:  
  Trong `src/app/api_server.py` có đoạn cấu hình event loop policy cho Windows để tương thích với Playwright và FastAPI.

- **Setup nhanh**:
  - Chạy `scripts\setup_windows.bat` để tạo venv, cài dependencies và Playwright.
  - Khởi động Chrome với CDP như hướng dẫn ở trên.
  - Kích hoạt venv: `venv\Scripts\activate`.
  - Chạy server: `uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674`.

---

## Cấu trúc project

```text
src/
├── app/
│   ├── __init__.py                    # export FastAPI app
│   ├── api_server.py                  # SpyEtsy API (FastAPI)
│   ├── cdp_connection.py              # Spy Etsy qua CDP connection
│   └── hidemyacc_connection_profile.py # Spy Etsy với HideMyAcc profile
├── core/
│   ├── __init__.py                    # export PlaywrightAutomation
│   └── automation.py                  # Playwright wrapper: connect_over_cdp, navigate, detach
├── models/
│   ├── __init__.py                    # export models & helpers
│   ├── input.py                       # SearchInput, ViewportConfig
│   └── output.py                      # save_json helper
├── utils/
│   ├── heyetsy_parser.py              # extract_heyetsy_data helper
│   ├── chrome_launcher.py             # Launch Chrome với CDP
│   ├── config_loader.py               # Load config từ config.ini
│   └── hidemyacc.py                   # HideMyAcc profile manager
└── gui/
    ├── app.py                         # PyQt6 application entry point
    └── main_window.py                 # Main window với form config
```

Tài liệu chi tiết nằm trong thư mục `docs/`:
- `ETSY_SPY_API.md` - Hướng dẫn sử dụng API
- `GUI_WORKFLOW.md` - Luồng hoạt động GUI app
- `CONFIG_INI_GUIDE.md` - Hướng dẫn cấu hình

---

## Maintenance & Utilities

### Xóa cache Python

Để xóa tất cả cache Python trong dự án (thư mục `__pycache__`, file `.pyc`, `.pyo`), chạy script:

**macOS/Linux:**
```bash
bash scripts/clear_cache.sh
```

**Windows:**
```bat
scripts\clear_cache.bat
```

Script sẽ xóa tất cả cache trong source code nhưng giữ nguyên cache trong `venv` để không ảnh hưởng đến môi trường ảo.

**Lệnh trực tiếp (nếu không dùng script):**
```bash
# Xóa thư mục __pycache__ (trừ venv)
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null

# Xóa file .pyc và .pyo (trừ venv)
find . -type f -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null
find . -type f -name "*.pyo" -not -path "./venv/*" -delete 2>/dev/null
```
