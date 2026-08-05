# Hướng dẫn test: Mac (local) → Windows (production)

Quy trình khuyến nghị: test cho chạy đúng trên Mac trước, sau đó mới deploy
sang máy Windows theo `docs/DEPLOY_WINDOWS.md`.

---

## Phần 1: Test trên Mac

### Bước 1 — Cài dependencies

```bash
cd auto-browser-playwright
python3 -m venv venv        # nếu chưa có venv, hoặc venv cũ bị hỏng (đổi tên thư mục project)
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium   # chỉ cần cho driver, không dùng browser này để chạy
```

> Nếu trước đó bạn từng đổi tên/di chuyển thư mục project, `venv/bin/pip`,
> `venv/bin/uvicorn`... có thể bị hỏng (shebang trỏ về path cũ). Cách nhanh
> nhất là dùng `python3 -m pip ...` / `python3 -m uvicorn ...` thay vì gọi
> thẳng script trong `venv/bin/`, hoặc xoá `venv/` và tạo lại.

### Bước 2 — (Tùy chọn) tạo `.env`

```bash
cp .env-example .env
```

Không tạo cũng được — `config.py` tự dùng giá trị mặc định giống hệt `.env-example`.

### Bước 3 — Mở Chrome với CDP (profile riêng, không đụng Chrome cá nhân)

```bash
./scripts/start_chrome_with_cdp.sh
```

Kiểm tra CDP đã sẵn sàng:

```bash
curl -s http://localhost:9222/json/version
```

Phải thấy JSON có `Browser`, `webSocketDebuggerUrl`. Nếu curl báo `Connection refused` → đợi thêm vài giây rồi thử lại (Chrome khởi động chậm ở lần đầu).

### Bước 4 — Chạy API server

```bash
uvicorn src.app.api_server:app --host 0.0.0.0 --port 5673
```

Mở `http://localhost:5673/docs` — thấy Swagger UI là server đã lên.

### Bước 5 — Gọi thử API

Dùng **tracking number thật, còn hiệu lực** (số ví dụ trong docs có thể đã cũ/hết hạn):

```bash
curl -X POST "http://localhost:5673/api/v1/cdp/auto-check-tracking" \
  -H "Content-Type: application/json" \
  -d '[
    {"shipment_id": "1", "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=<SỐ_TRACKING_THẬT>"}
  ]'
```

Kỳ vọng: JSON trả về đúng shape `[{shipment_id, delivered, delivered_at}]`, và log server (terminal đang chạy uvicorn) in ra từng bước xử lý.

### Bước 6 — Dừng lại

- `Ctrl+C` ở terminal chạy uvicorn.
- Đóng Chrome CDP: `./scripts/stop_chrome_with_cdp.sh` (hoặc đóng cửa sổ Chrome thủ công).

---

## Troubleshooting khi test trên Mac

### `delivered` luôn `false`, không lỗi gì

Kiểm tra theo thứ tự:

1. **Tracking number có hợp lệ/còn hiệu lực không?** — số cũ/hết hạn thường
   khiến USPS trả về trang khác với trang tracking thật.
2. **Trang có bị chặn bởi bot-protection không?** Chạy debug thủ công để xem
   USPS thực sự trả về gì:

   ```bash
   python3 -c "
   import asyncio
   from src.core.automation import PlaywrightAutomation

   async def main():
       a = PlaywrightAutomation()
       await a.connect_over_cdp('http://localhost:9222')
       await a.navigate('https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=<SỐ_TRACKING_THẬT>')
       await asyncio.sleep(5)
       text = await a.page.evaluate('() => document.body.innerText')
       print('body length:', len(text))
       print(text[:500])
       await a.page.screenshot(path='/tmp/usps_debug.png', full_page=True)
       await a.detach()

   asyncio.run(main())
   "
   ```

   - Nếu `body length: 0` liên tục và `/tmp/usps_debug.png` là trang trắng
     → USPS đang trả về JS challenge (bot-protection), không phải lỗi code.
     Thử: tăng `WAIT_TIME_SECONDS` trong `.env` lên 5–10s, thử lại sau vài
     phút, hoặc thử tracking number khác.
   - Nếu thấy nội dung trang tracking bình thường trong log/screenshot
     nhưng vẫn `delivered=false` → kiểm tra `REQUIRED_PHRASES` trong `.env`
     có khớp với text thật trên trang không (USPS có thể đổi wording).

