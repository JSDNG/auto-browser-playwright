## Hướng dẫn triển khai API trên Windows với domain ngoài

Tài liệu này hướng dẫn bạn biến `api_server.py` thành dịch vụ Windows chạy nền (không cần mở VS Code) và public qua domain ngoài.

---

## 1. Kiến trúc tổng quan

- **Ứng dụng Python**: `src/app/api_server.py`
  - FastAPI + Uvicorn.
  - Lắng nghe trên `0.0.0.0:5674` (xem cuối file):
    - `uvicorn.run(app, host="0.0.0.0", port=5674)`
  - Cung cấp các endpoints:
    - `/api/v1/etsy/scrape` - Etsy scraping qua CDP
    - `/api/v1/etsy/scrape_hidemyacc` - Etsy scraping với HideMyAcc profile
- **Chrome**:
  - Phải khởi động với `--remote-debugging-port=9223` (cho CDP connection endpoints).
- **HideMyAcc** (nếu dùng endpoint HideMyAcc):
  - Cài đặt HideMyAcc application
  - Profiles tại `~/.hidemyacc/profiles/`
- **Domain ngoài**:
  - Domain trỏ về IP máy/server.
  - Reverse proxy (Nginx/Caddy/IIS/Cloudflare Tunnel/ngrok) forward request đến `http://127.0.0.1:5674`.

---

## 2. Kiểm tra & chuẩn bị code

File chính: `src/app/api_server.py`

- Event loop cho Windows đã được cấu hình đúng:

```python
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

- Ứng dụng FastAPI được tạo và mount router:

```python
app = FastAPI(
    title="HideMyAcc Automation API",
    description="API đơn giản để khởi động HideMyAcc profile + Chrome/Marco và kết nối Playwright qua CDP",
    version="1.0.0"
)

app.include_router(api_router)
```

- Entry point chạy Uvicorn:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5674)
```

**Lưu ý:**
- Host `0.0.0.0` cho phép reverse proxy trên cùng máy truy cập được.
- Port mặc định: `5674`. Bạn có thể đổi port này, nhưng nhớ cập nhật lại cấu hình reverse proxy / tunnel.

---

## 3. Chuẩn bị môi trường Python trên Windows

Giả sử bạn đặt project ở:

- `C:\Users\dragon\Downloads\auto-browser-playwright\auto-browser-playwright`

### 3.1. Tạo virtualenv (khuyến nghị)

Mở **Command Prompt** hoặc **PowerShell**:

```bash
cd C:\auto-browser-playwright
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2. Chạy API bằng file `start_auto_check_tracking.bat`

Giả sử bạn đang ở thư mục gốc project (chứa file `start_auto_check_tracking.bat`):

```bat
start_auto_check_tracking.bat
```

Nội dung file:

```bat
@echo off

REM kích hoạt venv (đúng tên: venv)
call venv\Scripts\activate

REM chạy API server
python src\app\api_server.py

pause
```

- Cửa sổ terminal sẽ mở và API FastAPI chạy trên `http://127.0.0.1:5674`.
- Bạn có thể mở: `http://127.0.0.1:5674/docs` để xem Swagger UI.
- Đừng đóng cửa sổ này nếu muốn API tiếp tục chạy.

Nếu có lỗi, sửa cho chạy ổn **trước khi** triển khai reverse proxy / domain ngoài.

---

## 4. Khởi động Chrome với CDP (remote debugging)

**Lưu ý:** Chỉ cần thiết nếu bạn sử dụng endpoint:
- `/api/v1/etsy/scrape` - Etsy scraping qua CDP

**Không cần thiết** nếu chỉ dùng `/api/v1/etsy/scrape_hidemyacc` (HideMyAcc tự động launch browser).

### 4.1. Khởi động Chrome với CDP

Ví dụ trên Windows:

```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\temp\chrome-debug"
```

Gợi ý:

- Tạo một shortcut trên Desktop hoặc `.bat` file:

```bat
@echo off
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\temp\chrome-debug"
```

- Nếu bạn muốn Chrome cũng chạy “nền” trên server, có thể:
  - Dùng Task Scheduler để tự start Chrome khi login.
  - Hoặc tạo một service riêng cho Chrome bằng công cụ phù hợp khác (cao cấp hơn, chỉ làm khi cần).

### 4.2. Cài đặt HideMyAcc (nếu dùng endpoint HideMyAcc)

Nếu bạn sử dụng endpoint `/api/v1/etsy/scrape_hidemyacc`:

