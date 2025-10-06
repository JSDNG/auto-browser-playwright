# Auto Flash Sale - Tự Động Hóa HideMyAcc

Hệ thống tự động Flash Sale sử dụng HideMyAcc API để điều khiển trình duyệt.

## 🚀 Tính Năng

- **Tích hợp HideMyAcc**: API đầy đủ để quản lý profile
- **RESTful API**: API REST sạch sẽ cho tích hợp bên ngoài
- **Quản lý Profile**: Khởi động/dừng profile với logic retry
- **Giới hạn Tốc độ**: Rate limiting và bảo mật tích hợp
- **Hỗ trợ Docker**: Sẵn sàng cho triển khai container
- **Giám sát**: Health checks và logging
- **Webhook**: Tích hợp với các dịch vụ bên ngoài (n8n, v.v.)

## 📁 Cấu Trúc Dự Án

```
auto-fls/
├─ .env                    # Cấu hình môi trường
├─ requirements.txt        # Dependencies Python
├─ app/
│  ├─ __init__.py         # Khởi tạo package
│  ├─ config.py           # Quản lý cấu hình
│  ├─ hma_client.py       # Client API HideMyAcc
│  ├─ utils.py            # Các hàm tiện ích
│  └─ routes.py           # API routes
├─ server.py              # Ứng dụng Flask chính
├─ docker/
│  ├─ Dockerfile          # Định nghĩa Docker image
│  ├─ docker-compose.yml  # Cấu hình Docker Compose
│  ├─ ngrok.yml          # Cấu hình tunnel Ngrok
│  └─ prometheus.yml     # Cấu hình giám sát
└─ logs/                  # Logs ứng dụng
```

## 🛠️ Cài Đặt

### Yêu Cầu Hệ Thống

- Python 3.11+
- Ứng dụng HideMyAcc desktop
- Docker (tùy chọn)

### Phát Triển Local

1. **Clone và setup**:
   ```bash
   cd auto-fls
   pip install -r requirements.txt
   ```

2. **Cấu hình môi trường**:
   ```bash
   copy env_template.txt .env
   # Chỉnh sửa .env với cài đặt của bạn
   ```

3. **Khởi động HideMyAcc**:
   - Mở ứng dụng HideMyAcc desktop
   - Đảm bảo API server đang chạy (thường port 2268)

4. **Chạy ứng dụng**:
   ```bash
   python server.py
   ```

### Triển Khai Docker

1. **Build và chạy**:
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Kiểm tra trạng thái**:
   ```bash
   docker-compose ps
   docker-compose logs -f auto-fls
   ```

## 📚 Tài Liệu API

### Base URL
- Local: `http://localhost:5001/api/v1`
- Docker: `http://localhost:5001/api/v1`

### Endpoints

#### Kiểm Tra Sức Khỏe
```http
GET /api/v1/health
```

#### Danh Sách Profiles
```http
GET /api/v1/profiles
```

#### Khởi Động Profile
```http
POST /api/v1/profiles/{profile_id}/start
Content-Type: application/json

{
  "open_tabs": ["https://example.com"]
}
```

#### Dừng Profile
```http
POST /api/v1/profiles/{profile_id}/stop
```

#### Trạng Thái Profile
```http
GET /api/v1/profiles/{profile_id}/status
```

#### Profiles Đang Hoạt Động
```http
GET /api/v1/profiles/active
```

### Ví Dụ Sử Dụng

```python
import requests

# Khởi động profile
response = requests.post(
    "http://localhost:5001/api/v1/profiles/6898c8f7effa52a76ed48168/start",
    json={"open_tabs": ["https://seller.tiktok.com"]}
)

if response.status_code == 200:
    data = response.json()
    print(f"Profile khởi động trên port: {data['data']['port']}")
    print(f"WebSocket URL: {data['data']['ws_url']}")
```

## 🔧 Cấu Hình

### Biến Môi Trường

| Biến | Mô Tả | Mặc Định |
|------|-------|----------|
| `HMA_API_BASE` | URL gốc API HideMyAcc | `http://127.0.0.1:2268` |
| `HMA_API_KEY` | API key HideMyAcc | - |
| `SERVER_HOST` | Host server | `0.0.0.0` |
| `SERVER_PORT` | Port server | `5001` |
| `DEBUG` | Chế độ debug | `False` |
| `LOG_LEVEL` | Mức độ logging | `INFO` |
| `DEFAULT_PROFILE_ID` | Profile ID mặc định | `6898c8f7effa52a76ed48168` |
| `BACKUP_PROFILE_ID` | Profile ID dự phòng | `689c58b2effa52a76e7b76be` |

