## Hướng dẫn triển khai API CDP trên Windows với domain ngoài

Tài liệu này hướng dẫn bạn biến `api_server.py` thành dịch vụ Windows chạy nền (không cần mở VS Code) và public qua domain ngoài.

---

## 1. Kiến trúc tổng quan

- **Ứng dụng Python**: `src/app/api_server.py`
  - FastAPI + Uvicorn.
  - Lắng nghe trên `0.0.0.0:5673` (xem cuối file):
    - `uvicorn.run(app, host="0.0.0.0", port=5673)`
- **Chrome**:
  - Phải khởi động với `--remote-debugging-port=9222`.
- **Domain ngoài**:
  - Domain trỏ về IP máy/server.
  - Reverse proxy (Nginx/Caddy/IIS/Cloudflare Tunnel/ngrok) forward request đến `http://127.0.0.1:5673`.

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
    title="CDP Connection API",
    description="API để kết nối với Chrome qua CDP và kiểm tra trạng thái delivered",
    version="1.0.0"
)

app.include_router(api_router)
```

- Entry point chạy Uvicorn:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5673)
```

**Lưu ý:**
- Host `0.0.0.0` cho phép reverse proxy trên cùng máy truy cập được.
- Port mặc định: `5673`. Bạn có thể đổi port này, nhưng nhớ cập nhật lại cấu hình reverse proxy / tunnel.

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
copy .env-example .env
```

Chỉnh `.env` nếu port/CDP endpoint khác mặc định (xem bảng trong `README.md`).

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

- Cửa sổ terminal sẽ mở và API FastAPI chạy trên `http://127.0.0.1:5673`.
- Bạn có thể mở: `http://127.0.0.1:5673/docs` để xem Swagger UI.
- Đừng đóng cửa sổ này nếu muốn API tiếp tục chạy.

Nếu có lỗi, sửa cho chạy ổn **trước khi** triển khai reverse proxy / domain ngoài.

---

## 4. Khởi động Chrome với CDP (remote debugging)

API `check_delivery_status` yêu cầu Chrome chạy với cờ `--remote-debugging-port=9222`:

**Command Prompt (cmd.exe):**

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

**PowerShell:** phải thêm toán tử gọi lệnh `&` ở đầu, nếu không sẽ báo lỗi
`Unexpected token '--remote-debugging-port=9222' ...` (PowerShell coi chuỗi
trong ngoặc kép là expression, không phải lệnh để chạy):

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

Gợi ý:

- Tạo một shortcut trên Desktop hoặc `.bat` file:

```bat
@echo off
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

- Nếu bạn muốn Chrome cũng chạy “nền” trên server, có thể:
  - Dùng Task Scheduler để tự start Chrome khi login.
  - Hoặc tạo một service riêng cho Chrome bằng công cụ phù hợp khác (cao cấp hơn, chỉ làm khi cần).

---

## 5. Mở firewall cho port 5673 (nếu cần)

Để cho reverse proxy hoặc máy khác trong mạng truy cập được, đảm bảo Windows Firewall cho phép inbound port `5673`:

1. Vào **Windows Defender Firewall with Advanced Security**.
2. Inbound Rules → New Rule.
3. Chọn **Port** → TCP → Specific local ports: `5673`.
4. Allow the connection.
5. Áp dụng cho profile phù hợp (Domain/Private/Public).
6. Đặt tên rule, ví dụ: `AutoBrowserAPI_5673`.

---

## 6. Public API qua domain ngoài

### 7.1. Trường hợp server Windows có IP public / HTTPS do domain provider xử lý

Giả sử (theo môi trường thực tế của bạn):

- Domain: `tracking.printfamily.com`.
- Server Windows (hoặc máy trong LAN) có IP: `192.168.1.94`.
- API local trên máy đó: `http://127.0.0.1:5673`.

#### Bước DNS

