# Hướng dẫn chạy CDP Connection API

## Tổng quan

API này cho phép kết nối với Chrome đang chạy qua CDP (Chrome DevTools Protocol) để kiểm tra trạng thái delivered của các shipments từ USPS.

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
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

Hoặc dùng script tiện ích (tự tạo profile tách biệt):

```bash
./scripts/start_chrome_with_cdp.sh
```

### Linux

```bash
google-chrome --remote-debugging-port=9222
```

Hoặc:

```bash
chromium --remote-debugging-port=9222
```

### Windows

```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

Hoặc dùng script tiện ích:

```cmd
scripts\start_chrome_with_cdp.bat
```

### Kiểm tra CDP đang chạy

Mở trình duyệt và truy cập: `http://localhost:9222/json`

Nếu thấy danh sách các tab đang mở dưới dạng JSON, nghĩa là CDP đã hoạt động.

## Chạy API Server

### Cách 1: Chạy trực tiếp với Python

```bash
python src/app/api_server.py
```

### Cách 2: Chạy với uvicorn (khuyến nghị)

```bash
uvicorn src.app.api_server:app --reload --host 0.0.0.0 --port 5673
```

**Các tham số:**
- `--reload`: Tự động reload khi code thay đổi (chỉ dùng khi development)
- `--host 0.0.0.0`: Cho phép truy cập từ các máy khác trong mạng
- `--port 5673`: Port API (có thể thay đổi, mặc định trong docs là 5673)

### Cách 3: Chạy production với uvicorn

```bash
uvicorn src.app.api_server:app --host 0.0.0.0 --port 5673 --workers 4
```

## Truy cập API

Sau khi server chạy, bạn có thể:

1. **Truy cập Swagger UI** (tự động): `http://localhost:5673/docs`
2. **Truy cập ReDoc**: `http://localhost:5673/redoc`

## Các Endpoints

### POST `/api/v1/cdp/auto-check-tracking` - Kiểm tra nhiều shipments (Batch)

**Request Body:**
```json
[
    {
        "shipment_id": "123",
        "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
    },
    {
        "shipment_id": "456",
        "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858308"
    }
]
```

**Response:**
```json
[
    {
        "shipment_id": "123",
        "delivered": true,
        "delivered_at": "2025-12-13T05:01:00Z"
    },
    {
        "shipment_id": "456",
        "delivered": false,
        "delivered_at": null
    }
]
```

**Ví dụ với curl:**
```bash
curl -X POST "http://localhost:5673/api/v1/cdp/auto-check-tracking" \
  -H "Content-Type: application/json" \
  -d '[
    {
        "shipment_id": "123",
        "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
    }
  ]'
```

## Ví dụ sử dụng với Python

```python
import requests

# Dữ liệu shipments
shipments = [
    {
        "shipment_id": "123",
        "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
    },
    {
        "shipment_id": "456",
        "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858308"
    }
]

# Gọi API
response = requests.post(
    "http://localhost:5673/api/v1/cdp/auto-check-tracking",
    json=shipments,
    timeout=30,
)
response.raise_for_status()

# Xử lý kết quả (danh sách ShipmentTrackingResponse)
results = response.json()

for item in results:
    print(f"\nShipment ID: {item['shipment_id']}")
    print(f"  Delivered: {item['delivered']}")
    print(f"  Delivered at: {item['delivered_at']}")
```

## Ví dụ sử dụng với PHP

```php
<?php
$shipments = [
    [
        'shipment_id' => '123',
        'tracking_link' => 'https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307'
    ],
    [
        'shipment_id' => '456',
        'tracking_link' => 'https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858308'
    ]
];

$ch = curl_init('http://localhost:5673/api/v1/cdp/auto-check-tracking');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($shipments));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

$response = curl_exec($ch);

if ($response === false) {
    throw new \RuntimeException('Curl error: ' . curl_error($ch));
}

curl_close($ch);

$results = json_decode($response, true);

foreach ($results as $item) {
    echo "\nShipment ID: " . $item['shipment_id'] . "\n";
    echo "  Delivered: " . ($item['delivered'] ? 'true' : 'false') . "\n";
    echo "  Delivered at: " . ($item['delivered_at'] ?? 'null') . "\n";
}
?>
```

## Xử lý lỗi thường gặp

### 1. Lỗi: "Connection refused" hoặc "Cannot connect to CDP"

**Nguyên nhân:** Chrome chưa được khởi động với CDP hoặc port không đúng.

**Giải pháp:**
- Kiểm tra Chrome đã khởi động với `--remote-debugging-port=9222` chưa
- Truy cập `http://localhost:9222/json` để xác nhận CDP đang chạy
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
- Thử truy cập `http://localhost:9222/json` để xác nhận

## Lưu ý quan trọng

1. **Chrome phải được khởi động trước khi chạy API**
2. **Không đóng Chrome** trong khi API đang xử lý requests
3. **Mỗi request sẽ mở một tab mới** trong Chrome (hoặc sử dụng tab hiện có)
4. **Browser sẽ không bị đóng** sau khi xử lý xong (chỉ detach khỏi Playwright)
5. **API xử lý tuần tự** các shipments trong batch request (một cái một)

## Tối ưu hóa

### Xử lý song song (nếu cần)

Hiện tại API xử lý tuần tự. Nếu muốn xử lý song song, có thể sử dụng `asyncio.gather()`:

```python
# Trong api_server.py, thay vì for loop:
results = await asyncio.gather(*[
    connect_to_chrome_via_cdp(...) for shipment in shipments
])
```

**Lưu ý:** Xử lý song song có thể gây quá tải Chrome nếu có quá nhiều requests cùng lúc.

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
- Shipment đang xử lý
- Kết quả của từng shipment
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
3. CDP endpoint: `http://localhost:9222/json`
