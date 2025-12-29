Etsy Crawler - Mac Installation

Cảm ơn bạn đã tải Etsy Crawler!

YÊU CẦU HỆ THỐNG:
==================

1. Google Chrome chính chủ
   - Chrome phải được cài đặt trên hệ thống
   - Download từ: https://www.google.com/chrome/

2. Extension HeyEtsy
   - Cài extension vào Chrome profile
   - Có thể cài thủ công hoặc app sẽ tự động cài

3. Playwright Browsers
   - Mở Terminal
   - Chạy lệnh: playwright install chromium
   - Hoặc: python3 -m playwright install chromium

CÁCH CÀI ĐẶT:
=============

1. Mở file .dmg
2. Kéo EtsyCrawler.app vào thư mục Applications
3. Mở Applications và double-click EtsyCrawler.app
4. Nếu Mac báo "App không thể mở", làm theo:
   - System Preferences → Security & Privacy
   - Click "Open Anyway" bên cạnh thông báo
   - Hoặc: Right-click app → Open

CÁCH SỬ DỤNG:
=============

1. Khởi động Chrome với CDP:
   - Mở Terminal
   - Chạy: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
   - Hoặc dùng script: bash scripts/start_chrome_with_cdp.sh
   - Đảm bảo Chrome đã có extension HeyEtsy được cài

2. Chạy Etsy Crawler:
   - Double-click EtsyCrawler.app
   - Hoặc chạy từ Terminal: /Applications/EtsyCrawler.app/Contents/MacOS/EtsyCrawler

3. API Server sẽ chạy tại: http://localhost:5674
   - Swagger UI: http://localhost:5674/docs
   - ReDoc: http://localhost:5674/redoc

CẤU HÌNH:
=========

Chỉnh sửa file config.ini trong thư mục app để:
- Nhập từ khóa cần spy (keyword)
- Số trang cần spy (pages)
- Số tháng để lọc ngày đăng (created_date_months)
- Thay đổi webhook URL
- Thay đổi port API và CDP

HỖ TRỢ:
========

Nếu gặp vấn đề, vui lòng kiểm tra:
- Logs trong Console.app
- Chrome đã được khởi động với CDP chưa
- Playwright browsers đã được cài chưa

