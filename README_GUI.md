# Etsy Crawler - GUI App

## Tổng quan

Etsy Crawler là desktop application với GUI, cho phép tự động crawl dữ liệu từ Etsy sử dụng Chrome chính chủ và extension HeyEtsy.

## Tính năng

- ✅ **GUI Desktop App**: Giao diện đồ họa dễ sử dụng
- ✅ **System Tray Icon**: Chạy ngầm, dễ truy cập
- ✅ **Tự động launch Chrome**: Tự động khởi động Chrome với CDP nếu chưa chạy
- ✅ **Config qua GUI**: Nhập và lưu cấu hình qua form
- ✅ **FastAPI Server**: Vẫn có thể gọi API qua HTTP
- ✅ **Real-time Log**: Hiển thị log chi tiết trong app

## Luồng hoạt động

1. **Tải và cài đặt app**
   - Windows: `EtsyCrawler-Setup-1.0.0.exe`
   - Mac: `EtsyCrawler-1.0.0.dmg`

2. **Chạy app**
   - App hiển thị GUI window
   - System tray icon xuất hiện
   - FastAPI server tự động khởi động (localhost:5674)

3. **Cấu hình**
   - Nhập thông tin vào form:
     - Keyword (từ khóa tìm kiếm)
     - Pages (số trang)
     - Created date months (lọc theo tháng)
     - Webhook URL
     - CDP Port
   - Bấm "Lưu cấu hình" → Lưu vào `config.ini`

4. **Spy Etsy**
   - Bấm nút "Spy Etsy"
   - App kiểm tra Chrome CDP:
     - Nếu chưa chạy → Tự động launch Chrome với CDP
     - Nếu đã chạy → Tiếp tục
   - App thực hiện spy và hiển thị kết quả

## Yêu cầu

- **Chrome chính chủ**: Google Chrome đã cài đặt
- **Extension HeyEtsy**: Cài đặt trong Chrome profile
- **Windows**: Windows 10/11
- **Mac**: macOS 10.14+

## Cấu trúc

```
EtsyCrawler/
├── EtsyCrawler.exe (Windows) hoặc EtsyCrawler (Mac)
├── config.ini (tự tạo khi lưu config)
├── config.ini.example (template)
└── logs/ (tự tạo khi chạy)
```

## Sử dụng

### Lần đầu tiên

1. Chạy app
2. Nhập cấu hình vào form
3. Bấm "Lưu cấu hình"
4. Bấm "Spy Etsy"

### Lần sau

- App tự động load config từ `config.ini`
- Chỉ cần bấm "Spy Etsy"

### System Tray

- Click đúp vào tray icon để mở window
- Right-click để xem menu: "Hiển thị", "Thoát"

## API Server

FastAPI server vẫn chạy trong background, có thể gọi API qua HTTP:

- **Swagger UI**: http://localhost:5674/docs
- **API Endpoint**: http://localhost:5674/api/v1/etsy/spy

Xem `docs/ETSY_SPY_API.md` để biết chi tiết.

## Build

Xem `docs/SETUP_GUIDE.md` để biết cách build app.

## Troubleshooting

### Chrome không tự động launch

- Kiểm tra Chrome đã cài đặt chưa
- Kiểm tra CDP port có bị conflict không
- Thử launch Chrome thủ công với script:
  - Windows: `scripts\start_chrome_with_cdp.bat`
  - Mac: `bash scripts/start_chrome_with_cdp.sh`

### Config không lưu

- Kiểm tra quyền ghi file trong thư mục app
- Kiểm tra `config.ini` có tồn tại không

### Extension HeyEtsy không hoạt động

- Đảm bảo extension đã cài trong Chrome profile
- Kiểm tra extension có bật không
- Xem log trong GUI để biết chi tiết lỗi