- Vào quản lý DNS (Cloudflare, Namecheap, v.v.).
- Tạo bản ghi:
  - **Type**: `A`
  - **Name**: `tracking.printfamily.com` (hoặc `tracking` tùy giao diện DNS, sao cho trỏ đúng subdomain)
  - **Value**: IP nơi có thể truy cập tới máy `192.168.1.94`
    - Nếu bạn dùng trực tiếp IP public: nhập IP public (router sẽ NAT về 192.168.1.94).
    - Nếu chỉ dùng trong mạng LAN (không ra Internet): bạn có thể dùng DNS nội bộ hoặc file hosts.
  - TTL: auto hoặc 5–10 phút.

#### Bước reverse proxy (Nginx trên Windows, cấu hình tách file riêng `check_tracking.conf`)

Ý tưởng: **không sửa nhiều vào `nginx.conf` mặc định**, mà:

- Đảm bảo trong `http { ... }` của `nginx.conf` có dòng:

```nginx
http {
    # ...
    include       conf.d/*.conf;
}
```

- Mỗi project tạo **một file riêng** trong `conf.d`, ví dụ:
  - `C:\nginx\conf\conf.d\check_tracking.conf`

1. Cài Nginx cho Windows trên chính máy `192.168.1.94` (ví dụ tại `C:\nginx`).
2. Tạo thư mục `C:\nginx\conf\conf.d\` nếu chưa có.
3. Tạo file mới: `C:\nginx\conf\conf.d\check_tracking.conf` với nội dung:

```nginx
server {
    listen 80;
    server_name tracking.printfamily.com;

    location / {
        proxy_pass http://127.0.0.1:5673;
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
nslookup tracking.printfamily.com
```
  - Hoặc:
```bash
ping tracking.printfamily.com
```

- **Test kết nối từ local đến API backend:**
```bash
curl http://127.0.0.1:5673/docs
```
  - Hoặc mở trình duyệt: `http://127.0.0.1:5673/docs`

- **Test qua nginx (từ local):**
```bash
curl http://localhost/docs
```
  - Hoặc mở trình duyệt: `http://localhost/docs`

5. Kiểm tra:
   - Nếu domain provider đang terminate SSL (ví dụ Cloudflare Full/Proxied):
     - Truy cập `https://tracking.printfamily.com/docs` từ ngoài Internet.
   - Nếu chỉ dùng HTTP nội bộ:
     - Truy cập `http://tracking.printfamily.com/docs` trong mạng tương ứng.

## 7. Kiểm tra, debug, tối ưu

### 8.1. Kiểm tra nhanh

- `http://127.0.0.1:5673/docs` trên server:
  - Nếu **OK** ở đây nhưng domain ngoài không được → lỗi ở phần reverse proxy / DNS.
- Gửi request mẫu đến endpoint:

```json
POST /api/v1/cdp/auto-check-tracking
[
  {
    "shipment_id": "123",
    "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
  }
]
```
-

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

- Đảm bảo Chrome chạy ở chế độ tối ưu (bật headless nếu phù hợp, nếu code Playwright/ CDP hỗ trợ).
- Giảm `WAIT_TIME_SECONDS` trong `.env` nếu không cần chờ lâu (mặc định `2`, restart server sau khi đổi).
- Nếu lượng request lớn:
  - Xem xét chạy nhiều instance service trên các port khác nhau rồi load balance.
  - Hoặc tối ưu logic trong `connect_to_chrome_via_cdp`.

---

## 8. Tóm tắt quy trình triển khai

1. Cài Python + tạo venv + `pip install -r requirements.txt`.
2. Chạy API bằng `start_auto_check_tracking.bat` → truy cập `http://127.0.0.1:5673/docs` để kiểm tra.
3. Khởi động Chrome với `--remote-debugging-port=9222`.
4. Mở firewall cho port `5673` (nếu cần).
5. Cấu hình domain:
   - DNS trỏ về IP server.
   - Reverse proxy (Nginx/IIS/Caddy) hoặc Cloudflare Tunnel/ngrok forward đến `http://127.0.0.1:5673`.
6. Kiểm tra `http(s)://api.yourdomain.com/docs` và test gọi API từ bên ngoài.

