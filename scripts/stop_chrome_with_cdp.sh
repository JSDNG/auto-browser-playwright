#!/bin/bash

# Script để dừng Chrome đang chạy với CDP

PORT=${1:-9222}  # Port mặc định 9222, có thể truyền vào tham số

echo "Đang tìm Chrome đang chạy với CDP tại port $PORT..."

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Tìm process Chrome với remote-debugging-port
    CHROME_PIDS=$(ps aux | grep -i "Google Chrome" | grep "remote-debugging-port=$PORT" | grep -v grep | awk '{print $2}')
    
    if [ -z "$CHROME_PIDS" ]; then
        echo "⚠️  Không tìm thấy Chrome nào đang chạy với CDP tại port $PORT"
        echo ""
        echo "Kiểm tra bằng cách:"
        echo "  ps aux | grep 'remote-debugging-port'"
        exit 0
    fi
    
    echo "Tìm thấy các process Chrome với CDP:"
    ps aux | grep -i "Google Chrome" | grep "remote-debugging-port=$PORT" | grep -v grep
    
    echo ""
    echo "Đang dừng Chrome..."
    
    # Kill từng process
    for PID in $CHROME_PIDS; do
        echo "  → Đang kill process $PID..."
        kill -TERM $PID 2>/dev/null || kill -KILL $PID 2>/dev/null
    done
    
    # Chờ một chút để process dừng
    sleep 1
    
    # Kiểm tra lại xem còn process nào không
    REMAINING=$(ps aux | grep -i "Google Chrome" | grep "remote-debugging-port=$PORT" | grep -v grep | awk '{print $2}')
    if [ -z "$REMAINING" ]; then
        echo "✓ Đã dừng Chrome thành công!"
    else
        echo "⚠️  Một số process vẫn còn chạy, đang force kill..."
        for PID in $REMAINING; do
            kill -KILL $PID 2>/dev/null
        done
        echo "✓ Đã force kill tất cả process!"
    fi
    
# Linux
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Tìm process Chrome với remote-debugging-port
    CHROME_PIDS=$(ps aux | grep -E "(google-chrome|chromium)" | grep "remote-debugging-port=$PORT" | grep -v grep | awk '{print $2}')
    
    if [ -z "$CHROME_PIDS" ]; then
        echo "⚠️  Không tìm thấy Chrome nào đang chạy với CDP tại port $PORT"
        exit 0
    fi
    
    echo "Tìm thấy các process Chrome với CDP:"
    ps aux | grep -E "(google-chrome|chromium)" | grep "remote-debugging-port=$PORT" | grep -v grep
    
    echo ""
    echo "Đang dừng Chrome..."
    
    # Kill từng process
    for PID in $CHROME_PIDS; do
        echo "  → Đang kill process $PID..."
        kill -TERM $PID 2>/dev/null || kill -KILL $PID 2>/dev/null
    done
    
    # Chờ một chút để process dừng
    sleep 1
    
    # Kiểm tra lại
    REMAINING=$(ps aux | grep -E "(google-chrome|chromium)" | grep "remote-debugging-port=$PORT" | grep -v grep | awk '{print $2}')
    if [ -z "$REMAINING" ]; then
        echo "✓ Đã dừng Chrome thành công!"
    else
        echo "⚠️  Một số process vẫn còn chạy, đang force kill..."
        for PID in $REMAINING; do
            kill -KILL $PID 2>/dev/null
        done
        echo "✓ Đã force kill tất cả process!"
    fi
    
else
    echo "❌ Hệ điều hành không được hỗ trợ tự động"
    echo "Vui lòng dừng Chrome thủ công hoặc sử dụng Task Manager"
    exit 1
fi

echo ""
echo "Kiểm tra CDP đã tắt:"
if curl -s "http://localhost:$PORT/json" > /dev/null 2>&1; then
    echo "⚠️  CDP vẫn còn hoạt động tại http://localhost:$PORT"
    echo "   Có thể cần đợi thêm vài giây hoặc có Chrome instance khác đang chạy"
else
    echo "✓ CDP đã tắt tại port $PORT"
fi
