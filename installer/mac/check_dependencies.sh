#!/bin/bash
# Script kiểm tra dependencies trước khi chạy app
# Usage: bash installer/mac/check_dependencies.sh

echo "=========================================="
echo "Kiểm Tra Dependencies cho Etsy Crawler"
echo "=========================================="
echo ""

# Check Chrome
echo "🔍 Kiểm tra Google Chrome..."
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ -f "$CHROME_PATH" ]; then
    CHROME_VERSION=$("$CHROME_PATH" --version 2>/dev/null || echo "Unknown")
    echo "✅ Chrome đã được cài đặt"
    echo "   Version: $CHROME_VERSION"
    echo "   Path: $CHROME_PATH"
else
    echo "❌ Chrome CHƯA được cài đặt"
    echo "   Download: https://www.google.com/chrome/"
    echo "   App sẽ KHÔNG hoạt động nếu không có Chrome!"
fi

echo ""

# Check macOS version
echo "🔍 Kiểm tra macOS version..."
MACOS_VERSION=$(sw_vers -productVersion)
echo "✅ macOS Version: $MACOS_VERSION"

# Check if macOS 10.13+
MAJOR_VERSION=$(echo $MACOS_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $MACOS_VERSION | cut -d. -f2)
if [ "$MAJOR_VERSION" -ge 11 ] || ([ "$MAJOR_VERSION" -eq 10 ] && [ "$MINOR_VERSION" -ge 13 ]); then
    echo "✅ macOS version phù hợp (10.13+)"
else
    echo "⚠️  macOS version có thể quá cũ (cần 10.13+)"
fi

echo ""

# Check app executable
echo "🔍 Kiểm tra app executable..."
APP_PATH="dist/EtsyCrawlerDragonMedia"
if [ -f "$APP_PATH" ]; then
    echo "✅ App executable tồn tại: $APP_PATH"
    FILE_SIZE=$(du -h "$APP_PATH" | cut -f1)
    echo "   Size: $FILE_SIZE"
    
    # Check if executable
    if [ -x "$APP_PATH" ]; then
        echo "✅ Executable có quyền thực thi"
    else
        echo "⚠️  Executable thiếu quyền thực thi"
        echo "   Chạy: chmod +x $APP_PATH"
    fi
else
    echo "❌ App executable không tồn tại"
    echo "   Hãy build app trước: bash scripts/build.sh"
fi

echo ""

# Summary
echo "=========================================="
echo "TÓM TẮT:"
echo "=========================================="

if [ -f "$CHROME_PATH" ] && [ -f "$APP_PATH" ]; then
    echo "✅ Tất cả dependencies đã sẵn sàng!"
    echo "   Bạn có thể tạo DMG và phân phối app"
else
    echo "⚠️  Một số dependencies còn thiếu:"
    [ ! -f "$CHROME_PATH" ] && echo "   - Google Chrome"
    [ ! -f "$APP_PATH" ] && echo "   - App executable (cần build)"
    echo ""
    echo "   Sau khi cài đủ dependencies, chạy lại script này để kiểm tra"
fi

echo ""

