Etsy Crawler - Windows Installer

Cảm ơn bạn đã cài đặt Etsy Crawler!

YÊU CẦU HỆ THỐNG:
==================

1. Google Chrome chính chủ
   - Chrome phải được cài đặt trên hệ thống
   - Download từ: https://www.google.com/chrome/

2. Extension HeyEtsy
   - Cài extension vào Chrome profile
   - Có thể cài thủ công hoặc app sẽ tự động cài

3. Playwright Browsers
   - Sau khi cài đặt, mở Command Prompt (Admin)
   - Chạy lệnh: playwright install chromium
   - Hoặc chạy từ thư mục cài đặt: app\playwright_install.bat

CÁCH SỬ DỤNG:
=============

1. Khởi động Chrome với CDP:
   - Mở Command Prompt
   - Chạy: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223
   - Hoặc dùng script: scripts\start_chrome_with_cdp.bat
   - Đảm bảo Chrome đã có extension HeyEtsy được cài

2. Chạy Etsy Crawler:
   - Double-click EtsyCrawler.exe
   - Hoặc chạy từ Command Prompt: app\EtsyCrawler.exe

3. API Server sẽ chạy tại: http://localhost:5674
   - Swagger UI: http://localhost:5674/docs
   - ReDoc: http://localhost:5674/redoc

CẤU HÌNH:
=========

Chỉnh sửa file config.ini trong thư mục cài đặt để:
- Nhập từ khóa cần spy (keyword)
- Số trang cần spy (pages)
- Số tháng để lọc ngày đăng (created_date_months)
- Thay đổi webhook URL
- Thay đổi port API và CDP

HỖ TRỢ:
========

Nếu gặp vấn đề, vui lòng kiểm tra:
- Logs trong thư mục logs\
- Chrome đã được khởi động với CDP chưa
- Playwright browsers đã được cài chưa

