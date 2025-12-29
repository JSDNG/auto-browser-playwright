#!/bin/bash
# Build script: Build executable + tạo installer
# Usage: bash scripts/build_installer.sh [mac]

set -e

echo "=========================================="
echo "Building Etsy Crawler (Mac)"
echo "=========================================="
echo ""

# Check if pyinstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller chưa được cài đặt!"
    echo "   Chạy: pip install pyinstaller"
    exit 1
fi

# Check if we're in the project root
if [ ! -f "build.spec" ]; then
    echo "❌ Không tìm thấy build.spec!"
    echo "   Hãy chạy script từ thư mục gốc của project"
    exit 1
fi

# Clean previous builds
echo "🧹 Đang xóa build cũ..."
rm -rf build/ dist/

# Build PyInstaller executable
echo "📦 Building PyInstaller executable..."
pyinstaller build.spec

# Build DMG
echo "📦 Building Mac DMG..."
bash installer/mac/create_dmg.sh

echo ""
echo "✅ Build hoàn tất!"
echo "   Executable: dist/EtsyCrawler"
echo "   DMG: installer/mac/output/EtsyCrawler-*.dmg"
echo ""