1. Cài đặt HideMyAcc application trên Windows
2. Tạo profiles trong HideMyAcc
3. Profiles sẽ được lưu tại: `C:\Users\<username>\.hidemyacc\profiles\`
4. Marco browser sẽ được tự động tìm trong: `C:\Users\<username>\.hidemyacc\browser\`

Xem `docs/ETSY_SCRAPING_API.md` để biết chi tiết về HideMyAcc endpoints.

---

## 5. Mở firewall cho port 5674 (nếu cần)

Để cho reverse proxy hoặc máy khác trong mạng truy cập được, đảm bảo Windows Firewall cho phép inbound port `5674`:

1. Vào **Windows Defender Firewall with Advanced Security**.
2. Inbound Rules → New Rule.
3. Chọn **Port** → TCP → Specific local ports: `5674`.
4. Allow the connection.
5. Áp dụng cho profile phù hợp (Domain/Private/Public).
6. Đặt tên rule, ví dụ: `AutoBrowserAPI_5674`.

---

## 6. Public API qua domain ngoài

### 7.1. Trường hợp server Windows có IP public / HTTPS do domain provider xử lý

Giả sử (theo môi trường thực tế của bạn):

- Domain: `spyetsy.supover.com`.
- Server Windows (hoặc máy trong LAN) có IP: `192.168.1.94`.
- API local trên máy đó: `http://127.0.0.1:5674`.

#### Bước DNS

- Vào quản lý DNS (Cloudflare, Namecheap, v.v.).
- Tạo bản ghi:
  - **Type**: `A`
  - **Name**: `spyetsy.supover.com`
  - **Value**: IP nơi có thể truy cập tới máy `192.168.1.94`
    - Nếu bạn dùng trực tiếp IP public: nhập IP public (router sẽ NAT về 192.168.1.94).
    - Nếu chỉ dùng trong mạng LAN (không ra Internet): bạn có thể dùng DNS nội bộ hoặc file hosts.
  - TTL: auto hoặc 5–10 phút.

#### Bước reverse proxy (Nginx trên Windows, cấu hình tách file riêng `spy_etsy.conf`)

Ý tưởng: **không sửa nhiều vào `nginx.conf` mặc định**, mà:

- Đảm bảo trong `http { ... }` của `nginx.conf` có dòng:

```nginx
http {
    # ...
    include       conf.d/*.conf;
}
```

- Mỗi project tạo **một file riêng** trong `conf.d`, ví dụ:
  - `C:\nginx\conf\conf.d\spy_etsy.conf`