3. **Chrome CDP có đang chạy đúng chưa?** `curl http://localhost:9222/json`
   phải trả JSON danh sách tab.

### `Connection refused` / `Unable to connect to the remote server` khi gọi CDP endpoint

Nguyên nhân phổ biến nhất: **Chrome đã đang chạy sẵn** (dù chỉ 1 cửa sổ bình
thường trước đó). Khi Chrome đã có tiến trình chạy, việc mở lại `chrome.exe`
kèm `--remote-debugging-port` sẽ chỉ mở thêm 1 tab trong tiến trình cũ và
**bỏ qua** flag đó — CDP sẽ không bao giờ bật lên dù không báo lỗi gì.

Cách khắc phục:
1. **Đóng toàn bộ cửa sổ Chrome đang mở** (Task Manager / Activity Monitor
   → kill hết `chrome.exe` / `Google Chrome`), rồi chạy lại
   `scripts\start_chrome_with_cdp.bat` (Windows) hoặc
   `./scripts/start_chrome_with_cdp.sh` (Mac).
2. Đảm bảo có `--user-data-dir` **khác** với profile Chrome mặc định — script
   đã tự dùng 1 thư mục profile riêng (`%TEMP%\chrome-cdp-profile` trên
   Windows, `/tmp/chrome-cdp-profile` trên Mac), để Chrome buộc phải mở
   tiến trình mới thay vì gộp vào tiến trình đang chạy.
3. Sau khi chạy script, đợi 3–5 giây rồi mới `curl http://localhost:9222/json`
   — Chrome cần chút thời gian để khởi động xong.

### Server lỗi `ModuleNotFoundError`

Chưa `pip install -r requirements.txt`, hoặc đang chạy nhầm Python
không phải trong `venv`.

---

## Phần 2: Deploy & test trên Windows

Sau khi luồng chạy đúng trên Mac, làm theo `docs/DEPLOY_WINDOWS.md` (chi
tiết đầy đủ). Tóm tắt nhanh:

1. Cài Python, tạo venv, `pip install -r requirements.txt`.
2. `copy .env-example .env`, chỉnh nếu cần.
3. Khởi động Chrome với CDP — dùng `scripts\start_chrome_with_cdp.bat` (chạy
   được ở cả cmd và PowerShell), hoặc gõ lệnh trực tiếp:
   - Command Prompt: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"`
   - PowerShell (**bắt buộc thêm `&` ở đầu**, không có sẽ báo lỗi `Unexpected token`): `& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"`
4. Chạy server: `start_auto_check_tracking.bat` (hoặc
   `uvicorn src.app.api_server:app --host 0.0.0.0 --port 5673`).
5. Test cục bộ trước: `http://127.0.0.1:5673/docs` và gọi thử API bằng
   `curl`/Postman — giống hệt Bước 5 ở Phần 1.
6. Nếu gặp lỗi `ImportError: DLL load failed while importing _greenlet` khi
   chạy `uvicorn` — xem mục Troubleshooting trong `docs/DEPLOY_WINDOWS.md`
   (thường do bản `greenlet` chưa tương thích với Python 3.14).
7. Sau khi API local OK mới mở firewall / cấu hình domain ngoài + Nginx —
   xem `docs/DEPLOY_DOMAIN_NGINX.md` khi cần public ra ngoài.

> Lưu ý: hành vi bot-protection của USPS có thể khác nhau giữa các máy/IP
> (Mac dev vs server Windows production). Nếu Mac chạy tốt nhưng Windows bị
> chặn (hoặc ngược lại), áp dụng đúng cách debug ở mục Troubleshooting phía
> trên trên máy Windows.
