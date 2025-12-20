# Test Driven Development (TDD) - CDP Tracking API (USPS) & HeyEtsy scraper

## 1. Tổng quan

Xây dựng một API nhỏ, dễ test để:

-   **Kết nối CDP**: Kết nối Playwright tới Chrome đang chạy sẵn
-   **Kiểm tra USPS tracking**: Đọc nội dung trang tracking và xác định trạng thái delivered
-   **Batch requests**: Nhận nhiều shipments trong một request
-   **Kết quả đơn giản**: Mỗi shipment chỉ trả về `{ shipment_id, delivered, delivered_at }`

## 1.1. Kiến trúc hiện tại

```
Client (PHP/Python/...) ──▶ FastAPI (`api_server.py`) ──▶ Chrome (CDP)
                                     │
                                     ▼
                           `connect_to_chrome_via_cdp`
                                     │
                                     ▼
                             USPS Tracking Page
```

```
CLI (keyword/pages) ──▶ cdp_connection.py ──▶ Chrome (CDP) ──▶ Etsy search pages ──▶ HeyEtsy overlay
```

## 1.2. Project Structure (liên quan tới API này)

```
src/
├── app/
│   ├── api_server.py      # FastAPI app, định nghĩa endpoint
│   └── cdp_connection.py  # Hàm connect_to_chrome_via_cdp
├── core/
│   └── automation.py      # PlaywrightAutomation (launch/connect_over_cdp)
├── models/
│   ├── input.py           # SearchInput / ViewportConfig (dùng nội bộ)
│   └── output.py          # save_json helper
└── utils/
    └── heyetsy_parser.py  # extract_heyetsy_data helper
```

## 2. User Stories & Test Ideas (rút gọn)

### 2.1. User Story: Kiểm tra 1 shipment

**As a** backend service

**I want to** gửi 1 USPS tracking link tới API

**So that** tôi biết shipment đó đã delivered hay chưa

**Test cases** (ý tưởng):

-   TC_001: Tracking hợp lệ, trạng thái delivered, có `delivered_at`
-   TC_002: Tracking hợp lệ, chưa delivered, `delivered_at` = null
-   TC_003: Tracking link rỗng → HTTP 400

### 2.2. User Story: Kiểm tra nhiều shipments (batch)

**As a** backend service

**I want to** gửi danh sách shipments trong 1 request

**So that** tôi giảm round-trips và xử lý theo lô

**Test cases** (ý tưởng):

-   TC_010: 2 shipments hợp lệ → trả về đúng thứ tự input
-   TC_011: 1 valid, 1 invalid URL → valid OK, invalid có `delivered=false`, `delivered_at=null`
-   TC_012: Mảng rỗng → HTTP 400

## 3. Đối tượng test chính

### 3.1. `connect_to_chrome_via_cdp` (trong `cdp_connection.py`)

-   Kết nối được tới Chrome qua endpoint CDP
-   Điều hướng tới tracking URL
-   Đọc `document.body.innerText`
-   Tìm đủ các cụm từ required_phrases
-   Lấy `delivered_date` từ `.delivered-status .tb-date` nếu có

### 3.2. Endpoint `/api/v1/cdp/auto-check-tracking`

-   Validate input: `shipment_id` không rỗng, `tracking_link` không rỗng
-   Gọi `connect_to_chrome_via_cdp` lần lượt cho từng shipment
-   Đảm bảo thứ tự kết quả giống thứ tự input
-   Log rõ ràng từng shipment (phục vụ debug)

## 4. Hướng test (high level)

Do phần lớn logic phụ thuộc vào thực tế trang USPS + Chrome thật, TDD dạng full-mock có thể phức tạp. Thay vào đó:

-   Viết **integration tests** đơn giản chạy với Chrome CDP thật (có thể chạy thủ công khi cần)
-   Với unit test, có thể mock `PlaywrightAutomation` nếu muốn, nhưng không bắt buộc cho use case nhỏ này

File này chỉ giữ vai trò mô tả ý tưởng test để tham khảo, toàn bộ nội dung cũ liên quan tới n8n, `server_playwright.py`, `main.py`, `actions.py`, `extractor.py` đã được loại bỏ để phù hợp kiến trúc mới.

## 5. HeyEtsy scraper (cdp_connection.py) - Test ideas

- Khi parse HTML mẫu, `extract_heyetsy_data` bỏ video listing và bỏ `total_sold <= 5`.
- Gộp kết quả duy nhất theo `listing_id` khi nhiều trang chứa cùng listing.
- Lưu đúng định dạng JSON (UTF-8, indent=2) vào `captured_data.json` thông qua `save_json`.
- Đường dẫn output tồn tại và được ghi khi Chrome/CDP không lỗi.
