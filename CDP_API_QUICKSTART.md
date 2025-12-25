# CDP Connection API - Hướng dẫn nhanh

## Bước 1: Khởi động Chrome với CDP

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
```

**Hoặc dùng script:**
```bash
./scripts/start_chrome_with_cdp.sh
```

## Bước 2: Chạy API Server

```bash
uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5674
```

## Bước 3: Gọi API

### SpyEtsy (CDP Connection)

```bash
curl -X POST "http://localhost:5674/api/v1/etsy/spy" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "handmade bag",
    "pages": 2,
    "config": {
        "created_date": 2
    }
  }'
```

### SpyEtsy (HideMyAcc Profile)

```bash
curl -X POST "http://localhost:5674/api/v1/etsy/spy_hidemyacc" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "hma_xxx",
    "keyword": "handmade bag",
    "pages": 2,
    "config": {
        "created_date": 2
    }
  }'
```

### Xem API Documentation

Mở trình duyệt: `http://localhost:5674/docs`

## Xóa cache Python

Để xóa tất cả cache Python trong dự án:

**macOS/Linux:**
```bash
bash scripts/clear_cache.sh
```

**Windows:**
```bat
scripts\clear_cache.bat
```

## Xem hướng dẫn chi tiết

- **USPS Tracking**: Xem `docs/API_GUIDE.md`
- **SpyEtsy**: Xem `docs/ETSY_SPY_API.md`
