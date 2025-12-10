#!/bin/bash

# Script để khởi động Chrome với CDP trên macOS

PORT=${1:-9222}  # Port mặc định 9222, có thể truyền vào tham số

# Tạo thư mục user data riêng cho CDP
USER_DATA_DIR="/tmp/chrome-cdp-profile"
mkdir -p "$USER_DATA_DIR"

echo "Khởi động Chrome với CDP tại port $PORT..."
echo "URL endpoint: http://localhost:$PORT"
echo "User data directory: $USER_DATA_DIR"
echo ""

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
        --remote-debugging-port=$PORT \
        --user-data-dir="$USER_DATA_DIR" \
        --no-first-run \
        --no-default-browser-check &
    echo "✓ Chrome đã được khởi động với CDP"
    echo ""
    echo "Kiểm tra CDP bằng cách truy cập: http://localhost:$PORT/json"
    echo "Hoặc chạy: curl http://localhost:$PORT/json"
    
# Linux
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    google-chrome \
        --remote-debugging-port=$PORT \
        --user-data-dir="$USER_DATA_DIR" \
        --no-first-run \
        --no-default-browser-check &
    echo "✓ Chrome đã được khởi động với CDP"
    echo ""
    echo "Kiểm tra CDP bằng cách truy cập: http://localhost:$PORT/json"
    echo "Hoặc chạy: curl http://localhost:$PORT/json"
    
else
    echo "❌ Hệ điều hành không được hỗ trợ tự động"
    echo "Vui lòng khởi động Chrome thủ công với flag: --remote-debugging-port=$PORT"
fi
