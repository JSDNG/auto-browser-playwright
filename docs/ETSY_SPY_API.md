# Hướng dẫn sử dụng SpyEtsy API

## Tổng quan

API server cung cấp 2 phương thức để spy dữ liệu sản phẩm từ Etsy:

1. **CDP Connection** (`/api/v1/etsy/spy`): Kết nối với Chrome đang chạy qua CDP
2. **HideMyAcc Profile** (`/api/v1/etsy/spy_hidemyacc`): Tự động launch HideMyAcc profile với Marco browser

## Yêu cầu hệ thống

- Python 3.11+
- Google Chrome hoặc Marco browser (HideMyAcc)
- Các dependencies trong `requirements.txt`
- HideMyAcc profiles (nếu dùng endpoint HideMyAcc)

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt Playwright browsers

```bash
python -m playwright install chromium
```

### 3. Cài đặt HideMyAcc (nếu dùng endpoint HideMyAcc)

- Cài đặt HideMyAcc application
- Tạo profiles trong HideMyAcc
- Profiles sẽ được lưu tại: `~/.hidemyacc/profiles/`

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

## Endpoint 1: CDP Connection

### POST `/api/v1/etsy/spy`

Kết nối với Chrome đang chạy qua CDP để spy Etsy.

#### Yêu cầu

**Chrome phải được khởi động trước với CDP:**

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
```

**Linux:**
```bash
google-chrome --remote-debugging-port=9223
```

**Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223
```

**Kiểm tra CDP đang chạy:**
Truy cập `http://localhost:9223/json` - nếu thấy JSON list các tab, nghĩa là CDP đã hoạt động.

#### Request Body

```json
{
    "keyword": "handmade bag",
    "pages": 5,
    "config": {
        "created_date": 2
    }
}
```

**Parameters:**
- `keyword` (string, required): Từ khóa tìm kiếm trên Etsy
- `pages` (integer, required): Số trang cần spy (từ 1 đến pages)
- `config` (object, optional): Config cho việc lọc dữ liệu
  - `created_date` (integer, optional): Số tháng để lọc ngày đăng (1-12, mặc định: 2)

#### Response

```json
{
    "success": true,
    "message": "Đã spy xong 150 sản phẩm từ 5 trang.",
    "count": 150,
    "error": null
}
```

#### Ví dụ với curl

```bash
curl -X POST "http://localhost:5674/api/v1/etsy/spy" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "handmade bag",
    "pages": 2,
    "config": {
        "created_date": 3
    }
  }'
```

#### Ví dụ với Python

```python
import requests

response = requests.post(
    "http://localhost:5674/api/v1/etsy/spy",
    json={
        "keyword": "handmade bag",
        "pages": 2,
        "config": {
            "created_date": 3
        }
    },
    timeout=300
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Count: {result['count']}")
print(f"Message: {result['message']}")
```

## Endpoint 2: HideMyAcc Profile

### POST `/api/v1/etsy/spy_hidemyacc`

Tự động launch HideMyAcc profile với Marco browser và spy Etsy.

#### Yêu cầu

- HideMyAcc application đã được cài đặt
- Profile ID phải tồn tại trong hệ thống
- Marco browser sẽ được tự động tìm trong `~/.hidemyacc/browser/`

#### Request Body - Không dùng proxy

```json
{
    "profile_id": "hma_693f644df34a403926dc3bf6",
    "keyword": "handmade bag",
    "pages": 5,
    "config": {
        "created_date": 2
    }
}
```

#### Request Body - Có proxy

```json
{
    "profile_id": "hma_693f644df34a403926dc3bf6",
    "keyword": "handmade bag",
    "pages": 5,
    "config": {
        "created_date": 2
    },
    "proxy_server": "http://proxy.example.com:8080",
    "proxy_username": "user",
    "proxy_password": "pass"
}
```

**Parameters:**
- `profile_id` (string, required): HideMyAcc profile ID (ví dụ: `hma_xxx`)
- `keyword` (string, required): Từ khóa tìm kiếm trên Etsy
- `pages` (integer, required): Số trang cần spy
- `config` (object, optional): Config cho việc lọc dữ liệu
  - `created_date` (integer, optional): Số tháng để lọc ngày đăng (1-12, mặc định: 2)
