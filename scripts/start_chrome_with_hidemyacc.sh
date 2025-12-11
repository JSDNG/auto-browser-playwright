#!/bin/bash

# Script để khởi động Chrome với HideMyAcc profile qua CDP

PORT=${1:-9222}  # Port mặc định 9222
PROFILE_ID=${2}  # ID của HideMyAcc profile

if [ -z "$PROFILE_ID" ]; then
    echo "❌ Thiếu tham số PROFILE_ID"
    echo ""
    echo "Cú pháp:"
    echo "  $0 [PORT] [PROFILE_ID]"
    echo ""
    echo "Ví dụ:"
    echo "  $0 9222 profile1"
    echo ""
    echo "Để xem danh sách profiles, chạy:"
    echo "  python3 -m src.utils.hidemyacc"
    exit 1
fi

# Tìm profile
echo "Đang tìm HideMyAcc profile: $PROFILE_ID..."

# Get the script directory to find the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

PYTHON_SCRIPT=$(cat <<EOF
from pathlib import Path
import sys
sys.path.insert(0, "$PROJECT_ROOT")
from src.utils.hidemyacc import HideMyAccManager

manager = HideMyAccManager()
profile = manager.get_profile_by_id("$PROFILE_ID")
if profile:
    print(profile["user_data_dir"])
else:
    print("NOT_FOUND")
    sys.exit(1)
EOF
)

PROFILE_PATH=$(python3 -c "$PYTHON_SCRIPT")

if [ "$PROFILE_PATH" = "NOT_FOUND" ] || [ -z "$PROFILE_PATH" ]; then
    echo "❌ Không tìm thấy profile: $PROFILE_ID"
    echo ""
    echo "Danh sách profiles có sẵn:"
    python3 -m src.utils.hidemyacc
    exit 1
fi

echo "✓ Tìm thấy profile tại: $PROFILE_PATH"
echo ""

# Kiểm tra xem profile có tồn tại không
if [ ! -d "$PROFILE_PATH" ]; then
    echo "❌ Profile path không tồn tại: $PROFILE_PATH"
    exit 1
fi

echo "Khởi động Chrome với HideMyAcc profile qua CDP..."
echo "Port: $PORT"
echo "Profile: $PROFILE_ID"
echo "User Data Dir: $PROFILE_PATH"
echo ""

# Tìm Marco browser từ HideMyAcc (HideMyAcc sử dụng Marco browser, không phải Chrome chính)
MARCO_BROWSER=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Tìm phiên bản Marco mới nhất
    MARCO_DIR=$(ls -dt ~/.hidemyacc/browser/marco-browser-* 2>/dev/null | head -1)
    if [ -n "$MARCO_DIR" ] && [ -f "$MARCO_DIR/Marco.app/Contents/MacOS/Marco" ]; then
        MARCO_BROWSER="$MARCO_DIR/Marco.app/Contents/MacOS/Marco"
        echo "✓ Tìm thấy Marco browser: $MARCO_BROWSER"
    fi
fi

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -n "$MARCO_BROWSER" ] && [ -f "$MARCO_BROWSER" ]; then
        # Sử dụng Marco browser từ HideMyAcc
        "$MARCO_BROWSER" \
            --remote-debugging-port=$PORT \
            --user-data-dir="$PROFILE_PATH" \
            --no-first-run \
            --no-default-browser-check \
            --disable-blink-features=AutomationControlled \
            --disable-infobars \
            2>/dev/null &
        
        PID=$!
        echo "✓ Marco browser (HideMyAcc) đã được khởi động (PID: $PID)"
    else
        # Fallback về Chrome chính nếu không tìm thấy Marco
        echo "⚠️  Không tìm thấy Marco browser, sử dụng Chrome chính..."
        /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
            --remote-debugging-port=$PORT \
            --user-data-dir="$PROFILE_PATH" \
            --no-first-run \
            --no-default-browser-check \
            --disable-blink-features=AutomationControlled \
            --disable-infobars \
            2>/dev/null &
        
        PID=$!
        echo "✓ Chrome đã được khởi động (PID: $PID)"
    fi
    echo ""
    echo "CDP endpoint: http://localhost:$PORT"
    echo "Kiểm tra: curl http://localhost:$PORT/json"
    
# Linux
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    google-chrome \
        --remote-debugging-port=$PORT \
        --user-data-dir="$PROFILE_PATH" \
        --no-first-run \
        --no-default-browser-check \
        --disable-blink-features=AutomationControlled \
        --disable-infobars \
        2>/dev/null &
    
    PID=$!
    echo "✓ Chrome đã được khởi động (PID: $PID)"
    echo ""
    echo "CDP endpoint: http://localhost:$PORT"
    echo "Kiểm tra: curl http://localhost:$PORT/json"
    
else
    echo "❌ Hệ điều hành không được hỗ trợ tự động"
    echo "Vui lòng khởi động Chrome thủ công với:"
    echo "  --remote-debugging-port=$PORT"
    echo "  --user-data-dir=\"$PROFILE_PATH\""
    exit 1
fi

# Chờ một chút để Chrome khởi động
sleep 2

# Kiểm tra CDP
if curl -s http://localhost:$PORT/json > /dev/null 2>&1; then
    echo "✓ CDP đang hoạt động!"
else
    echo "⚠️  CDP có thể chưa sẵn sàng, đợi thêm một chút..."
fi
