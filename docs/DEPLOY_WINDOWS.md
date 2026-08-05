# Setup & chạy CDP Tracking API trên Windows (local)

Tài liệu này đi từ **pull code** → **cài môi trường** → **chạy Chrome CDP** →
**chạy API server local** (`http://127.0.0.1:5673`). Dừng ở bước chạy server —
phần public qua domain ngoài + Nginx nằm ở file riêng (xem ghi chú cuối bài).

---

## 0. Yêu cầu hệ thống

- **Windows 10/11**
- **Git** đã cài (`git --version` chạy được)
- **Python 3.11 – 3.13** (khuyến nghị). Có thể dùng Python 3.14 nhưng một số
  package (đặc biệt `greenlet`, dependency của Playwright) mới hỗ trợ 3.14 gần
  đây và dễ gặp lỗi cài đặt hơn — xem mục Troubleshooting nếu gặp lỗi
  `DLL load failed`.
- **Google Chrome** đã cài đặt (dùng Chrome thật, không dùng browser đi kèm
  Playwright).

---

## 1. Lấy code

Lần đầu (clone):

```powershell
git clone <REPO_URL> auto-browser-playwright
cd auto-browser-playwright
```

Nếu đã có sẵn code từ trước, chỉ cần pull bản mới nhất:

```powershell
cd auto-browser-playwright
git pull
```

---

## 2. Tạo virtualenv & cài dependencies

Mở **PowerShell** (hoặc Command Prompt) tại thư mục project:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

