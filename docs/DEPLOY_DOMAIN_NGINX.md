# Public API qua domain ngoài (Nginx reverse proxy trên Windows)

Tài liệu này nối tiếp `docs/DEPLOY_WINDOWS.md` — chỉ làm khi API đã **chạy
ổn định ở local** (`http://127.0.0.1:5673/docs` OK). Domain + SSL đã setup
sẵn ở Cloudflare, nên Nginx ở đây chỉ cần forward HTTP đơn giản tới API
local, không cần tự quản lý cert.

```
Internet ──▶ Cloudflare (DNS + SSL) ──▶ Nginx (port 80) ──▶ API local (127.0.0.1:5673)
```

---

## 1. Mở firewall cho port 80

```powershell
New-NetFirewallRule -DisplayName "Nginx_HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

Không cần mở port `5673` (API) hay `9222` (CDP) ra ngoài — Nginx đứng trước rồi.

---

## 2. Cài Nginx

```powershell
Invoke-WebRequest -Uri "https://nginx.org/download/nginx-1.27.4.zip" -OutFile "$env:TEMP\nginx.zip"
Expand-Archive -Path "$env:TEMP\nginx.zip" -DestinationPath "C:\" -Force
Rename-Item "C:\nginx-1.27.4" "C:\nginx"
```

---

## 3. Config reverse proxy

Bật include `conf.d/*.conf` trong `C:\nginx\conf\nginx.conf` (thêm dòng này
vào trong khối `http { ... }` nếu chưa có):

```nginx
include conf.d/*.conf;
```

Tạo file config riêng cho domain:

```powershell
New-Item -ItemType Directory -Path "C:\nginx\conf\conf.d" -Force
notepad C:\nginx\conf\conf.d\check_tracking.conf
```

Nội dung (thay `tracking.example.com` bằng domain thật của bạn):

```nginx
server {
    listen 80;
    server_name tracking.example.com;

    location / {
        proxy_pass http://127.0.0.1:5673;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60s;
    }
}
```

## 4. Chạy Nginx

```powershell
cd C:\nginx
.\nginx.exe -t             # kiểm tra config trước
.\nginx.exe                # lần đầu khởi động
.\nginx.exe -s reload      # nếu Nginx đã chạy sẵn, reload để áp config mới
```

---

## 5. Kiểm tra

```powershell
curl http://127.0.0.1:5673/docs   # API local — phải OK
curl http://localhost/docs        # qua Nginx — phải trả giống hệt trên
```

Sau đó test từ ngoài: `https://tracking.example.com/docs` (Cloudflare tự lo
phần HTTPS, Nginx chỉ nhận HTTP thuần từ Cloudflare).

---

## Troubleshooting

**`nginx -t` báo lỗi cú pháp** — đọc số dòng lỗi, thường thiếu `;` hoặc `}`.

**`curl http://localhost/docs` lỗi dù API local OK** — Nginx chưa chạy
(`tasklist | findstr nginx`), hoặc `conf.d\check_tracking.conf` sai
`proxy_pass`, hoặc quên thêm `include conf.d/*.conf;` vào `nginx.conf`. Xem
log: `type C:\nginx\logs\error.log`.

**Port 80 bị chiếm** — `netstat -ano | findstr :80` để tìm process đang giữ
port (thường là IIS mặc định của Windows), tắt process đó.

**Domain ngoài không vào được dù local + Nginx đều OK** — kiểm tra lại DNS
đã trỏ đúng IP, firewall/router đã forward port 80 vào đúng máy, và
Cloudflare SSL mode phù hợp (Flexible nếu Nginx chỉ chạy HTTP như trên).
