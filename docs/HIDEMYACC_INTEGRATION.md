# Tích hợp HideMyAcc với Playwright qua CDP

## Tổng quan

HideMyAcc là công cụ quản lý browser profile với tính năng anti-detect. Hướng dẫn này giúp bạn kết nối Playwright với các profile của HideMyAcc qua CDP (Chrome DevTools Protocol).

## Lợi ích

- ✅ Sử dụng fingerprint anti-detect từ HideMyAcc
- ✅ Tái sử dụng cookies, sessions đã lưu
- ✅ Quản lý nhiều profiles riêng biệt
- ✅ Tự động hóa với profile đã cấu hình sẵn

## Yêu cầu

1. HideMyAcc đã được cài đặt
2. Đã tạo ít nhất một profile trong HideMyAcc
3. Python và Playwright đã cài đặt

## Hướng dẫn sử dụng

### Cách 1: Tự động (Khuyến nghị) - Code tự tìm và khởi động

**Bước 1: Liệt kê HideMyAcc profiles (tùy chọn)**
```bash
python3 -m src.utils.hidemyacc
```

**Bước 2: Chạy script - Code sẽ tự động tìm profile và khởi động Chrome**
```bash
# Tự động chọn profile đầu tiên và tự động khởi động Chrome
python3 src/app/hidemyacc_connection.py

# Chỉ định profile cụ thể
python3 src/app/hidemyacc_connection.py --profile my_profile

# Không tự động khởi động (nếu Chrome đã chạy sẵn)
python3 src/app/hidemyacc_connection.py --profile my_profile --no-auto-launch
```

**Lưu ý:** Code sẽ:
- ✅ Tự động tìm HideMyAcc profiles
- ✅ Tự động khởi động Chrome với profile đó + CDP
- ✅ Tự động kết nối Playwright

### Cách 2: Thủ công - Khởi động Chrome trước

**Bước 1: Liệt kê HideMyAcc profiles**

Xem danh sách các profile có sẵn:

```bash
python3 -m src.utils.hidemyacc
```

Kết quả sẽ hiển thị:
- ID/Name của profile
- Đường dẫn đến profile
- User data directory

**Bước 2: Khởi động Chrome với HideMyAcc profile + CDP**

**macOS/Linux:**
```bash
./scripts/start_chrome_with_hidemyacc.sh [PORT] [PROFILE_ID]
```

**Windows:**
```cmd
scripts\start_chrome_with_hidemyacc.bat [PORT] [PROFILE_ID]
```

**Ví dụ:**
```bash
# Sử dụng port mặc định 9222
./scripts/start_chrome_with_hidemyacc.sh 9222 my_profile

# Sử dụng port tùy chỉnh
./scripts/start_chrome_with_hidemyacc.sh 9223 profile_2
```

**Bước 3: Kết nối Playwright**

**Cách 1: Sử dụng script có sẵn**
```bash
# Tự động chọn profile đầu tiên
python3 src/app/hidemyacc_connection.py

# Chỉ định profile cụ thể
python3 src/app/hidemyacc_connection.py --profile my_profile --port 9222
```

**Cách 2: Sử dụng trong code Python**
```python
from src.core.automation import PlaywrightAutomation

automation = PlaywrightAutomation()

# Kết nối với Chrome đang chạy (đã khởi động với HideMyAcc profile)
await automation.connect_over_cdp("http://localhost:9222")

# Sử dụng như bình thường
await automation.navigate("https://example.com")
```

## Cấu trúc thư mục HideMyAcc

HideMyAcc thường lưu profiles tại:

- **macOS:**
  - `~/Library/Application Support/HideMyAcc/Profiles/`
  - `~/Documents/HideMyAcc/Profiles/`

- **Linux:**
  - `~/.config/HideMyAcc/Profiles/`
  - `~/Documents/HideMyAcc/Profiles/`

