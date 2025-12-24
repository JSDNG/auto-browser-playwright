# Hướng dẫn chạy CDP Connection cho Grok Video Generation

## Tổng quan

API này cung cấp endpoint **Grok Video Generation** (`/api/v1/grok/launch`): Gen video với Grok Imagine.

> **Lưu ý**: Xem `docs/API_GUIDE.md` để biết chi tiết về Grok video generation endpoints.

## Yêu cầu hệ thống

- Python 3.11+
- Google Chrome đã cài đặt
- Các dependencies trong `requirements.txt`

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt Playwright browsers (nếu chưa có)

```bash
python -m playwright install chromium
```

## Khởi động Chrome với CDP (Tùy chọn)

**Lưu ý**: Nếu dùng endpoint `/api/v1/grok/launch`, không cần khởi động Chrome trước. API sẽ tự động launch Chrome.

Nếu bạn muốn dùng CLI với CDP connection, Chrome phải được khởi động với flag `--remote-debugging-port` trước khi chạy.

### macOS

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224
```

Hoặc dùng script tiện ích (tự tạo profile tách biệt):

```bash
./scripts/start_chrome_with_cdp.sh
```

### Linux

```bash
google-chrome --remote-debugging-port=9224
```

Hoặc:

```bash
chromium --remote-debugging-port=9224
```

### Windows

```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9224 --user-data-dir="C:\temp\chrome-debug"
```

Hoặc dùng script tiện ích:

```cmd
scripts\start_chrome_with_cdp.bat
```

### Kiểm tra CDP đang chạy

Mở trình duyệt và truy cập: `http://localhost:9224/json`

Nếu thấy danh sách các tab đang mở dưới dạng JSON, nghĩa là CDP đã hoạt động.

## Chạy API Server

### Cách 1: Chạy trực tiếp với Python

```bash
python src/app/api_server.py
```

### Cách 2: Chạy với uvicorn (khuyến nghị)

```bash
uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674
```

**Các tham số:**
- `--reload`: Tự động reload khi code thay đổi (chỉ dùng khi development)
- `--host 0.0.0.0`: Cho phép truy cập từ các máy khác trong mạng
- `--port 5674`: Port API (có thể thay đổi, mặc định trong docs là 5674)

### Cách 3: Chạy production với uvicorn

```bash
uvicorn src.app.api_server:app --host 0.0.0.0 --port 5674 --workers 4
```

## Truy cập API

Sau khi server chạy, bạn có thể:

1. **Truy cập Swagger UI** (tự động): `http://localhost:5674/docs`
2. **Truy cập ReDoc**: `http://localhost:5674/redoc`

## Các Endpoints

API hiện tại cung cấp endpoint **Grok Video Generation**. Xem `docs/API_GUIDE.md` để biết chi tiết về:

- `/api/v1/grok/launch` - Gen video với Grok Imagine

## Xử lý lỗi thường gặp

### 1. Lỗi: "Connection refused" hoặc "Cannot connect to CDP"

**Nguyên nhân:** Chrome chưa được khởi động với CDP hoặc port không đúng (chỉ áp dụng khi dùng CLI với CDP).

**Giải pháp:**
- Nếu dùng API endpoint `/api/v1/grok/launch`, không cần Chrome chạy trước
- Nếu dùng CLI với CDP, kiểm tra Chrome đã khởi động với `--remote-debugging-port=9224` chưa
- Truy cập `http://localhost:9224/json` để xác nhận CDP đang chạy
- Kiểm tra port có bị conflict không

### 2. Lỗi: "ModuleNotFoundError: No module named 'fastapi'"

**Nguyên nhân:** Chưa cài đặt dependencies.

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### 3. Lỗi: "Playwright browser not found"

**Nguyên nhân:** Chưa cài đặt Playwright browsers.

**Giải pháp:**
```bash
playwright install chromium
```

### 4. Lỗi khi launch Chrome

**Nguyên nhân:** Chrome chưa được cài đặt hoặc không tìm thấy.

**Giải pháp:**
- Đảm bảo Chrome đã được cài đặt trên hệ thống
- Kiểm tra Chrome có trong PATH không
- Thử launch Chrome thủ công để xác nhận

## Lưu ý quan trọng

1. **API endpoint không cần Chrome chạy trước**: Endpoint `/api/v1/grok/launch` sẽ tự động launch Chrome
2. **CLI với CDP cần Chrome chạy trước**: Nếu dùng CLI `cdp_connection.py`, Chrome phải được khởi động với CDP trước
3. **Không đóng Chrome** trong khi API đang xử lý requests (nếu dùng CDP)
4. **Browser sẽ không bị đóng** sau khi xử lý xong (chỉ detach khỏi Playwright)
5. **API xử lý tuần tự** - mỗi request xử lý một cái một

## Dừng server

Nhấn `Ctrl+C` trong terminal đang chạy server.

## Dừng Chrome với CDP

### macOS/Linux:
```bash
./scripts/stop_chrome_with_cdp.sh
```

### Windows:
```cmd
scripts\stop_chrome_with_cdp.bat
```

Hoặc đóng Chrome thủ công.

## Troubleshooting

### Kiểm tra logs

API server sẽ log các thông tin quan trọng:
- Request nhận được
- Trang đang navigate
- Element đã tìm thấy/click
- Input field đã tìm thấy/nhập text
- Lỗi nếu có

### Debug mode

Để xem chi tiết hơn, có thể thay đổi log level trong `api_server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Liên hệ và hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Logs của API server
2. Chrome DevTools Console (F12)
3. CDP endpoint: `http://localhost:9224/json` (nếu dùng CDP)
