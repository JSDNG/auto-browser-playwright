# Hướng dẫn sử dụng Grok Video Generation API

## Tổng quan

API server cung cấp endpoint để gen video với Grok Imagine:

1. **Grok Launch** (`/api/v1/grok/launch`): Launch Chrome, navigate đến Grok Imagine và nhập prompt để gen video

## Yêu cầu hệ thống

- Python 3.11+
- Google Chrome
- Các dependencies trong `requirements.txt`

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt Playwright browsers

```bash
python -m playwright install chromium
```

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
- `--port 5674`: Port API (có thể thay đổi trong `api_server.py`)

### Cách 3: Chạy production với uvicorn

```bash
uvicorn src.app.api_server:app --host 0.0.0.0 --port 5674 --workers 4
```

## Truy cập API

Sau khi server chạy, bạn có thể:

1. **Truy cập Swagger UI**: `http://localhost:5674/docs`
2. **Truy cập ReDoc**: `http://localhost:5674/redoc`

## Endpoint: Grok Video Generation

### POST `/api/v1/grok/launch`

Launch Chrome, navigate đến Grok Imagine (https://grok.com/imagine) và nhập prompt để gen video.

#### Yêu cầu

- Chrome phải được cài đặt trên hệ thống
- Không cần Chrome đang chạy trước (API sẽ tự động launch)

#### Request Body

```json
{
    "text": "A beautiful sunset over the ocean with birds flying"
}
```

**Parameters:**
- `text` (string, required): Prompt text để tạo video (không được để trống)

#### Response

```json
{
    "success": true,
    "message": "Đã navigate đến Grok Imagine và nhập prompt để gen video thành công",
    "url": "https://grok.com/imagine",
    "error": null
}
```

**Response Fields:**
- `success` (boolean): Trạng thái thành công/thất bại
- `message` (string): Thông báo mô tả kết quả
- `url` (string, optional): URL hiện tại sau khi navigate
- `error` (string, optional): Thông báo lỗi nếu có

#### Ví dụ với curl

```bash
curl -X POST "http://localhost:5674/api/v1/grok/launch" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A beautiful sunset over the ocean with birds flying"
  }'
```

#### Ví dụ với Python

```python
import requests

response = requests.post(
    "http://localhost:5674/api/v1/grok/launch",
    json={
        "text": "A beautiful sunset over the ocean with birds flying"
    },
    timeout=60
)

result = response.json()
print(f"Success: {result['success']}")
print(f"URL: {result.get('url')}")
print(f"Message: {result['message']}")
```

## Flow hoạt động

### Grok Launch Flow

1. Launch Chrome trực tiếp (không qua CDP)
2. Navigate đến https://grok.com/imagine
3. Chờ 5 giây để trang load và các element render
4. Tìm và click vào element cụ thể (input field wrapper)
5. Đợi 2 giây sau khi click
6. Tìm input field (textarea hoặc contenteditable)
7. Nhập prompt text vào input field
8. Detach automation (giữ browser mở để tiếp tục sử dụng)

## Cấu hình

Các cấu hình có thể chỉnh trong `src/app/api_server.py`:

```python
# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5674

# CDP port cho Chrome (nếu dùng CDP connection)
CONFIG_CDP_PORT = 9224
```

## Xử lý lỗi thường gặp

### 1. Lỗi khi launch Grok

**Nguyên nhân:** Chrome chưa được cài đặt hoặc không tìm thấy.

**Giải pháp:**
- Đảm bảo Chrome đã được cài đặt trên hệ thống
- Kiểm tra Chrome có trong PATH không
- Thử launch Chrome thủ công để xác nhận

### 2. Lỗi: "Text không được để trống"

**Nguyên nhân:** Request body không có field `text` hoặc `text` là chuỗi rỗng.

**Giải pháp:**
- Đảm bảo request body có field `text` với giá trị không rỗng
- Kiểm tra JSON format có đúng không

### 3. Lỗi: "Không tìm thấy input field"

**Nguyên nhân:** Cấu trúc HTML của Grok Imagine có thể đã thay đổi.

**Giải pháp:**
- Kiểm tra xem trang Grok Imagine có load đầy đủ không
- Có thể cần tăng thời gian chờ (hiện tại 5 giây)
- Kiểm tra selector có còn đúng không

## Lưu ý quan trọng

1. **Browser được giữ mở**: Sau khi nhập prompt, browser sẽ được giữ mở (detach, không close) để có thể tiếp tục sử dụng hoặc debug.

2. **Timeout**: Khuyến nghị 60 giây cho request.

3. **Xử lý tuần tự**: Mỗi request xử lý tuần tự, không song song.

4. **Input field detection**: API sẽ thử nhiều selector khác nhau để tìm input field, bao gồm:
   - `textarea[placeholder*='message']`
   - `textarea[placeholder*='ask']`
   - `textarea[placeholder*='imagine']`
   - `textarea`
   - `[contenteditable='true']`
   - và các selector khác

## Sử dụng CLI (không qua API)

### CDP Connection CLI

```bash
# Cần Chrome đã chạy với --remote-debugging-port=9224
python src/app/cdp_connection.py "your prompt text"
```

## Troubleshooting

### Kiểm tra logs

API server sẽ log các thông tin quan trọng:
- Request nhận được
- Trang đang navigate
- Element đã tìm thấy/click
- Input field đã tìm thấy/nhập text
- Lỗi nếu có

### Debug mode

Để xem chi tiết hơn, thay đổi log level trong `api_server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Kiểm tra browser

Sau khi API chạy, browser sẽ được giữ mở. Bạn có thể:
- Kiểm tra xem prompt đã được nhập vào input field chưa
- Kiểm tra console (F12) để xem có lỗi JavaScript không
- Thử submit prompt thủ công để xác nhận

## Liên hệ và hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Logs của API server
2. Browser DevTools Console (F12)
3. Kiểm tra xem Grok Imagine có thay đổi cấu trúc HTML không
