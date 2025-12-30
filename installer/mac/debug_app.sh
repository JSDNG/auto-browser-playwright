#!/bin/bash
# Script debug app để xem lỗi chi tiết
# Usage: bash installer/mac/debug_app.sh

echo "=========================================="
echo "Debug Etsy Crawler App"
echo "=========================================="
echo ""

# Check if app exists (try app bundle first, then executable)
APP_NAME="EtsyCrawlerDragonMedia"
APP_BUNDLE_PATH="dist/${APP_NAME}.app"
APP_EXECUTABLE_PATH="dist/${APP_NAME}"

APP_PATH=""
if [ -d "$APP_BUNDLE_PATH" ]; then
    echo "📦 Tìm thấy app bundle: $APP_BUNDLE_PATH"
    EXECUTABLE_IN_BUNDLE="$APP_BUNDLE_PATH/Contents/MacOS/${APP_NAME}"
    if [ -f "$EXECUTABLE_IN_BUNDLE" ]; then
        APP_PATH="$EXECUTABLE_IN_BUNDLE"
        echo "✅ Tìm thấy executable trong bundle: $APP_PATH"
    else
        # Try _APP_NAME (PyInstaller convention)
        EXECUTABLE_IN_BUNDLE_ALT="$APP_BUNDLE_PATH/Contents/MacOS/_${APP_NAME}"
        if [ -f "$EXECUTABLE_IN_BUNDLE_ALT" ]; then
            APP_PATH="$EXECUTABLE_IN_BUNDLE_ALT"
            echo "✅ Tìm thấy executable trong bundle (alt): $APP_PATH"
        else
            echo "❌ Không tìm thấy executable trong bundle"
            exit 1
        fi
    fi
elif [ -f "$APP_EXECUTABLE_PATH" ]; then
    APP_PATH="$APP_EXECUTABLE_PATH"
    echo "📦 Tìm thấy executable: $APP_PATH"
else
    echo "❌ Không tìm thấy app tại:"
    echo "   - $APP_BUNDLE_PATH"
    echo "   - $APP_EXECUTABLE_PATH"
    exit 1
fi

echo "📦 App path: $APP_PATH"
echo "📊 File size: $(du -h "$APP_PATH" | cut -f1)"
echo ""

# Check permissions
echo "🔍 Kiểm tra permissions..."
ls -la "$APP_PATH"
echo ""

# Check if executable
if [ ! -x "$APP_PATH" ]; then
    echo "⚠️  App không có quyền thực thi, đang thêm..."
    chmod +x "$APP_PATH"
fi

# Check temp directory
echo "🔍 Kiểm tra temp directory..."
echo "TMPDIR: $TMPDIR"
echo "HOME: $HOME"
echo ""

# Try to create temp directory
TEMP_TEST="/tmp/etsycrawler_test"
echo "🔍 Test tạo thư mục temp..."
mkdir -p "$TEMP_TEST" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Có thể tạo thư mục temp"
    rm -rf "$TEMP_TEST"
else
    echo "❌ KHÔNG thể tạo thư mục temp"
fi
echo ""

# Check if running from DMG
if [ -d "/Volumes/EtsyCrawler DragonMedia" ] || [ -d "/Volumes/EtsyCrawlerDragonMedia" ]; then
    echo "⚠️  App đang chạy từ DMG (read-only)"
    echo "   Nên copy app vào Applications trước khi chạy"
fi
echo ""

# Run app with full output
echo "🚀 Chạy app với output đầy đủ..."
echo "----------------------------------------"
"$APP_PATH" 2>&1
EXIT_CODE=$?
echo "----------------------------------------"
echo ""
echo "Exit code: $EXIT_CODE"

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ App bị lỗi!"
    echo ""
    echo "🔍 Các nguyên nhân có thể:"
    echo "   1. PyInstaller không thể tạo temp directory"
    echo "   2. App đang chạy từ DMG (read-only)"
    echo "   3. Thiếu quyền truy cập"
    echo ""
    echo "💡 Giải pháp:"
    echo "   1. Copy app vào Applications: cp dist/EtsyCrawlerDragonMedia.app /Applications/"
    echo "   2. Hoặc chạy từ thư mục có quyền ghi"
    echo "   3. Kiểm tra Console.app để xem logs chi tiết"
fi