1. Cài Nginx cho Windows trên chính máy `192.168.1.94` (ví dụ tại `C:\nginx`).
2. Tạo thư mục `C:\nginx\conf\conf.d\` nếu chưa có.
3. Tạo file mới: `C:\nginx\conf\conf.d\spy_etsy.conf` với nội dung:

```nginx
server {
    listen 80;
    server_name spyetsy.supover.com;

    location / {
        proxy_pass http://127.0.0.1:5674;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

4. Reload/restart Nginx:

```bash
cd C:\nginx
nginx -s reload
```

**Các lệnh kiểm tra nginx có thể dùng:**

- **Kiểm tra cấu hình nginx có đúng không** (trước khi reload):
```bash
cd C:\nginx
nginx -t
```
  - Nếu OK: sẽ hiển thị `nginx: configuration file ... test is successful`
  - Nếu có lỗi: sẽ hiển thị lỗi cụ thể, cần sửa trước khi reload

- **Kiểm tra nginx đang chạy:**
```bash
tasklist | findstr nginx
```
  - Hoặc kiểm tra trong Task Manager (Ctrl+Shift+Esc) → tìm process `nginx.exe`

- **Kiểm tra port 80 có đang listen:**
```bash
netstat -ano | findstr :80
```
  - Hoặc dùng PowerShell:
```powershell
Get-NetTCPConnection -LocalPort 80
```

- **Xem log nginx nếu có lỗi:**
```bash
type C:\nginx\logs\error.log
```
  - Hoặc mở file `C:\nginx\logs\error.log` bằng Notepad

- **Restart nginx (nếu reload không được):**
```bash
cd C:\nginx
nginx -s stop
nginx
```

- **Kiểm tra DNS đã trỏ đúng chưa:**
```bash
nslookup spyetsy.supover.com
```
  - Hoặc:
```bash
ping spyetsy.supover.com
```

- **Test kết nối từ local đến API backend:**
```bash
curl http://127.0.0.1:5674/docs
```
  - Hoặc mở trình duyệt: `http://127.0.0.1:5674/docs`

- **Test qua nginx (từ local):**
```bash
curl http://localhost/docs
```
  - Hoặc mở trình duyệt: `http://localhost/docs`

5. Kiểm tra:
   - Nếu domain provider đang terminate SSL (ví dụ Cloudflare Full/Proxied):
     - Truy cập `https://spyetsy.supover.com/docs` từ ngoài Internet.
   - Nếu chỉ dùng HTTP nội bộ:
     - Truy cập `http://spyetsy.supover.com/docs` trong mạng tương ứng.

## 7. Kiểm tra, debug, tối ưu

### 8.1. Kiểm tra nhanh

- `http://127.0.0.1:5674/docs` trên server:
  - Nếu **OK** ở đây nhưng domain ngoài không được → lỗi ở phần reverse proxy / DNS.
  - Swagger UI sẽ hiển thị tất cả endpoints: USPS tracking và Etsy scraping

- **Test Etsy Scraping - CDP Connection:**

```bash
POST /api/v1/etsy/scrape
{
  "keyword": "handmade bag",
  "pages": 2
}
```

- **Test Etsy Scraping - HideMyAcc Profile:**

```bash
POST /api/v1/etsy/scrape_hidemyacc
{
  "profile_id": "hma_xxx",
  "keyword": "handmade bag",
  "pages": 2
}
```

Xem `docs/ETSY_SCRAPING_API.md` để biết chi tiết về Etsy scraping endpoints.

### 8.2. Log & lỗi

- Kiểm tra:
  - `logs/service-out.log`
  - `logs/service-err.log`
- Trong code, logger đã được cấu hình:

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

Bạn có thể:

- Tăng/giảm level log (DEBUG/INFO/WARNING).
- Thêm handler ghi log theo ngày (RotatingFileHandler) nếu log lớn.

### 8.3. Tối ưu hiệu suất

- **Chrome/CDP endpoints:**
  - Đảm bảo Chrome chạy ở chế độ tối ưu (bật headless nếu phù hợp, nếu code Playwright/CDP hỗ trợ).
  - Giảm thời gian chờ nếu không cần chờ lâu (hiện tại Etsy scraping chờ 10 giây mỗi trang).

- **HideMyAcc endpoints:**
  - Browser được launch tự động, không cần Chrome chạy trước.
  - Timeout nên đặt cao hơn (khuyến nghị 600 giây) vì cần thời gian launch browser.

- **Nếu lượng request lớn:**
  - Xem xét chạy nhiều instance service trên các port khác nhau rồi load balance.
  - Hoặc tối ưu logic trong `scrape_etsy_via_cdp` và `scrape_etsy_with_profile`.
  - Lưu ý: Mỗi request xử lý tuần tự, không song song.

---

## 8. Tóm tắt quy trình triển khai

1. **Cài đặt môi trường:**
   - Cài Python + tạo venv + `pip install -r requirements.txt`
   - Cài Playwright browsers: `python -m playwright install chromium`
   - (Tùy chọn) Cài HideMyAcc nếu dùng endpoint HideMyAcc

2. **Chạy API:**
   - Chạy API bằng `start_auto_check_tracking.bat` → truy cập `http://127.0.0.1:5674/docs` để kiểm tra
   - Hoặc chạy với uvicorn: `uvicorn src.app.api_server:app --host 0.0.0.0 --port 5674`

3. **Chuẩn bị browser (nếu cần):**
   - **CDP endpoints:** Khởi động Chrome với `--remote-debugging-port=9223`
   - **HideMyAcc endpoints:** Không cần, tự động launch

4. **Mở firewall:**
   - Mở firewall cho port `5674` (nếu cần)

5. **Cấu hình domain:**
   - DNS trỏ về IP server
   - Reverse proxy (Nginx/IIS/Caddy) hoặc Cloudflare Tunnel/ngrok forward đến `http://127.0.0.1:5674`

6. **Kiểm tra:**
   - Truy cập `http(s)://api.yourdomain.com/docs` và test gọi API từ bên ngoài
   - Test các endpoints: USPS tracking, Etsy scraping (CDP và HideMyAcc)

## 9. Tài liệu tham khảo

- **Etsy Scraping API:** Xem `docs/ETSY_SCRAPING_API.md`
- **CDP Connection:** Xem `docs/CDP_CONNECTION.md`
- **API Guide:** Xem `docs/API_GUIDE.md`
- **HideMyAcc Quick Start:** Xem `QUICK_START_HIDEMYACC.md`