- `proxy_server` (string, optional): Địa chỉ proxy server (format: `http://host:port`)
- `proxy_username` (string, optional): Username cho proxy authentication (required nếu có `proxy_server`)
- `proxy_password` (string, optional): Password cho proxy authentication (required nếu có `proxy_server`)

**Lưu ý:** Nếu có `proxy_server` thì phải có đầy đủ `proxy_username` và `proxy_password`.

#### Response

```json
{
    "success": true,
    "message": "Đã spy xong 150 sản phẩm từ 5 trang.",
    "count": 150,
    "error": null
}
```

#### Ví dụ với curl

```bash
curl -X POST "http://localhost:5674/api/v1/etsy/spy_hidemyacc" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "hma_693f644df34a403926dc3bf6",
    "keyword": "handmade bag",
    "pages": 2,
    "config": {
        "created_date": 3
    }
  }'
```

#### Ví dụ với Python

```python
import requests

response = requests.post(
    "http://localhost:5674/api/v1/etsy/spy_hidemyacc",
    json={
        "profile_id": "hma_693f644df34a403926dc3bf6",
        "keyword": "handmade bag",
        "pages": 2,
        "config": {
            "created_date": 3
        },
        "proxy_server": "http://proxy.example.com:8080",
        "proxy_username": "user",
        "proxy_password": "pass"
    },
    timeout=600  # Timeout dài hơn vì cần launch browser
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Count: {result['count']}")
print(f"Message: {result['message']}")
```

## Flow hoạt động

### CDP Connection Flow

1. Kết nối với Chrome đang chạy qua CDP tại `localhost:9223`
2. Navigate đến từng trang Etsy search (page 1 đến page N)
3. Chờ 10 giây để trang tải ổn định (Etsy là SPA)
4. Extract HTML body (loại bỏ script/style tags)
5. Parse dữ liệu HeyEtsy từ HTML
6. Lọc sản phẩm theo ngày đăng (nếu có config)
7. Deduplicate theo `listing_id`
8. Gửi dữ liệu tới webhook: `https://spyetsy.supover.com/webhook`
9. Detach automation (giữ browser mở)

### HideMyAcc Profile Flow

1. Tìm HideMyAcc profile theo `profile_id`
2. Tự động tìm Marco browser executable mới nhất
3. Cấu hình proxy (nếu có)
4. Launch Playwright với profile qua `user-data-dir`
5. Navigate đến từng trang Etsy search
6. Extract và parse dữ liệu HeyEtsy
7. Lọc sản phẩm theo ngày đăng (nếu có config)
8. Gửi dữ liệu tới webhook
9. Detach automation (giữ browser mở)

## Dữ liệu được gửi tới Webhook

Dữ liệu được gửi dưới dạng JSON array, mỗi item là một sản phẩm:

```json
[
    {
        "listing_id": "123456789",
        "title": "Handmade Leather Bag",
        "image": "https://...",
        "views_24h": 150,
        "sold_24h": 3,
        "total_views": 5000,
        "total_sold": 150,
        "favorites": 25,
        "created": "12/25/2024",
        ...
    },
    ...
]
```

**Webhook URL:** `https://spyetsy.supover.com/webhook`

## Cấu hình

Các cấu hình có thể chỉnh trong `src/app/api_server.py`:

```python
# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5674

# CDP port cho Chrome/Marco (HideMyAcc)
CONFIG_CDP_PORT = 9223
```

## Xử lý lỗi thường gặp

### 1. Lỗi: "Connection refused" hoặc "Cannot connect to CDP"

**Nguyên nhân:** Chrome chưa được khởi động với CDP hoặc port không đúng.

**Giải pháp:**
- Kiểm tra Chrome đã khởi động với `--remote-debugging-port=9223` chưa
- Truy cập `http://localhost:9223/json` để xác nhận CDP đang chạy
- Kiểm tra port có bị conflict không

### 2. Lỗi: "Không tìm thấy HideMyAcc profile"

