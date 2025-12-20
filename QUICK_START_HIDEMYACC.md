# Hướng dẫn chạy từ đầu - HideMyAcc với Playwright

## Yêu cầu

1. ✅ HideMyAcc đã được cài đặt
2. ✅ Đã tạo ít nhất một profile trong HideMyAcc
3. ✅ Python và Playwright đã cài đặt trong dự án này

## Bước 1: Kiểm tra HideMyAcc profiles có sẵn

Chạy lệnh này để xem các profile bạn đã tạo:

```bash
python3 -m src.utils.hidemyacc
```

Kết quả sẽ hiển thị danh sách profiles, ví dụ:
```
✓ Tìm thấy 2 HideMyAcc profile(s):

[1] profile1
    ID: profile1
    Path: /Users/mac/.../Profiles/profile1
    User Data: /Users/mac/.../Profiles/profile1/User Data

[2] profile2
    ID: profile2
    Path: /Users/mac/.../Profiles/profile2
    User Data: /Users/mac/.../Profiles/profile2/User Data
```

**Ghi nhớ tên profile** bạn muốn sử dụng (ví dụ: `profile1`)

---

## Bước 2: Chạy script - Tự động mọi thứ

Chỉ cần chạy một lệnh duy nhất:

```bash
# Chạy với Etsy scraping
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --keyword "handmade bag" --pages 2

# Hoặc chỉ launch profile (không scrape)
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --no-proxy
```

**Code sẽ tự động:**
1. ✅ Tìm profile trong HideMyAcc (`~/.hidemyacc/profiles/`)
2. ✅ Tự động tìm Marco browser executable mới nhất
3. ✅ Launch Playwright với profile qua `user-data-dir`
4. ✅ Navigate đến Etsy và scrape dữ liệu (nếu có keyword/pages)
5. ✅ Gửi dữ liệu tới webhook n8n
6. ✅ Giữ browser mở (detach, không close)

**Xong!** Browser sẽ mở và bạn có thể thấy nó đang hoạt động.

---

## Bước 3: Sử dụng trong code Python của bạn

Sau khi đã test thành công, bạn có thể dùng trong code:

### Ví dụ 1: Launch profile và automation đơn giản

```python
import asyncio
from src.app.hidemyacc_connection_profile import launch_hidemyacc_profile_for_api

async def main():
    # Launch HideMyAcc profile và lấy automation object
    automation, profile_info = await launch_hidemyacc_profile_for_api(
        profile_id='hma_xxx',  # Profile ID
        use_command_line_config=True,
        cdp_port=9223
    )
    
    if automation:
        # Thực hiện automation
        await automation.navigate("https://www.example.com")
        await automation.page.wait_for_timeout(3000)
        
        # Lấy title
        title = await automation.page.title()
        print(f"Page title: {title}")
        
        # Detach (KHÔNG đóng browser)
        await automation.detach()
    else:
        print("Không thể launch profile")

if __name__ == "__main__":
    asyncio.run(main())
```

### Ví dụ 2: Sử dụng với network interception (bắt API)

```python
import asyncio
from src.app.hidemyacc_connection_profile import launch_hidemyacc_profile_for_api

async def main():
    automation, profile_info = await launch_hidemyacc_profile_for_api(
        profile_id='hma_xxx',
        use_command_line_config=True
    )
    
    if automation:
        captured_data = []
        
        # Hàm bắt API responses
        async def handle_response(response):
            if "api" in response.url and response.status == 200:
                try:
                    data = await response.json()
                    captured_data.append({
                        "url": response.url,
                        "data": data
                    })
                    print(f"✓ Bắt được API: {response.url}")
                except:
                    pass
        
        # Thiết lập listener
        automation.page.on("response", handle_response)
        
        # Điều hướng và chờ
        await automation.navigate("https://www.etsy.com/listing/...")
        await automation.page.wait_for_timeout(5000)
        
        # Xem kết quả
        print(f"\nĐã bắt được {len(captured_data)} API responses")
        for item in captured_data:
            print(f"  - {item['url']}")
        
        await automation.detach()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Các tùy chọn khi chạy script

```bash
# Chỉ định profile và scrape Etsy
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --keyword "handmade bag" --pages 5

# Chỉ launch profile, không scrape
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx

# Bật proxy (với credentials mặc định)
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --with-proxy

# Tắt proxy
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --no-proxy

# Xem help
python3 src/app/hidemyacc_connection_profile.py --help
```

---

## Nếu gặp lỗi

### Lỗi: "Không tìm thấy HideMyAcc profiles"

**Giải pháp:**
1. Kiểm tra HideMyAcc đã cài đặt chưa
2. Kiểm tra đã tạo profile trong HideMyAcc chưa
3. Nếu HideMyAcc ở vị trí khác, sửa file `src/utils/hidemyacc.py`:
   ```python
   POSSIBLE_PATHS = {
       "darwin": [
           Path("/your/custom/path/to/HideMyAcc"),  # Thêm đường dẫn của bạn
           # ...
       ]
   }
   ```

### Lỗi: "Không thể khởi động Chrome"

**Giải pháp:**
1. Kiểm tra Chrome đã cài đặt
2. macOS: Chrome phải ở `/Applications/Google Chrome.app/`
3. Thử khởi động thủ công:
   ```bash
   ./scripts/start_chrome_with_hidemyacc.sh 9223 profile1
   ```

### Lỗi: "CDP không kết nối được"

**Giải pháp:**
1. Kiểm tra port có bị chiếm không:
   ```bash
   lsof -i :9223  # macOS/Linux
   ```
2. Đợi thêm vài giây để Chrome khởi động hoàn toàn
3. Thử port khác:
   ```bash
   python3 src/app/hidemyacc_connection.py --profile profile1 --port 9223
   ```

---

## Workflow đầy đủ (từng bước)

1. **Mở terminal** trong thư mục dự án
   ```bash
   cd /Users/mac/Documents/browser/auto-browser-playwright
   ```

2. **Kiểm tra profiles:**
   ```bash
   python3 -m src.utils.hidemyacc
   ```

3. **Chạy script (tự động mọi thứ):**
   ```bash
   python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --keyword "handmade bag" --pages 2
   ```

4. **Browser sẽ mở tự động** với HideMyAcc profile

5. **Sử dụng automation** trong code Python của bạn

---

## Tips

- ⚠️ **Mỗi profile chỉ nên chạy một lần** - Nếu profile đã chạy, đóng Chrome trước khi chạy lại
- ✅ **Detach thay vì close** - Dùng `automation.detach()` thay vì `automation.close()` để giữ browser mở
- ✅ **Marco browser** - Tự động tìm Marco browser mới nhất trong `~/.hidemyacc/browser/`
- ✅ **Profile đã cấu hình** - Fingerprint, proxy, cookies trong profile sẽ được sử dụng tự động
- ✅ **Webhook** - Dữ liệu Etsy được tự động gửi tới webhook n8n sau khi scrape xong

---

## Ví dụ nhanh

```bash
# 1. Xem profiles
python3 -c "from src.utils.hidemyacc import HideMyAccManager; print(HideMyAccManager().find_profiles())"

# 2. Chạy với profile cụ thể và scrape Etsy
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx --keyword "handmade bag" --pages 2

# 3. Hoặc chỉ launch profile (không scrape)
python3 src/app/hidemyacc_connection_profile.py --profile hma_xxx
```

**Xong! Browser sẽ mở và sẵn sàng cho automation.** 🚀
