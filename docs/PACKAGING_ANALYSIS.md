# Phân tích Đóng gói App - Etsy Auto Crawler

## Tổng quan dự án

**Mục đích**: Đóng gói dự án thành desktop app để:
- Auto crawler Etsy
- Sử dụng Chrome chính chủ (không bị chặn)
- Kế thừa extension HeyEtsy (cài trong Chrome chính chủ)
- Hỗ trợ Windows và Mac

**Kiến trúc hiện tại**:
- FastAPI server (Python)
- Playwright điều khiển Chrome chính chủ qua CDP
- Extension HeyEtsy được cài trong Chrome profile
- Parse dữ liệu từ extension HeyEtsy overlay

---

## Phương án: PyInstaller

### ✅ Ưu điểm
- **Đơn giản**: Chỉ cần thêm PyInstaller, không thay đổi code
- **Nhanh**: 1-2 tuần để hoàn thành
- **Phù hợp**: Background service/CLI, không cần GUI
- **Hỗ trợ đa nền tảng**: Windows, Mac, Linux
- **Standalone**: Executable độc lập, không cần Python runtime

### ❌ Nhược điểm
- Không có GUI (chỉ console/background)
- File size ~100-200MB
- Startup hơi chậm (unpacking)

### Cấu trúc output
```
EtsyCrawler.exe (Windows) hoặc EtsyCrawler (Mac)
├── Executable (standalone)
├── config.json (optional)
└── logs/ (tự tạo khi chạy)
```

### Yêu cầu user
1. Cài Chrome chính chủ (system Chrome)
2. Cài extension HeyEtsy vào Chrome profile
3. Chạy `playwright install chromium` (hoặc bundle vào app)
4. Khởi động Chrome với CDP: `--remote-debugging-port=9223`

---

### Tại sao chọn PyInstaller
1. ✅ Đơn giản, nhanh (1-2 tuần)
2. ✅ Không cần thay đổi code hiện tại
3. ✅ Phù hợp với use case (background service/API)
4. ✅ Standalone executable, dễ phân phối

### Workflow
```
User tải app (.exe/.dmg) → Cài đặt → Chạy app
  ↓
GUI window hiển thị + System tray icon
  ↓
FastAPI server tự động khởi động (localhost:5674)
  ↓
User nhập config vào form → Lưu vào config.ini
  ↓
User bấm "Spy Etsy"
  ↓
App kiểm tra Chrome CDP:
  - Chưa chạy → Tự động launch Chrome với CDP
  - Đã chạy → Tiếp tục
  ↓
App thực hiện spy Etsy qua CDP (Playwright)
  ↓
Chrome có extension HeyEtsy → Parse dữ liệu → Gửi webhook
  ↓
Hiển thị kết quả trong GUI + Notification
```

### Installer
- **Windows**: Inno Setup → `.exe` installer (EtsyCrawler-Setup-1.0.0.exe)
- **Mac**: `hdiutil` hoặc `create-dmg` → `.dmg` file (EtsyCrawler-1.0.0.dmg)

---

## Đánh giá kỹ thuật

### ✅ Phù hợp
- Chrome chính chủ: Dùng system Chrome (không bundle)
- Extension HeyEtsy: Cài trong Chrome profile (user tự cài hoặc app tự động cài)
- Windows & Mac: PyInstaller hỗ trợ cả 2
- Không bị chặn: Dùng Chrome thật với profile thật và extension thật

### ⚠️ Cần lưu ý
- Playwright browsers: Cần cài riêng hoặc bundle (file size lớn)
- Code signing: Cần để tránh warning (Mac/Windows)
- Auto-update: Không có built-in, cần tự implement

### ❌ Không phù hợp
- Docker: Không phù hợp vì cần Chrome GUI
- Headless browser: Không phù hợp vì cần extension

---

## Kết luận

**Phương án**: **PyInstaller**

**Lý do**:
- Đơn giản, nhanh (1-2 tuần)
- Không cần thay đổi code
- Phù hợp với use case (background service/API)
- Standalone executable, dễ phân phối

**Next steps**:
1. Setup PyInstaller
2. Tạo build script
3. Tạo installer:
   - Windows: `.exe` installer (Inno Setup)
   - Mac: `.dmg` file (hdiutil/create-dmg)
4. Test trên máy clean

**Xem hướng dẫn setup**: `SETUP_GUIDE.md`

