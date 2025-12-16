# Hướng dẫn kết nối Playwright với Chrome đang chạy qua CDP

## Tổng quan

Playwright có thể kết nối với Chrome đang chạy sẵn thông qua **Chrome DevTools Protocol (CDP)** thay vì tạo Chrome instance mới. Điều này hữu ích khi bạn muốn:
- Điều khiển Chrome đã mở sẵn của bạn
- Tái sử dụng session/cookies đã có
- Debug trong Chrome thật thay vì Chrome ảo

## Cách khởi động Chrome với CDP

### Bước 1: Khởi động Chrome với remote debugging port

Chrome cần được khởi động với flag `--remote-debugging-port` để bật CDP server.

#### macOS:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

#### Linux:
```bash
google-chrome --remote-debugging-port=9222
# hoặc
chromium --remote-debugging-port=9222
```

#### Windows:
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

### Bước 2: Xác nhận CDP đang chạy

Mở trình duyệt khác và truy cập: `http://localhost:9222/json`

Bạn sẽ thấy JSON list các tab/windows đang mở. Nếu thấy JSON này nghĩa là CDP đã hoạt động.

### Bước 3: Sử dụng trong code

```python
from src.core.automation import PlaywrightAutomation

automation = PlaywrightAutomation()

# Kết nối với Chrome đang chạy qua CDP
await automation.connect_over_cdp("http://localhost:9222")

# Sử dụng như bình thường
await automation.navigate("https://example.com")
```

## Lưu ý quan trọng

1. **Port mặc định**: 9222 là port phổ biến, nhưng bạn có thể dùng port khác
2. **Chỉ một Chrome instance**: Mỗi port chỉ có thể dùng cho một Chrome instance
3. **Security**: CDP không có authentication mặc định, chỉ nên dùng trên localhost
4. **Format endpoint**: 
   - `http://localhost:9222` (Playwright tự convert sang WebSocket)
   - `ws://localhost:9222` (WebSocket trực tiếp)

## Ví dụ đầy đủ

Xem file `src/app/cdp_connection.py` để có ví dụ hoàn chỉnh.

## Troubleshooting

### Lỗi: "Target closed" hoặc "Connection refused"
- Kiểm tra Chrome đã khởi động với `--remote-debugging-port` chưa
- Kiểm tra port có đúng không (mặc định 9222)
- Thử truy cập `http://localhost:9222/json` để xác nhận

### Lỗi: "Protocol error"
- Đảm bảo Chrome version tương thích với Playwright
- Thử restart Chrome với CDP flag

### Không thấy tab hiện có
- `connect_over_cdp()` sẽ tự động tìm context/page hiện có
- Nếu không có, sẽ tạo context/page mới