**Nguyên nhân:** Profile ID không tồn tại hoặc sai format.

**Giải pháp:**
- Kiểm tra profile ID có đúng không
- Liệt kê profiles: `python -c "from src.utils.hidemyacc import HideMyAccManager; print(HideMyAccManager().find_profiles())"`
- Đảm bảo HideMyAcc đã được cài đặt và có profiles

### 3. Lỗi: "Không tìm thấy Marco browser"

**Nguyên nhân:** Marco browser chưa được cài đặt hoặc không tìm thấy.

**Giải pháp:**
- Đảm bảo HideMyAcc đã được cài đặt
- Marco browser thường nằm tại `~/.hidemyacc/browser/marco-browser-*/`
- Kiểm tra quyền truy cập thư mục

### 4. Lỗi: "Proxy authentication failed"

**Nguyên nhân:** Proxy credentials không đúng.

**Giải pháp:**
- Kiểm tra `proxy_server`, `proxy_username`, `proxy_password` có đúng không
- Đảm bảo có đầy đủ cả 3 tham số nếu dùng proxy

### 5. Lỗi: "Không có dữ liệu để gửi" (count = 0)

**Nguyên nhân:** Không tìm thấy sản phẩm hoặc parser không extract được dữ liệu.

**Giải pháp:**
- Kiểm tra keyword có đúng không
- Kiểm tra Etsy có hiển thị kết quả không
- Có thể cần tăng thời gian chờ (hiện tại 10 giây)
- Kiểm tra HTML structure có thay đổi không (parser có thể cần update)
- Kiểm tra config `created_date` có quá nghiêm ngặt không

## Lưu ý quan trọng

1. **Browser được giữ mở**: Sau khi spy xong, browser sẽ được giữ mở (detach, không close) để có thể tiếp tục sử dụng hoặc debug.

2. **Timeout**: Endpoint HideMyAcc cần timeout dài hơn vì phải launch browser (khuyến nghị 600 giây).

3. **Xử lý tuần tự**: Mỗi request xử lý tuần tự, không song song.

4. **Webhook**: Dữ liệu được tự động gửi tới webhook `https://spyetsy.supover.com/webhook` sau khi spy xong.

5. **Deduplication**: Dữ liệu được deduplicate theo `listing_id` để tránh trùng lặp.

6. **Lọc ngày đăng**: Mặc định chỉ lấy sản phẩm có ngày đăng trong vòng 2 tháng. Có thể tùy chỉnh qua `config.created_date` (1-12 tháng).

## Sử dụng CLI (không qua API)

### CDP Connection CLI

```bash
python src/app/cdp_connection.py "handmade bag" 5
```

### HideMyAcc Profile CLI

```bash
python src/app/hidemyacc_connection_profile.py \
  --profile hma_693f644df34a403926dc3bf6 \
  --keyword "handmade bag" \
  --pages 5 \
  --with-proxy
```

**Options:**
- `--profile, -p`: HideMyAcc profile ID (bắt buộc nếu có nhiều profiles)
- `--keyword, -k`: Từ khóa search (mặc định: "t-shirt")
- `--pages`: Số trang spy (mặc định: 5)
- `--with-proxy`: Bật proxy với credentials mặc định
- `--no-proxy`: Tắt proxy (mặc định khi chạy trực tiếp)

## Troubleshooting

### Kiểm tra logs

API server sẽ log các thông tin quan trọng:
- Request nhận được
- Trang đang xử lý
- Số lượng sản phẩm đã extract
- Lỗi nếu có

### Debug mode

Để xem chi tiết hơn, thay đổi log level trong `api_server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Kiểm tra webhook

Kiểm tra webhook có nhận được dữ liệu không:
- Xem logs của webhook server tại `https://spyetsy.supover.com`
- Kiểm tra webhook URL có đúng không
- Kiểm tra network connection

## Liên hệ và hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Logs của API server
2. Browser DevTools Console (F12)
3. CDP endpoint: `http://localhost:9223/json` (cho CDP connection)
4. HideMyAcc profiles: `~/.hidemyacc/profiles/`

