# Hướng Dẫn Cài Đặt Etsy Crawler (Dùng Nội Bộ)

## 📦 Yêu Cầu Hệ Thống

### Bắt Buộc:
1. **macOS 10.13 trở lên**
2. **Google Chrome** - Phải cài đặt trên máy
   - Download: https://www.google.com/chrome/
   - App sẽ tự động tìm và sử dụng Chrome đã cài

### Không Cần:
- ❌ **KHÔNG cần** cài Python
- ❌ **KHÔNG cần** cài Playwright browsers (app dùng Chrome hệ thống)
- ❌ **KHÔNG cần** cài dependencies khác

## 🚀 Cách Cài Đặt (3 Bước Đơn Giản)

### Bước 1: Mở file DMG
- Double-click file `EtsyCrawler-1.0.0.dmg`
- Cửa sổ sẽ hiện ra với icon EtsyCrawler.app

### Bước 2: Kéo App vào Applications
- Kéo `EtsyCrawler.app` vào thư mục `Applications` (hoặc kéo vào icon Applications trong cửa sổ DMG)
- Đợi copy xong

### Bước 3: Mở App
- Vào `Applications` folder
- Double-click `EtsyCrawler.app`
- **Lần đầu mở:** Mac có thể hiện cảnh báo bảo mật

#### Nếu Mac báo "App không thể mở":
1. Vào **System Settings** → **Privacy & Security**
2. Tìm thông báo về EtsyCrawler
3. Click **"Open Anyway"**
4. Hoặc: Right-click app → **Open** → Click **Open** trong dialog

## ✅ Kiểm Tra Cài Đặt Thành Công

Sau khi mở app, bạn sẽ thấy:
- ✅ Cửa sổ GUI của Etsy Crawler hiện ra
- ✅ API Server chạy tại: http://localhost:5674
- ✅ Swagger UI: http://localhost:5674/docs

## 🔧 Cấu Hình

Tất cả cấu hình được thực hiện qua **giao diện GUI**:

1. Mở `EtsyCrawler.app` → Cửa sổ GUI sẽ hiện ra
2. Trong form cấu hình, nhập:
   - **Từ khóa** (keyword): Ví dụ: "handmade bag"
   - **Số trang** (pages): Số trang cần spy (1-20)
   - **Lọc theo tháng** (created_date_months): Số tháng để lọc ngày đăng (1-12)
   - **CDP Port**: Port để kết nối Chrome (mặc định: 9223)
3. Click **"Lưu cấu hình"** để lưu vào config.ini
4. Click **"Spy Etsy"** để bắt đầu spy

**Lưu ý:** Không cần chỉnh sửa file `config.ini` trực tiếp. Tất cả được quản lý qua GUI.

## 📝 Sử Dụng

### Cách 1: Dùng GUI (Khuyến nghị)
1. Mở `EtsyCrawler.app`
2. Sử dụng giao diện để cấu hình và chạy

### Cách 2: Dùng API
1. Mở `EtsyCrawler.app` (API server tự động chạy)
2. Truy cập: http://localhost:5674/docs
3. Gọi API endpoints theo nhu cầu

## ⚠️ Lưu Ý Quan Trọng

### Chrome Phải Được Cài Đặt
- App **bắt buộc** cần Google Chrome
- Nếu chưa có Chrome, app sẽ báo lỗi
- Download Chrome: https://www.google.com/chrome/

### Extension HeyEtsy (Nếu Cần)
- Nếu app yêu cầu extension HeyEtsy, cài vào Chrome profile
- App có thể tự động cài hoặc bạn cài thủ công

## 🐛 Xử Lý Lỗi

### Lỗi: "Không tìm thấy Chrome"
**Giải pháp:**
1. Kiểm tra Chrome đã cài: Mở Chrome từ Applications
2. Nếu chưa có: Download và cài Chrome
3. Mở lại EtsyCrawler.app

### Lỗi: "App không thể mở"
**Giải pháp:**
1. System Settings → Privacy & Security → Click "Open Anyway"
2. Hoặc: Right-click app → Open

### Lỗi: "Port 5674 đã được sử dụng"
**Giải pháp:**
1. Đóng app EtsyCrawler đang chạy (kiểm tra trong system tray)
2. Hoặc khởi động lại máy nếu app không đóng được

### Lỗi: App mở nhưng không hiển thị giao diện PyQt6
**Giải pháp:**
1. Kiểm tra Console.app để xem lỗi chi tiết:
   - Mở **Console.app** (Applications → Utilities → Console)
   - Tìm log của `EtsyCrawlerDragonMedia` hoặc `com.etsycrawlerdragonmedia.app`
2. Chạy app từ Terminal để xem output:
   ```bash
   cd /Applications
   ./EtsyCrawlerDragonMedia.app/Contents/MacOS/EtsyCrawlerDragonMedia
   ```
3. Kiểm tra quyền truy cập:
   - System Settings → Privacy & Security → Accessibility
   - Đảm bảo app có quyền truy cập (nếu được yêu cầu)
4. Nếu app chạy từ DMG (read-only):
   - Copy app vào Applications folder trước khi chạy
   - Không chạy trực tiếp từ DMG

## 📞 Hỗ Trợ Nội Bộ

Nếu gặp vấn đề:
1. Kiểm tra Chrome đã cài chưa
2. Kiểm tra app đã được mở thành công chưa
3. Kiểm tra API server có chạy tại http://localhost:5674/docs
4. Liên hệ IT Support nội bộ

## 📋 Checklist Cài Đặt

- [ ] Đã cài Google Chrome
- [ ] Đã mở file DMG
- [ ] Đã kéo app vào Applications
- [ ] Đã mở app thành công (hoặc đã bypass security warning)
- [ ] App hiển thị GUI hoặc API server chạy tại http://localhost:5674/docs

---

**Lưu ý:** Đây là app dùng nội bộ, không cần code signing. Nếu Mac hiện cảnh báo bảo mật, làm theo hướng dẫn ở Bước 3.

