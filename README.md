## Grok Video Generation API – Playwright + FastAPI

FastAPI server dùng Playwright để tự động gen video với Grok Imagine (https://grok.com/imagine).

### Tổng quan

- **Input**: Text prompt để tạo video
- **Xử lý**: FastAPI gọi Playwright, launch Chrome (hoặc kết nối qua CDP), navigate đến Grok Imagine, nhập prompt và tạo video
- **Output**: Kết quả dạng JSON với thông tin về việc gen video thành công hay thất bại

Chi tiết kiến trúc và luồng xử lý xem thêm trong `docs/implement.md` và `docs/tdd.md`.

### Yêu cầu hệ thống

- **Python**: 3.11+
- **Chrome**: Cài Chrome trên máy (dùng system Chrome, không dùng browser đi kèm Playwright)
- **CDP** (tùy chọn): Nếu dùng CDP connection, Chrome phải được khởi động với `--remote-debugging-port=9224`

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

### 2. Chạy FastAPI server (uvicorn)

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

## Grok Video Generation

### Mục đích

Gen video với Grok Imagine bằng cách:
- Launch Chrome trực tiếp (khuyến nghị)
- Hoặc kết nối với Chrome đã mở sẵn qua CDP

### Chạy CLI (CDP Connection)

```bash
# Cần Chrome đã chạy với --remote-debugging-port=9224
python src/app/cdp_connection.py "your prompt text"
```

### Chạy API

Xem `docs/API_GUIDE.md` để biết chi tiết về endpoint:
- `/api/v1/grok/launch` - Launch Chrome và navigate đến Grok Imagine để gen video

### Cách làm

1. **Direct Launch** (khuyến nghị):
   - API tự động launch Chrome
   - Navigate đến `https://grok.com/imagine`
   - Chờ trang load (5 giây)
   - Tìm và click vào element cụ thể
   - Đợi 2 giây
   - Nhập prompt text vào input field
   - Giữ browser mở để tiếp tục sử dụng

2. **CDP Connection**:
   - Yêu cầu Chrome đã bật `--remote-debugging-port=9224` và đang mở
   - Kết nối với Chrome qua CDP
   - Thực hiện các bước tương tự như Direct Launch

---

## Endpoints chính

API hiện tại cung cấp endpoint:

- **POST `/api/v1/grok/launch`**: Launch Chrome, navigate đến Grok Imagine và nhập prompt để gen video

Xem `docs/API_GUIDE.md` để biết chi tiết về request/response format và cách sử dụng.

---

## Hỗ trợ chạy trên Windows

- **Event loop cho asyncio**:  
  Trong `src/app/api_server.py` có đoạn:

  - Nếu hệ điều hành là Windows, cấu hình lại event loop policy để tương thích với Playwright và FastAPI.

- **Setup nhanh**:
  - Chạy `scripts\setup_windows.bat` để tạo venv, cài dependencies và Playwright.
  - Kích hoạt venv: `venv\Scripts\activate`.
  - Chạy server: `uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674`.

---

## Cấu trúc project (rút gọn)

```text
src/
├── app/
│   ├── __init__.py        # export FastAPI app
│   ├── api_server.py      # Grok Video Generation API (FastAPI)
│   └── cdp_connection.py   # Hàm grok_gen_video_via_cdp và grok_gen_video_direct
├── core/
│   ├── __init__.py        # export PlaywrightAutomation
│   └── automation.py      # Playwright wrapper: connect_over_cdp, navigate, detach
├── models/
│   ├── __init__.py        # export models & helpers dùng nội bộ
│   ├── input.py           # ViewportConfig, GrokInput
│   └── output.py          # save_json helper
└── utils/
    └── (các utility functions khác)
```

Tài liệu chi tiết cho kiến trúc nằm trong thư mục `docs/`.
