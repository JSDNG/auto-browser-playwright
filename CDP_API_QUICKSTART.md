# CDP Connection API - Hướng dẫn nhanh

## Bước 1: Khởi động Chrome với CDP

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
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

### Kiểm tra nhiều shipments (Batch)

```bash
curl -X POST "http://localhost:5674/api/v1/cdp/auto-check-tracking" \
  -H "Content-Type: application/json" \
  -d '[
    {
        "shipment_id": "123",
        "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9400150105794041827256"
    }
  ]'
```

### Xem API Documentation

Mở trình duyệt: `http://localhost:5674/docs`

## Xem hướng dẫn chi tiết

Xem file: `docs/API_GUIDE.md`