- **Windows:**
  - `%USERPROFILE%\Documents\HideMyAcc\Profiles\`
  - `%APPDATA%\HideMyAcc\Profiles\`

## Troubleshooting

### Không tìm thấy HideMyAcc profiles

1. Kiểm tra HideMyAcc đã được cài đặt:
   ```bash
   # macOS
   ls ~/Library/Application\ Support/ | grep -i hide
   
   # Hoặc
   ls ~/Documents/ | grep -i hide
   ```

2. Đảm bảo đã tạo ít nhất một profile trong HideMyAcc

3. Nếu HideMyAcc ở vị trí khác, chỉnh sửa `src/utils/hidemyacc.py`:
   ```python
   POSSIBLE_PATHS = {
       "darwin": [
           Path("/path/to/your/HideMyAcc"),  # Thêm đường dẫn của bạn
           # ...
       ]
   }
   ```

### Chrome không khởi động được

- Kiểm tra port có đang được sử dụng không:
  ```bash
  lsof -i :9222  # macOS/Linux
  netstat -ano | findstr :9222  # Windows
  ```

- Thử đổi port khác:
  ```bash
  ./scripts/start_chrome_with_hidemyacc.sh 9223 profile_name
  ```

### CDP không kết nối được

1. Kiểm tra CDP đang chạy:
   ```bash
   curl http://localhost:9222/json
   ```

2. Đảm bảo Chrome đã khởi động hoàn toàn (đợi 2-3 giây)

3. Kiểm tra profile path có đúng không:
   ```python
   python3 -m src.utils.hidemyacc
   ```

### Profile bị lỗi hoặc không hoạt động

- Thử profile khác
- Kiểm tra profile trong HideMyAcc có hoạt động bình thường không
- Đảm bảo profile không đang được sử dụng bởi HideMyAcc

## Workflow khuyến nghị

### Workflow tự động (Đơn giản nhất)

1. **Tạo profile trong HideMyAcc** với các thiết lập cần thiết (fingerprint, proxy, etc.)

2. **Chạy script - Mọi thứ tự động:**
   ```bash
   python3 src/app/hidemyacc_connection.py --profile profile_name
   ```
   
   Code sẽ tự động:
   - Tìm profile
   - Khởi động Chrome với profile + CDP
   - Kết nối Playwright
   - Sẵn sàng để automation

3. **Sử dụng trong code Python:**
   ```python
   from src.app.hidemyacc_connection import connect_to_hidemyacc_profile
   
   # Tự động tìm, khởi động và kết nối
   automation = await connect_to_hidemyacc_profile('profile_name', 9222, auto_launch=True)
   
   if automation:
       # Thực hiện automation
       await automation.navigate("https://example.com")
       
       # Detach khi xong (browser sẽ không bị đóng)
       await automation.detach()
   ```

### Workflow thủ công (Nếu cần kiểm soát nhiều hơn)

1. **Tạo profile trong HideMyAcc** với các thiết lập cần thiết

2. **Khởi động Chrome với profile:**
   ```bash
   ./scripts/start_chrome_with_hidemyacc.sh 9222 profile_name
   ```

3. **Kết nối Playwright:**
   ```python
   from src.core.automation import PlaywrightAutomation
   
   automation = PlaywrightAutomation()
   await automation.connect_over_cdp("http://localhost:9222")
   ```

4. **Thực hiện automation** như bình thường

5. **Detach khi xong** (browser sẽ không bị đóng):
   ```python
   await automation.detach()
   ```

## Lưu ý

- ⚠️ Mỗi profile chỉ nên được khởi động một lần
- ⚠️ Không đóng Chrome thủ công khi đang dùng CDP (dùng `detach()` thay vì `close()`)
- ⚠️ Mỗi port chỉ có thể dùng cho một Chrome instance
- ✅ Profiles của HideMyAcc được giữ nguyên, không bị ảnh hưởng bởi automation

## Ví dụ đầy đủ

Xem file `src/app/hidemyacc_connection.py` để có ví dụ hoàn chỉnh.
