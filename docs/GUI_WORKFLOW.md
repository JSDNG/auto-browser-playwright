# Luồng hoạt động - Etsy Crawler GUI App

## Tổng quan

App là desktop application với GUI, chạy FastAPI server trong background và có system tray icon.

## Luồng hoạt động

```
1. User tải app (.exe cho Windows, .dmg cho Mac)
   ↓
2. User cài đặt và chạy app
   ↓
3. App hiển thị GUI window + system tray icon
   ↓
4. FastAPI server tự động khởi động (localhost:5674)
   ↓
5. User nhập thông tin vào form:
   - Keyword (từ khóa tìm kiếm)
   - Pages (số trang)
   - Created date months (lọc theo tháng)
   - Webhook URL
   - CDP Port
   ↓
6. User bấm "Lưu cấu hình" → Lưu vào config.ini
   ↓
7. User bấm "Spy Etsy"
   ↓
8. App kiểm tra Chrome CDP port:
   - Nếu chưa chạy → Tự động launch Chrome với CDP
   - Nếu đã chạy → Tiếp tục
   ↓
9. App thực hiện spy Etsy:
   - Kết nối Chrome qua CDP
   - Navigate từng trang Etsy
   - Parse dữ liệu HeyEtsy
   - Gửi kết quả về webhook
   ↓
10. Hiển thị kết quả trong GUI:
    - Số lượng sản phẩm đã spy
    - Log chi tiết
    - Notification qua tray icon
```

## Cấu trúc GUI

### Main Window
- **Form config**: Nhập keyword, pages, filter, webhook, CDP port
- **Buttons**: "Lưu cấu hình", "Spy Etsy"
- **Status label**: Hiển thị trạng thái hiện tại
- **Log output**: Hiển thị log chi tiết
- **Chrome status**: Hiển thị trạng thái Chrome CDP

### System Tray
- **Icon**: Hiển thị trong system tray
- **Menu**: "Hiển thị", "Thoát"
- **Notification**: Thông báo khi spy hoàn thành

## Tự động launch Chrome

Khi user bấm "Spy Etsy":
1. Kiểm tra Chrome CDP có đang chạy không
2. Nếu chưa có:
   - Tự động tìm Chrome executable
   - Launch Chrome với `--remote-debugging-port=$PORT`
   - Đợi Chrome khởi động xong
3. Tiếp tục spy

## Lưu config

- Config được lưu vào `config.ini` trong thư mục app
- Format: INI file (dễ chỉnh sửa)
- User có thể chỉnh sửa trực tiếp file hoặc qua GUI

## FastAPI Server

- Chạy trong background thread
- Port: 5674 (có thể config trong config.ini)
- Vẫn có thể gọi API qua HTTP nếu cần
- Swagger UI: http://localhost:5674/docs