### Thiết Lập HideMyAcc

1. **Cài đặt HideMyAcc**: Tải từ trang web chính thức
2. **Tạo profiles**: Thiết lập các profile trình duyệt
3. **Bật API**: Đảm bảo API server đang chạy
4. **Lấy profile IDs**: Sử dụng endpoint danh sách profiles

## 🐳 Cấu Hình Docker

### Docker Compose Services

- **auto-fls**: Server ứng dụng chính
- **ngrok**: Tunnel công khai (tùy chọn)
- **prometheus**: Giám sát (tùy chọn)

### Tùy Chỉnh

Chỉnh sửa `docker/docker-compose.yml` để:
- Thay đổi ports
- Thêm biến môi trường
- Cấu hình volumes
- Bật/tắt services

## 📊 Giám Sát

### Health Checks

- Ứng dụng: `GET /api/v1/health`
- Docker: Health checks tích hợp
- Prometheus: Metrics endpoint (nếu bật)

### Logs

- Logs ứng dụng: `logs/auto_fls.log`
- Docker logs: `docker-compose logs -f auto-fls`

## 🔒 Bảo Mật

- Rate limiting trên tất cả endpoints
- Validation input cho profile IDs
- Xử lý lỗi và logging
- Cấu hình CORS
- Secrets dựa trên môi trường

## 🚨 Khắc Phục Sự Cố

### Vấn Đề Thường Gặp

1. **Kết nối bị từ chối đến HMA**:
   - Kiểm tra HideMyAcc có đang chạy không
   - Xác minh port 2268 có thể truy cập
   - Kiểm tra cài đặt firewall

2. **Lỗi license (402)**:
   - Gia hạn license HideMyAcc
   - Kiểm tra trạng thái thanh toán

3. **Profile không tìm thấy (400)**:
   - Xác minh profile ID tồn tại
   - Kiểm tra profile chưa đang chạy

### Chế Độ Debug

Bật chế độ debug:
```bash
set DEBUG=True
python server.py
```

## 📝 Các Bước Triển Khai

### 1. Cài Đặt Dependencies
```bash
cd auto-fls
pip install -r requirements.txt
```

### 2. Cấu Hình Environment
```bash
copy env_template.txt .env
# Chỉnh sửa .env với Profile IDs của bạn
```

### 3. Khởi Động HideMyAcc
- Mở HideMyAcc desktop app
- Đảm bảo API server chạy trên port 2268

### 4. Chạy Server
```bash
python server.py
```

### 5. Test API
```bash
# Health check
curl http://localhost:5001/api/v1/health

# Khởi động profile
curl -X POST http://localhost:5001/api/v1/profiles/6898c8f7effa52a76ed48168/start
```

## 🎯 Sử Dụng Thực Tế

### Khởi Động Profile Tự Động
```python
import requests

# Sử dụng profile mặc định từ .env
response = requests.post(
    "http://localhost:5001/api/v1/profiles/6898c8f7effa52a76ed48168/start",
    json={
        "open_tabs": [
            "https://seller.tiktok.com",
            "https://example.com"
        ]
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Profile khởi động thành công!")
    print(f"📍 Port: {data['data']['port']}")
    print(f"🔗 WebSocket: {data['data']['ws_url']}")
else:
    print(f"❌ Lỗi: {response.text}")
```

### Kiểm Tra Trạng Thái
```python
# Kiểm tra health
health = requests.get("http://localhost:5001/api/v1/health")
print(f"Server status: {health.json()['status']}")

# Kiểm tra profiles đang hoạt động
active = requests.get("http://localhost:5001/api/v1/profiles/active")
print(f"Active profiles: {active.json()['data']['active_count']}")
```

## 📞 Hỗ Trợ

Để được hỗ trợ:
- Kiểm tra phần khắc phục sự cố
- Xem logs để biết chi tiết lỗi
- Mở issue trên GitHub

## 📄 License

Dự án này được cấp phép theo MIT License.

## 🤝 Đóng Góp

1. Fork repository
2. Tạo feature branch
3. Thực hiện thay đổi
4. Thêm tests
5. Submit pull request
