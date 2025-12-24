# Grok Video Generation API - Hướng dẫn nhanh

## Bước 1: Chạy API Server

```bash
uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674
```

**Lưu ý**: Không cần khởi động Chrome trước. API sẽ tự động launch Chrome.

## Bước 2: Gọi API

### Grok Video Generation

```bash
curl -X POST "http://localhost:5674/api/v1/grok/launch" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "A beautiful sunset over the ocean with birds flying"
  }'
```

### Xem API Documentation

Mở trình duyệt: `http://localhost:5674/docs`

## Sử dụng CLI (Tùy chọn - CDP Connection)

Nếu muốn dùng CLI với CDP connection:

### Bước 1: Khởi động Chrome với CDP

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224
```

**Hoặc dùng script:**
```bash
./scripts/start_chrome_with_cdp.sh
```

### Bước 2: Chạy CLI

```bash
python src/app/cdp_connection.py "A beautiful sunset over the ocean with birds flying"
```

## Xem hướng dẫn chi tiết

- **API Guide**: Xem `docs/API_GUIDE.md`
- **CDP Connection**: Xem `docs/CDP_CONNECTION.md`
