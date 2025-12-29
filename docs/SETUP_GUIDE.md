# Hướng dẫn Setup - Đóng gói App Etsy Crawler

## Yêu cầu

- Python 3.11+
- PyInstaller: `pip install pyinstaller`
- Inno Setup (cho Windows): https://jrsoftware.org/isdl.php

---

## Quick Start

### Windows
```cmd
scripts\build_installer.bat
```
→ Tạo: `dist\EtsyCrawler.exe` + `installer\windows\output\EtsyCrawler-Setup-1.0.0.exe`

### Mac
```bash
bash scripts/build_installer.sh
```
→ Tạo: `dist/EtsyCrawler` + `installer/mac/output/EtsyCrawler-1.0.0.dmg`

---

## Chi tiết

### Windows

1. **Cài đặt** (nếu chưa có):
   ```cmd
   pip install pyinstaller
   REM Download Inno Setup: https://jrsoftware.org/isdl.php
   ```

2. **Build**:
   ```cmd
   scripts\build_installer.bat
   ```

3. **Output**:
   - Executable: `dist\EtsyCrawler.exe`
   - Installer: `installer\windows\output\EtsyCrawler-Setup-1.0.0.exe`

### Mac

1. **Cài đặt** (nếu chưa có):
   ```bash
   pip install pyinstaller
   ```

2. **Build**:
   ```bash
   bash scripts/build_installer.sh
   ```

3. **Output**:
   - Executable: `dist/EtsyCrawler`
   - DMG: `installer/mac/output/EtsyCrawler-1.0.0.dmg`

---

## Build thủ công (nếu cần)

Nếu muốn build từng bước riêng:

### Build executable
```bash
# Mac/Linux
pyinstaller build.spec

# Windows
pyinstaller build.spec
```

### Tạo installer riêng
```bash
# Windows
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\windows\EtsyCrawler.iss

# Mac
bash installer/mac/create_dmg.sh
```

---

## Bước 3: Test

### Test trên máy clean (không có Python)

**Windows**:
1. Copy installer sang máy Windows khác
2. Chạy installer
3. Test app có chạy không
4. Test API: `http://localhost:5674/docs`

**Mac**:
1. Copy DMG sang máy Mac khác
2. Mở DMG, drag app vào Applications
3. Test app có chạy không
4. Test API: `http://localhost:5674/docs`

---

## Cấu trúc Files

```
installer/
├── windows/
│   ├── EtsyCrawler.iss      # Inno Setup script
│   └── output/              # Output installer .exe
└── mac/
    ├── create_dmg.sh        # Script tạo DMG
    └── output/              # Output DMG file
```

---

## Tùy chỉnh

### Windows Installer
Chỉnh sửa `installer/windows/EtsyCrawler.iss`:
- App name, version
- License file
- Icon

### Mac DMG
Chỉnh sửa `installer/mac/create_dmg.sh`:
- App name, version
- DMG window size
- Icon

---

## Troubleshooting

### Build fails: "ModuleNotFoundError"
→ Thêm module vào `hiddenimports` trong `build.spec`

### Executable không chạy
→ Kiểm tra console output (nếu `console=True`)
→ Test trên máy clean

### Mac: "App không thể mở"
→ Cần code signing (xem bên dưới)
→ Hoặc user right-click → Open

---

## Code Signing (Optional)

### Mac
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  EtsyCrawler.app
```

### Windows
```cmd
signtool sign /f certificate.pfx /p password \
  /t http://timestamp.digicert.com installer.exe
```

---


---

## Lưu ý quan trọng

1. **Chrome**: App không bundle Chrome, user cần cài Chrome chính chủ
2. **Extension HeyEtsy**: User cần cài extension vào Chrome profile (hoặc app tự động cài)
3. **CDP**: Chrome phải được khởi động với `--remote-debugging-port=9223`
4. **Playwright**: User cần chạy `playwright install chromium` (hoặc bundle vào app)

---

## Tham khảo

- [PyInstaller Docs](https://pyinstaller.org/)
- [Inno Setup Docs](https://jrsoftware.org/ishelp/)
- [create-dmg GitHub](https://github.com/create-dmg/create-dmg)

