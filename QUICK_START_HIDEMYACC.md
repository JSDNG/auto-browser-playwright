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
python3 src/app/hidemyacc_connection.py --profile profile1
```

**Code sẽ tự động:**
1. ✅ Tìm profile `profile1` trong HideMyAcc
2. ✅ Kiểm tra Chrome có đang chạy với CDP chưa
3. ✅ Nếu chưa → Tự động khởi động Chrome với profile + CDP
4. ✅ Kết nối Playwright với Chrome
5. ✅ Mở trang Google làm ví dụ

**Xong!** Browser sẽ mở và bạn có thể thấy nó đang hoạt động.

---

## Bước 3: Sử dụng trong code Python của bạn

Sau khi đã test thành công, bạn có thể dùng trong code:

### Ví dụ 1: Kết nối và automation đơn giản

```python
import asyncio
from src.app.hidemyacc_connection import connect_to_hidemyacc_profile

async def main():
    # Tự động tìm profile, khởi động Chrome và kết nối
    automation = await connect_to_hidemyacc_profile(
        'profile1',      # Tên profile
        cdp_port=9222,   # Port CDP
        auto_launch=True # Tự động khởi động (mặc định True)
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
        print("Không thể kết nối")

if __name__ == "__main__":
    asyncio.run(main())
```

### Ví dụ 2: Sử dụng với network interception (bắt API)

```python
import asyncio
from src.app.hidemyacc_connection import connect_to_hidemyacc_profile

async def main():
    automation = await connect_to_hidemyacc_profile('profile1')
    
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
# Chỉ định profile
python3 src/app/hidemyacc_connection.py --profile profile1

# Chỉ định port khác (nếu port 9222 đã dùng)
python3 src/app/hidemyacc_connection.py --profile profile1 --port 9223

# KHÔNG tự động khởi động (nếu Chrome đã chạy sẵn)
python3 src/app/hidemyacc_connection.py --profile profile1 --no-auto-launch

# Xem help
python3 src/app/hidemyacc_connection.py --help
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
   ./scripts/start_chrome_with_hidemyacc.sh 9222 profile1
   ```

### Lỗi: "CDP không kết nối được"

**Giải pháp:**
1. Kiểm tra port có bị chiếm không:
   ```bash
   lsof -i :9222  # macOS/Linux
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
   python3 src/app/hidemyacc_connection.py --profile YOUR_PROFILE_NAME
   ```

4. **Browser sẽ mở tự động** với HideMyAcc profile

5. **Sử dụng automation** trong code Python của bạn

---

## Tips

- ⚠️ **Mỗi profile chỉ nên chạy một lần** - Nếu profile đã chạy, đóng Chrome trước khi chạy lại
- ✅ **Detach thay vì close** - Dùng `automation.detach()` thay vì `automation.close()` để giữ browser mở
- ✅ **Port khác nhau** - Nếu muốn chạy nhiều profile cùng lúc, dùng port khác nhau (9222, 9223, 9224...)
- ✅ **Profile đã cấu hình** - Fingerprint, proxy, cookies trong profile sẽ được sử dụng tự động

---

## Ví dụ nhanh

```bash
# 1. Xem profiles
python3 -m src.utils.hidemyacc

# 2. Chạy với profile đầu tiên (tự động)
python3 src/app/hidemyacc_connection.py

# 3. Hoặc chỉ định profile cụ thể
python3 src/app/hidemyacc_connection.py --profile my_profile
```

**Xong! Browser sẽ mở và sẵn sàng cho automation.** 🚀
