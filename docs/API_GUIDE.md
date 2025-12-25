# Hướng dẫn chạy CDP Connection API

## Tổng quan

API này cung cấp endpoint **SpyEtsy** (`/api/v1/etsy/spy`): Spy dữ liệu sản phẩm từ Etsy qua CDP connection.

> **Lưu ý**: Xem `docs/ETSY_SPY_API.md` để biết chi tiết về SpyEtsy endpoints.

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

## Khởi động Chrome với CDP

**Quan trọng**: Chrome phải được khởi động với flag `--remote-debugging-port` trước khi chạy API.

### macOS

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
```

Hoặc dùng script tiện ích (tự tạo profile tách biệt):

```bash
./scripts/start_chrome_with_cdp.sh
```

### Linux

```bash
google-chrome --remote-debugging-port=9223
```

Hoặc:

```bash
chromium --remote-debugging-port=9223
```

### Windows

```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\temp\chrome-debug"
```

Hoặc dùng script tiện ích:

```cmd
scripts\start_chrome_with_cdp.bat
```

### Kiểm tra CDP đang chạy

Mở trình duyệt và truy cập: `http://localhost:9223/json`

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
3. **Health check**: `http://localhost:5674/health`

## Các Endpoints

API hiện tại chỉ cung cấp endpoint **SpyEtsy**. Xem `docs/ETSY_SPY_API.md` để biết chi tiết về:

- `/api/v1/etsy/spy` - SpyEtsy qua CDP connection
- `/api/v1/etsy/spy_hidemyacc` - SpyEtsy với HideMyAcc profile

## Xử lý lỗi thường gặp

### 1. Lỗi: "Connection refused" hoặc "Cannot connect to CDP"

**Nguyên nhân:** Chrome chưa được khởi động với CDP hoặc port không đúng.

**Giải pháp:**
- Kiểm tra Chrome đã khởi động với `--remote-debugging-port=9223` chưa
- Truy cập `http://localhost:9223/json` để xác nhận CDP đang chạy
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

### 4. API chạy nhưng không kết nối được với Chrome

**Nguyên nhân:** Chrome đã đóng hoặc CDP không còn hoạt động.

**Giải pháp:**
- Khởi động lại Chrome với CDP
- Kiểm tra Chrome có đang chạy không
- Thử truy cập `http://localhost:9223/json` để xác nhận

## Lưu ý quan trọng

1. **Chrome phải được khởi động trước** (cho endpoint `/api/v1/etsy/scrape`)
2. **Không đóng Chrome** trong khi API đang xử lý requests
3. **Browser sẽ không bị đóng** sau khi xử lý xong (chỉ detach khỏi Playwright)
4. **API xử lý tuần tự** - mỗi request xử lý một cái một
5. **Dữ liệu được gửi tới webhook** sau khi scrape xong

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

## Xóa cache Python

Để xóa tất cả cache Python trong dự án (thư mục `__pycache__`, file `.pyc`, `.pyo`):

**macOS/Linux:**
```bash
bash scripts/clear_cache.sh
```

**Windows:**
```bat
scripts\clear_cache.bat
```

Script sẽ xóa tất cả cache trong source code nhưng giữ nguyên cache trong `venv` để không ảnh hưởng đến môi trường ảo.

## Troubleshooting

### Kiểm tra logs

API server sẽ log các thông tin quan trọng:
- Request nhận được
- Trang đang xử lý
- Số lượng sản phẩm đã extract
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
3. CDP endpoint: `http://localhost:9223/json`
