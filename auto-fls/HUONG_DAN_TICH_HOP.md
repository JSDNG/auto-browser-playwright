# Hướng Dẫn Tích Hợp và Sử Dụng Dự Án Auto Browser Playwright

## 📋 Mục Lục

1. [Tổng Quan Dự Án](#tổng-quan-dự-án)
2. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
3. [Cài Đặt và Cấu Hình](#cài-đặt-và-cấu-hình)
4. [Tích Hợp HideMyAcc Automation](#tích-hợp-hidemyacc-automation)
5. [Sử Dụng API Server](#sử-dụng-api-server)
6. [Ví Dụ Sử Dụng](#ví-dụ-sử-dụng)
7. [Khắc Phục Sự Cố](#khắc-phục-sự-cố)

---

## 📖 Tổng Quan Dự Án

Dự án **Auto Browser Playwright** là một hệ thống tự động hóa trình duyệt kết hợp:
- **HideMyAcc API**: Quản lý và khởi động browser profiles
- **Playwright**: Tự động hóa trình duyệt qua Chrome DevTools Protocol (CDP)
- **Flask API Server**: RESTful API để điều khiển từ xa

### Tính Năng Chính

✅ **Quản lý HideMyAcc Profiles**: Khởi động/dừng profiles qua API  
✅ **Tự động hóa Playwright**: Điều khiển browser qua CDP  
✅ **RESTful API**: Tích hợp dễ dàng với các hệ thống khác  
✅ **Retry Logic**: Tự động thử lại khi lỗi  
✅ **Backup Profiles**: Tự động chuyển sang profile dự phòng  
✅ **Rate Limiting**: Bảo vệ API khỏi spam  

---

## 📁 Cấu Trúc Dự Án

```
auto-browser-playwright/
├── auto-fls/
│   ├── app/
│   │   ├── __init__.py              # Khởi tạo Flask app
│   │   ├── config.py                # Cấu hình (env variables)
│   │   ├── hma_client.py            # Client gọi HideMyAcc API
│   │   ├── hidemyacc_automation.py  # ⭐ Tích hợp Playwright + HideMyAcc
│   │   ├── routes.py                # API endpoints
│   │   └── utils.py                 # Utility functions
│   ├── server.py                    # Entry point Flask server
│   ├── requirements.txt             # Python dependencies
│   ├── env_template.txt             # Template file .env
│   ├── README.md                    # Tài liệu tiếng Anh
│   ├── README_VI.md                 # Tài liệu tiếng Việt
│   └── HUONG_DAN_TICH_HOP.md        # ⭐ File này
└── docker/                          # Docker configuration (optional)
```

### Mô Tả Các File Quan Trọng

#### 1. `hidemyacc_automation.py` ⭐
File chính để tích hợp HideMyAcc với Playwright:
- Class `HideMyAccPlaywright`: Wrapper để tự động hóa
- Kết nối Playwright qua CDP với HideMyAcc browser
- Hỗ trợ cả SDK Python và HTTP API

#### 2. `hma_client.py`
Client để giao tiếp với HideMyAcc API:
- Start/stop profiles
- Quản lý profiles
- Health checks

#### 3. `server.py`
Flask server chính:
- Khởi động API server
- Auto-start HideMyAcc profile khi server start
- Background cleanup tasks

#### 4. `routes.py`
API endpoints:
- `GET /api/v1/health`: Health check
- `POST /api/v1/start-flash-sale`: Khởi động profile
- `POST /api/v1/stop-profile`: Dừng profile

---

## 🛠️ Cài Đặt và Cấu Hình

### Yêu Cầu Hệ Thống

- Python 3.11+
- HideMyAcc Desktop Application (đã cài đặt và chạy)
- HideMyAcc API Server (port 2268 mặc định)

### Bước 1: Cài Đặt Dependencies

```bash
cd auto-fls
pip install -r requirements.txt
```

**Dependencies chính:**
- `playwright`: Browser automation
- `flask`: Web framework
- `requests`: HTTP client
- `loguru`: Logging
- `python-dotenv`: Environment variables

### Bước 2: Cấu Hình Environment

```bash
# Copy template
cp env_template.txt .env

# Chỉnh sửa .env
```

**File `.env` quan trọng:**

```env
# HideMyAcc API
HMA_API_BASE=http://127.0.0.1:2268
HMA_API_KEY=your-api-key-here  # (optional)

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=5001

# Profile IDs
DEFAULT_PROFILE_ID=6898c8f7effa52a76ed48168
BACKUP_PROFILE_ID=689c58b2effa52a76e7b76be
```

### Bước 3: Khởi Động HideMyAcc

1. Mở ứng dụng **HideMyAcc Desktop**
2. Đảm bảo **API Server** đang chạy (thường port 2268)
3. Kiểm tra kết nối:
   ```bash
   curl http://127.0.0.1:2268/status
   ```

### Bước 4: Cài Đặt Playwright Browsers

```bash
playwright install chromium
```

---

## 🔗 Tích Hợp HideMyAcc Automation

### Cách Hoạt Động

File `hidemyacc_automation.py` kết nối HideMyAcc với Playwright qua **Chrome DevTools Protocol (CDP)**:

```
HideMyAcc Profile → CDP Endpoint → Playwright → Browser Automation
```

### Sửa Lỗi Đã Thực Hiện

#### ❌ Lỗi Cũ:

1. **Sai Port API**: Dùng port `50325` thay vì `2268`
2. **Sai Endpoint**: Dùng `/browser/start` thay vì `/profiles/start/{profile_id}`
3. **Sai Payload**: Gửi `profileId`, `automation`, `debuggingPort` không đúng format
4. **Sai Response Parsing**: Không parse đúng structure `{"code": 1, "data": {...}}`
5. **Sai CDP URL**: Không lấy đúng `wsUrl` từ response

#### ✅ Đã Sửa:

1. ✅ Port đúng: `http://127.0.0.1:2268`
2. ✅ Endpoint đúng: `POST /profiles/start/{profile_id}`
3. ✅ Payload đúng: `{"open_tabs": [...]}` (optional)
4. ✅ Parse response: Lấy `result["data"]` từ response
5. ✅ CDP URL: Lấy từ `wsUrl` trong response data

### Cách Sử Dụng `HideMyAccPlaywright`

#### Ví Dụ 1: Sử Dụng Cơ Bản

```python
import asyncio
from app.hidemyacc_automation import HideMyAccPlaywright

async def main():
    # Khởi tạo
    automation = HideMyAccPlaywright(
        api_key="your-api-key",  # Optional
        base_url="http://127.0.0.1:2268"  # Optional, default
    )
    
    try:
        # 1. Khởi động profile
        profile_id = "6898c8f7effa52a76ed48168"
        await automation.start_profile(profile_id)
        
        # 2. Lấy page
        page = await automation.get_page()
        
        # 3. Automation
        await page.goto("https://www.tiktok.com")
        await page.screenshot(path="tiktok.png")
        
        # 4. Thực hiện các thao tác khác
        # ...
        
    finally:
        # 5. Đóng kết nối
        await automation.close()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Ví Dụ 2: Với Options

```python
async def main():
    automation = HideMyAccPlaywright()
    
    # Khởi động với options
    options = {
        "open_tabs": [
            "https://seller.tiktok.com",
            "https://www.etsy.com"
        ]
    }
    
    await automation.start_profile("6898c8f7effa52a76ed48168", options)
    page = await automation.get_page()
    
    # Page đã mở sẵn các tabs
    # ...
    
    await automation.close()
```

#### Ví Dụ 3: Scraping Etsy

```python
async def scrape_etsy():
    automation = HideMyAccPlaywright()
    
    try:
        await automation.start_profile("6898c8f7effa52a76ed48168")
        page = await automation.get_page()
        
        # Navigate
        await page.goto("https://www.etsy.com/search?q=trending")
        await page.wait_for_selector(".wt-grid__item-xs-6", timeout=10000)
        
        # Scrape
        products = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.wt-grid__item-xs-6');
                return Array.from(items).slice(0, 5).map(item => {
                    const title = item.querySelector('h3')?.textContent?.trim();
                    const price = item.querySelector('.currency-value')?.textContent?.trim();
                    const link = item.querySelector('a')?.href;
                    return { title, price, link };
                });
            }
        """)
        
        for product in products:
            print(f"{product['title']} - ${product['price']}")
            
    finally:
        await automation.close()
```

---

## 🌐 Sử Dụng API Server

### Khởi Động Server

```bash
cd auto-fls
python server.py
```

Server sẽ chạy tại: `http://localhost:5001`

### API Endpoints

#### 1. Health Check

```bash
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "hma_server": "connected",
  "active_profiles": 1,
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. Start Flash Sale (Khởi động Profile)

```bash
POST /api/v1/start-flash-sale
Content-Type: application/json

{
  "profile_id": "6898c8f7effa52a76ed48168",  # Optional
  "open_tabs": ["https://seller.tiktok.com"],  # Optional
  "use_backup": true  # Optional, default true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Flash Sale started successfully",
  "data": {
    "session_id": "session_...",
    "profile_id": "6898c8f7effa52a76ed48168",
    "port": 36807,
    "ws_url": "ws://127.0.0.1:36807/devtools/browser/...",
    "user_agent": "Mozilla/5.0...",
    "started_at": "2024-01-01T12:00:00",
    "flash_sale_status": "started"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 3. Stop Profile

```bash
POST /api/v1/stop-profile
Content-Type: application/json

{
  "profile_id": "6898c8f7effa52a76ed48168"
}
```

### Ví Dụ Sử Dụng API

#### Python

```python
import requests

# Start profile
response = requests.post(
    "http://localhost:5001/api/v1/start-flash-sale",
    json={
        "open_tabs": ["https://seller.tiktok.com"]
    }
)

if response.status_code == 200:
    data = response.json()["data"]
    print(f"Profile started on port: {data['port']}")
    print(f"WebSocket: {data['ws_url']}")
```

#### cURL

```bash
# Health check
curl http://localhost:5001/api/v1/health

# Start profile
curl -X POST http://localhost:5001/api/v1/start-flash-sale \
  -H "Content-Type: application/json" \
  -d '{"open_tabs": ["https://seller.tiktok.com"]}'

# Stop profile
curl -X POST http://localhost:5001/api/v1/stop-profile \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "6898c8f7effa52a76ed48168"}'
```

---

## 💡 Ví Dụ Sử Dụng

### Kết Hợp API Server + Playwright Automation

```python
import asyncio
import requests
from app.hidemyacc_automation import HideMyAccPlaywright

async def automated_workflow():
    """Workflow tự động: Start profile → Automation → Stop"""
    
    # Bước 1: Start profile qua API
    print("🚀 Starting profile via API...")
    response = requests.post(
        "http://localhost:5001/api/v1/start-flash-sale",
        json={"open_tabs": ["https://seller.tiktok.com"]}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to start profile: {response.text}")
        return
    
    data = response.json()["data"]
    profile_id = data["profile_id"]
    ws_url = data["ws_url"]
    
    print(f"✅ Profile started: {profile_id}")
    print(f"🔗 WebSocket: {ws_url}")
    
    # Bước 2: Kết nối Playwright
    automation = HideMyAccPlaywright()
    try:
        # Sử dụng profile đã start
        await automation.start_profile(profile_id)
        page = await automation.get_page()
        
        # Bước 3: Automation
        print("🤖 Starting automation...")
        await page.goto("https://seller.tiktok.com")
        await page.wait_for_load_state("networkidle")
        
        # Thực hiện các thao tác
        # ...
        
        print("✅ Automation completed!")
        
    finally:
        # Bước 4: Cleanup
        await automation.close()
        
        # Stop profile qua API
        requests.post(
            "http://localhost:5001/api/v1/stop-profile",
            json={"profile_id": profile_id}
        )

if __name__ == "__main__":
    asyncio.run(automated_workflow())
```

### Tự Động Hóa TikTok Seller

```python
async def automate_tiktok_seller():
    automation = HideMyAccPlaywright()
    
    try:
        # Start với TikTok Seller URL
        await automation.start_profile(
            "6898c8f7effa52a76ed48168",
            options={"open_tabs": ["https://seller-us.tiktok.com/product"]}
        )
        
        page = await automation.get_page()
        
        # Đợi page load
        await page.wait_for_load_state("networkidle")
        
        # Login (nếu cần)
        # await page.fill("#username", "your-username")
        # await page.fill("#password", "your-password")
        # await page.click("button[type='submit']")
        
        # Navigate to products
        await page.goto("https://seller-us.tiktok.com/product")
        
        # Scrape hoặc thao tác
        # ...
        
    finally:
        await automation.close()
```

---

## 🚨 Khắc Phục Sự Cố

### Lỗi Thường Gặp

#### 1. "Cannot connect to HMA server"

**Nguyên nhân:**
- HideMyAcc chưa chạy
- Port 2268 bị chặn
- Firewall chặn kết nối

**Giải pháp:**
```bash
# Kiểm tra HideMyAcc đang chạy
curl http://127.0.0.1:2268/status

# Kiểm tra port
netstat -an | grep 2268
```

#### 2. "Profile not found" hoặc "Invalid profile ID"

**Nguyên nhân:**
- Profile ID sai
- Profile không tồn tại

**Giải pháp:**
```python
# List profiles để lấy đúng ID
import requests
response = requests.get("http://127.0.0.1:2268/profiles")
print(response.json())
```

#### 3. "CDP không sẵn sàng"

**Nguyên nhân:**
- Profile chưa start xong
- Port CDP bị conflict

**Giải pháp:**
- Đợi thêm vài giây sau khi start profile
- Kiểm tra port trong response có đúng không

#### 4. "Playwright connection failed"

**Nguyên nhân:**
- wsUrl không đúng format
- CDP endpoint không accessible

**Giải pháp:**
```python
# Debug: In ra wsUrl
print(f"WebSocket URL: {ws_url}")

# Kiểm tra CDP endpoint
import requests
cdp_check = ws_url.replace("ws://", "http://").split("/devtools")[0]
response = requests.get(f"{cdp_check}/json/version")
print(response.json())
```

### Debug Mode

Bật debug để xem chi tiết:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Hoặc trong .env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Kiểm Tra Logs

```bash
# Logs ứng dụng
tail -f auto-fls/logs/auto_fls.log

# Logs server
python server.py  # Xem console output
```

---

## 📚 Tài Liệu Tham Khảo

### HideMyAcc API

- **Base URL**: `http://127.0.0.1:2268`
- **Start Profile**: `POST /profiles/start/{profile_id}`
- **Stop Profile**: `POST /profiles/stop/{profile_id}`
- **List Profiles**: `GET /profiles`
- **Profile Status**: `GET /profiles/{profile_id}/status`

### Playwright CDP

- **Documentation**: https://playwright.dev/python/docs/api/class-browser#browser-connect-over-cdp
- **CDP Endpoint**: `http://localhost:{port}/json/version`

### Response Format

HideMyAcc API trả về:
```json
{
  "code": 1,
  "data": {
    "port": 36807,
    "wsUrl": "ws://127.0.0.1:36807/devtools/browser/...",
    "userAgent": "Mozilla/5.0...",
    "success": true
  }
}
```

---

## ✅ Checklist Tích Hợp

- [ ] Cài đặt Python 3.11+
- [ ] Cài đặt HideMyAcc Desktop
- [ ] Cài đặt dependencies (`pip install -r requirements.txt`)
- [ ] Cấu hình `.env` file
- [ ] Khởi động HideMyAcc API Server
- [ ] Test kết nối: `curl http://127.0.0.1:2268/status`
- [ ] Cài đặt Playwright browsers: `playwright install chromium`
- [ ] Test `hidemyacc_automation.py` với profile ID
- [ ] Khởi động Flask server: `python server.py`
- [ ] Test API: `curl http://localhost:5001/api/v1/health`

---

## 🎯 Kết Luận

Dự án này cung cấp:
1. ✅ **HideMyAcc Integration**: Quản lý profiles qua API
2. ✅ **Playwright Automation**: Tự động hóa browser qua CDP
3. ✅ **RESTful API**: Tích hợp dễ dàng
4. ✅ **Error Handling**: Retry logic và backup profiles

File `hidemyacc_automation.py` đã được sửa để:
- ✅ Sử dụng đúng HideMyAcc API (port 2268, endpoints đúng)
- ✅ Parse response đúng format
- ✅ Kết nối Playwright qua CDP chính xác

**Bắt đầu sử dụng ngay:**
```python
from app.hidemyacc_automation import HideMyAccPlaywright

automation = HideMyAccPlaywright()
await automation.start_profile("your-profile-id")
page = await automation.get_page()
# ... automation code ...
await automation.close()
```

---

**Tác giả**: Auto Browser Playwright Team  
**Cập nhật**: 2024  
**Version**: 1.0.0