> Nếu lệnh `python` không nhận diện được, thử `py -3.12` (nếu máy có nhiều
> bản Python) hoặc cài Python từ [python.org](https://www.python.org/downloads/)
> (nhớ tick **"Add python.exe to PATH"** khi cài).

Sau bước này, prompt sẽ hiện `(.venv) PS ...` nghĩa là venv đã active.

### Nếu gặp lỗi `ImportError: DLL load failed while importing _greenlet`

Lỗi này xảy ra khi chạy `uvicorn` (không phải lúc `pip install`), do bản
`greenlet` đã cài không tương thích đúng với Python đang dùng (thường gặp
nhất với **Python 3.14** — rất mới, một số bản `greenlet` cũ chưa có wheel
build sẵn phù hợp). Fix theo thứ tự:

1. **Force reinstall `greenlet` lên bản mới nhất** (thường fix được ngay):

   ```powershell
   pip install --upgrade --force-reinstall greenlet
   ```

   Chạy lại `uvicorn ...` sau khi cài xong.

2. **Nếu vẫn lỗi `DLL load failed`** — máy thường thiếu
   **Microsoft Visual C++ Redistributable (x64)**, runtime bắt buộc cho các
   extension Python biên dịch sẵn trên Windows. Tải bản chính thức từ
   Microsoft: https://aka.ms/vs/17/release/vc_redist.x64.exe → cài xong,
   **mở lại terminal mới** rồi thử lại.

3. **Nếu vẫn không được** — đổi sang Python bản ổn định hơn (3.12 hoặc 3.13)
   thay vì 3.14:

   ```powershell
   deactivate
   Remove-Item -Recurse -Force .venv
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

---

## 3. Tạo file `.env`

```powershell
Copy-Item .env-example .env
```

Không bắt buộc — nếu bỏ qua, `config.py` tự dùng giá trị mặc định giống hệt
`.env-example`. Chỉ cần chỉnh `.env` nếu muốn đổi port, CDP endpoint, thời
gian chờ, hoặc các cụm từ nhận diện "delivered" — xem bảng biến trong
`README.md`.

---

## 4. Khởi động Chrome với CDP (remote debugging)

API bắt buộc phải có Chrome đang chạy với cờ `--remote-debugging-port=9222`.

### Cách khuyến nghị: dùng script có sẵn

```powershell
.\scripts\start_chrome_with_cdp.bat
```

Script này tự tìm đường dẫn Chrome và mở với `--user-data-dir` **riêng**
(khác profile Chrome mặc định của bạn) — bắt buộc phải làm vậy, xem lý do ở
mục Troubleshooting bên dưới.

### Hoặc chạy lệnh thủ công

**Command Prompt (cmd.exe):**

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

**PowerShell:** phải thêm toán tử gọi lệnh `&` ở đầu dòng, nếu không sẽ báo
lỗi `Unexpected token '--remote-debugging-port=9222' ...` (PowerShell coi
chuỗi trong ngoặc kép là expression, không phải lệnh để chạy):

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"
```

### Xác nhận CDP đã lên

Đợi vài giây rồi kiểm tra:

```powershell
curl http://localhost:9222/json
```

Phải thấy JSON danh sách tab. Nếu báo `Unable to connect` / `Connection
refused`, xem mục Troubleshooting.

**Giữ cửa sổ Chrome này mở** trong suốt quá trình chạy/gọi API.

---

## 5. Chạy API server

Trong terminal đã activate venv (Bước 2), ở thư mục gốc project:

```powershell
uvicorn src.app.api_server:app --host 0.0.0.0 --port 5673
```

Thấy dòng `Uvicorn running on http://0.0.0.0:5673` là server đã lên. Giữ
terminal này mở.

> Cách khác: chạy `start_auto_check_tracking.bat` (tự activate venv tên
> `venv` và chạy `python src\app\api_server.py`) — chỉ dùng nếu venv của bạn
> đặt tên đúng là `venv`, không phải `.venv`.

### Kiểm tra server sống

Mở trình duyệt (hoặc terminal khác): `http://127.0.0.1:5673/docs` → phải
thấy Swagger UI.

### Test gọi API (dùng tracking number thật, còn hiệu lực)

PowerShell:

```powershell
curl -Method POST "http://localhost:5673/api/v1/cdp/auto-check-tracking" `
  -ContentType "application/json" `
  -Body '[{"shipment_id":"1","tracking_link":"https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=<SỐ_TRACKING_THẬT>"}]'
```

Kỳ vọng: JSON trả về `{"shipment_id":"1","delivered":true/false,"delivered_at":"..."}`,
đồng thời log xử lý hiện ở terminal đang chạy uvicorn.

Đến đây là **API đã chạy local hoàn chỉnh trên Windows**. Phần public qua
domain ngoài + Nginx sẽ ở tài liệu riêng.

---

## Troubleshooting

### `Unexpected token '--remote-debugging-port=9222'` (PowerShell)

Thiếu toán tử `&` ở đầu dòng khi gõ trực tiếp lệnh mở `chrome.exe` trong
PowerShell — xem lại Bước 4, dùng đúng bản lệnh PowerShell (có `&`) hoặc
dùng Command Prompt.

### `... was unexpected at this time` khi chạy `.bat`

Đã fix trong `scripts/start_chrome_with_cdp.bat` hiện tại (lỗi cũ do dấu
ngoặc `(x86)` trong đường dẫn Program Files chưa escape làm `cmd.exe` đếm
lệch ngoặc khi parse block `if/else`). Nếu bạn có `.bat` tự viết bị lỗi
tương tự, tránh dùng `if ... ( ... ) else if ... ( ... )` nhiều dòng khi
trong đó có chuỗi chứa `(` hoặc `)` chưa escape.

### `Unable to connect to the remote server` / `Connection refused` khi gọi `curl http://localhost:9222/json`

Nguyên nhân phổ biến nhất: **Chrome đã đang chạy sẵn** (dù chỉ là 1 cửa sổ
Chrome bình thường bạn mở trước đó). Khi Chrome đã có tiến trình chạy, mở
lại `chrome.exe` kèm `--remote-debugging-port` sẽ chỉ mở thêm 1 tab trong
tiến trình cũ và **bỏ qua** flag đó — CDP sẽ không bao giờ bật lên dù script
không báo lỗi gì.

Cách khắc phục:
1. **Đóng toàn bộ cửa sổ Chrome đang mở** (Task Manager → kill hết
   `chrome.exe`), rồi chạy lại `scripts\start_chrome_with_cdp.bat`.
2. Đảm bảo dùng `--user-data-dir` **khác** profile Chrome mặc định (script
   đã tự làm việc này — dùng `%TEMP%\chrome-cdp-profile`) để Chrome buộc
   phải mở tiến trình mới.
3. Đợi 3–5 giây sau khi chạy script rồi mới `curl` kiểm tra.

### `ImportError: DLL load failed while importing _greenlet`

Xem mục "Nếu gặp lỗi `ImportError: DLL load failed...`" ở Bước 2 phía trên.

### `ModuleNotFoundError: No module named 'fastapi'` (hoặc package khác)

Chưa `pip install -r requirements.txt`, hoặc đang chạy Python không phải
trong `.venv` (kiểm tra prompt có tiền tố `(.venv)` không).

### API chạy, trả JSON, nhưng `delivered` luôn `false` dù bạn biết đơn đã delivered

Không phải lỗi kết nối — kiểm tra theo mục "Troubleshooting" trong
`docs/TESTING_GUIDE.md` (USPS có thể trả trang bot-protection, hoặc tracking
number không hợp lệ/hết hạn, hoặc `REQUIRED_PHRASES` trong `.env` không khớp
wording thực tế trên trang).

### Tối ưu hiệu suất

- Giảm `WAIT_TIME_SECONDS` trong `.env` nếu không cần chờ lâu (mặc định `2`,
  restart server sau khi đổi).
- Nếu lượng request lớn: cân nhắc chạy nhiều instance service trên các port
  khác nhau rồi load balance, hoặc tối ưu logic trong `connect_to_chrome_via_cdp`.

---

## Bước tiếp theo

Sau khi API chạy ổn định local (`http://127.0.0.1:5673/docs` OK, gọi API
trả kết quả đúng), phần **mở firewall + cấu hình domain ngoài + Nginx
reverse proxy** sẽ nằm trong tài liệu riêng (xem `docs/` khi tài liệu đó
được tạo).
