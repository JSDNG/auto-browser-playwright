#!/bin/bash
# Script để tạo .dmg file cho Mac
# Usage: bash installer/mac/create_dmg.sh

set -e

APP_NAME="EtsyCrawler"
APP_VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${APP_VERSION}.dmg"
BUILD_DIR="dist"
DMG_DIR="installer/mac/dmg"
APP_BUNDLE_DIR="${DMG_DIR}/${APP_NAME}.app"
DMG_OUTPUT="installer/mac/output"

echo "=========================================="
echo "Creating DMG for Mac"
echo "=========================================="
echo ""

# Check if PyInstaller build exists
if [ ! -f "${BUILD_DIR}/${APP_NAME}" ]; then
    echo "❌ Không tìm thấy executable: ${BUILD_DIR}/${APP_NAME}"
    echo "   Hãy build PyInstaller trước: bash scripts/build.sh"
    exit 1
fi

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "⚠️  create-dmg chưa được cài đặt"
    echo "   Cài đặt: brew install create-dmg"
    echo ""
    echo "   Hoặc dùng Disk Utility thủ công (xem hướng dẫn bên dưới)"
    echo ""
    
    # Fallback: Tạo DMG thủ công với hdiskutil
    echo "📦 Tạo DMG thủ công với hdiutil..."
    
    # Clean up
    rm -rf "${DMG_DIR}"
    rm -f "${DMG_OUTPUT}/${DMG_NAME}"
    mkdir -p "${DMG_DIR}"
    mkdir -p "${DMG_OUTPUT}"
    
    # Copy executable
    cp "${BUILD_DIR}/${APP_NAME}" "${DMG_DIR}/"
    chmod +x "${DMG_DIR}/${APP_NAME}"
    
    # Copy README and config
    cp README.md "${DMG_DIR}/"
    cp config.ini "${DMG_DIR}/"
    cp installer/mac/README.txt "${DMG_DIR}/"
    
    # Create DMG
    hdiutil create -volname "${APP_NAME}" -srcfolder "${DMG_DIR}" -ov -format UDZO \
        "${DMG_OUTPUT}/${DMG_NAME}"
    
    echo ""
    echo "✅ DMG đã được tạo: ${DMG_OUTPUT}/${DMG_NAME}"
    exit 0
fi

# Clean up
rm -rf "${DMG_DIR}"
rm -f "${DMG_OUTPUT}/${DMG_NAME}"
mkdir -p "${DMG_DIR}"
mkdir -p "${DMG_OUTPUT}"

# Create app bundle structure
mkdir -p "${APP_BUNDLE_DIR}/Contents/MacOS"
mkdir -p "${APP_BUNDLE_DIR}/Contents/Resources"

# Copy executable
cp "${BUILD_DIR}/${APP_NAME}" "${APP_BUNDLE_DIR}/Contents/MacOS/${APP_NAME}"
chmod +x "${APP_BUNDLE_DIR}/Contents/MacOS/${APP_NAME}"

# Create Info.plist
cat > "${APP_BUNDLE_DIR}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.etsycrawler.app</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>${APP_VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${APP_VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

# Copy README and config to DMG root (outside app bundle)
cp README.md "${DMG_DIR}/"
cp config.ini "${DMG_DIR}/"
cp installer/mac/README.txt "${DMG_DIR}/"

# Create DMG using create-dmg
create-dmg \
    --volname "${APP_NAME}" \
    --volicon "installer/mac/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 150 200 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 450 200 \
    --hdiutil-quiet \
    "${DMG_OUTPUT}/${DMG_NAME}" \
    "${DMG_DIR}"

echo ""
echo "✅ DMG đã được tạo: ${DMG_OUTPUT}/${DMG_NAME}"
echo ""
echo "📝 Lưu ý:"
echo "   - DMG có thể cần code signing để tránh warning trên Mac"
echo "   - User cần drag app vào Applications folder"
echo "   - User cần cài Chrome và Playwright browsers"

