# Hướng dẫn sử dụng config.ini

## Tổng quan

File `config.ini` cho phép bạn cấu hình filter và search criteria mà không cần gửi request body qua API.

## Cách sử dụng

### 1. Tạo file config.ini

Copy `config.ini.example` thành `config.ini`:

```bash
# Mac/Linux
cp config.ini.example config.ini

# Windows
copy config.ini.example config.ini
```

### 2. Chỉnh sửa config.ini

Mở file `config.ini` và chỉnh sửa:

```ini
[search]
# Từ khóa tìm kiếm trên Etsy
keyword = handmade bag

# Số trang cần spy (1-20)
pages = 5

[filter]
# Số tháng để lọc ngày đăng (1-12)
# Ví dụ: 2 = chỉ lấy sản phẩm đăng trong vòng 2 tháng gần đây
created_date_months = 2

[webhook]
# URL webhook để gửi dữ liệu sau khi spy xong
url = https://spyetsy.supover.com/webhook

[api]
# Host và port cho API server
host = 0.0.0.0
port = 5674

[cdp]
# Port cho Chrome CDP connection
port = 9223
```

### 3. Gọi API

**Cách 1: Không gửi body (dùng config.ini)**
```bash
curl -X POST "http://localhost:5674/api/v1/etsy/spy" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Cách 2: Gửi body (override config.ini)**
```bash
curl -X POST "http://localhost:5674/api/v1/etsy/spy" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "handmade bag",
    "pages": 5,
    "config": {
      "created_date": 2
    }
  }'
```

## Thứ tự ưu tiên

1. **Request body** (nếu có) → Ưu tiên cao nhất
2. **config.ini** (nếu không có body)
3. **Default values** (nếu không có cả 2)

## Lưu ý

- File `config.ini` phải nằm cùng thư mục với executable
- Nếu không có `config.ini`, app sẽ dùng default values
- Request body luôn override `config.ini` nếu có

