# Public API qua domain ngoài (Nginx reverse proxy trên Windows)

Tài liệu này nối tiếp `docs/DEPLOY_WINDOWS.md` — chỉ làm khi API đã **chạy
ổn định ở local** (`http://127.0.0.1:5673/docs` OK).

Kiến trúc thật đang dùng: domain chạy qua **Cloudflare Tunnel**, tunnel
(`cloudflared`) chạy trên máy khác (`dragon-home-server`) chứ không phải
chính máy Windows này — route `tracking.supover.com` đã trỏ tới
`http://192.168.0.190` (IP LAN của máy Windows, cổng mặc định **80**).

```
Internet ──▶ Cloudflare Tunnel ──▶ dragon-home-server ──▶ LAN ──▶ Nginx :80 (192.168.0.190) ──▶ API local (127.0.0.1:5673)
```

Vì Internet không chạm trực tiếp vào máy Windows (tunnel đã che hết), máy
này **không cần expose gì ra ngoài, không cần port-forward trên router**.
Chỉ cần: port 80 nhận được traffic từ máy `dragon-home-server` trong LAN,
và có Nginx lắng nghe ở đó để forward tiếp vào API local.

---

## 1. Cho phép port 80 trong LAN

Route tunnel gọi vào `http://192.168.0.190` (không có port = mặc định 80),
nên máy này cần lắng nghe port 80. Đây là rule **LAN-only**, không phải mở
ra Internet:

```powershell
New-NetFirewallRule -DisplayName "Nginx_HTTP_LAN" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -Profile Private,Domain
```

`-Profile Private,Domain` cố tình **không** bao gồm `Public` — rule này chỉ
áp dụng cho mạng LAN nội bộ, không mở ra Internet (vốn cũng không cần, vì
Cloudflare Tunnel đã lo phần đó).

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

Nội dung:

```nginx
server {
    listen 80;
    server_name tracking.supover.com;

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

Sau đó test thẳng qua domain thật (tunnel đã trỏ sẵn, không cần đợi DNS):
`https://tracking.supover.com/docs`.

---

## Troubleshooting

**`nginx -t` báo lỗi cú pháp** — đọc số dòng lỗi, thường thiếu `;` hoặc `}`.

**`curl http://localhost/docs` lỗi dù API local OK** — Nginx chưa chạy
(`tasklist | findstr nginx`), hoặc `conf.d\check_tracking.conf` sai
`proxy_pass`, hoặc quên thêm `include conf.d/*.conf;` vào `nginx.conf`. Xem
log: `type C:\nginx\logs\error.log`.

**Port 80 bị chiếm** — `netstat -ano | findstr :80` để tìm process đang giữ
port (thường là IIS mặc định của Windows), tắt process đó.

**`https://tracking.supover.com/docs` không vào được dù local + Nginx đều OK
(`curl http://localhost/docs` chạy tốt trên máy Windows)** — lỗi nằm ở tầng
tunnel/LAN, không phải Nginx:
- Kiểm tra route `tracking.supover.com` trong Cloudflare Zero Trust →
  Tunnels & Mesh → Published application routes vẫn trỏ đúng
  `http://192.168.0.190`.
- Từ máy `dragon-home-server`, thử `curl http://192.168.0.190/docs` — nếu
  máy đó cũng không gọi được, chắc chắn là do Bước 1 (firewall LAN) chưa
  đúng, hoặc IP máy Windows đã đổi (kiểm tra `ipconfig` xem còn đúng
  `192.168.0.190` không — IP LAN qua DHCP có thể đổi sau khi máy khởi động
  lại; nếu đổi, cập nhật lại route trong Cloudflare Tunnel).
- Kiểm tra `cloudflared` trên `dragon-home-server` đang chạy bình thường
  (không liên quan tới máy Windows — hỏi/kiểm tra riêng ở máy đó).
