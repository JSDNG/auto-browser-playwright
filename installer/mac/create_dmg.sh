#!/bin/bash
# Script để tạo .dmg file cho Mac
# Usage: bash installer/mac/create_dmg.sh

set -e

APP_NAME="EtsyCrawlerDragonMedia"
APP_DISPLAY_NAME="EtsyCrawler DragonMedia"
APP_VERSION="1.0.1"
DMG_NAME="${APP_NAME}-${APP_VERSION}.dmg"
BUILD_DIR="dist"
DMG_DIR="installer/mac/dmg"
APP_BUNDLE_DIR="${DMG_DIR}/${APP_NAME}.app"
DMG_OUTPUT="installer/mac/output"
EXECUTABLE_PATH="${BUILD_DIR}/${APP_NAME}"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Copy config.ini to target directory
copy_config_file() {
    local target_dir="$1"
    if [ -f "config.ini" ]; then
        cp config.ini "${target_dir}/config.ini"
        echo "✅ config.ini đã được copy"
    elif [ -f "config.ini.example" ]; then
        cp config.ini.example "${target_dir}/config.ini"
        echo "⚠️  Đã copy config.ini.example (tên config.ini)"
    else
        echo "⚠️  config.ini và config.ini.example không tồn tại, app sẽ dùng default values"
    fi
}

# Copy documentation files to DMG root
copy_documentation() {
    local target_dir="$1"
    if [ -f "README.md" ]; then
        cp README.md "${target_dir}/"
    fi
    if [ -f "installer/mac/HUONG_DAN_CAI_DAT.md" ]; then
        cp installer/mac/HUONG_DAN_CAI_DAT.md "${target_dir}/"
    fi
}

# Clean up old build files
cleanup_build() {
    rm -rf "${DMG_DIR}"
    rm -f "${DMG_OUTPUT}/${DMG_NAME}"
    mkdir -p "${DMG_DIR}"
    mkdir -p "${DMG_OUTPUT}"
}

# Create app bundle structure
create_app_bundle_structure() {
    mkdir -p "${APP_BUNDLE_DIR}/Contents/MacOS"
    mkdir -p "${APP_BUNDLE_DIR}/Contents/Resources"
}

# Copy executable to app bundle
copy_executable() {
    cp "${EXECUTABLE_PATH}" "${APP_BUNDLE_DIR}/Contents/MacOS/_${APP_NAME}"
    chmod +x "${APP_BUNDLE_DIR}/Contents/MacOS/_${APP_NAME}"
}

# Create wrapper script for PyInstaller temp directory fix
create_wrapper_script() {
    cat > "${APP_BUNDLE_DIR}/Contents/MacOS/${APP_NAME}" << WRAPPER_EOF
#!/bin/bash
# Wrapper script to fix PyInstaller temp directory issue
TMP_BASE="\${HOME}/.etsycrawlerdragonmedia_temp"
mkdir -p "\$TMP_BASE"
export TMPDIR="\$TMP_BASE"
export _MEIPASS2="\$TMPDIR"
exec "\$(dirname "\$0")/_${APP_NAME}" "\$@"
WRAPPER_EOF
    chmod +x "${APP_BUNDLE_DIR}/Contents/MacOS/${APP_NAME}"
}

# Create Info.plist for app bundle
create_info_plist() {
    cat > "${APP_BUNDLE_DIR}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.etsycrawlerdragonmedia.app</string>
    <key>CFBundleName</key>
    <string>${APP_DISPLAY_NAME}</string>
    <key>CFBundleVersion</key>
    <string>${APP_VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${APP_VERSION}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
EOF
}

# Create DMG using create-dmg tool
create_dmg_with_tool() {
    local volicon_option=""
    if [ -f "installer/mac/icon.icns" ]; then
        volicon_option="--volicon installer/mac/icon.icns"
    fi

    create-dmg \
        --volname "${APP_DISPLAY_NAME}" \
        ${volicon_option} \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 150 200 \
        --hide-extension "${APP_NAME}.app" \
        --app-drop-link 450 200 \
        --hdiutil-quiet \
        "${DMG_OUTPUT}/${DMG_NAME}" \
        "${DMG_DIR}"
}

# Build app bundle (used by main flow)
build_app_bundle() {
    echo "📦 Tạo app bundle..."
    create_app_bundle_structure
    copy_executable
    create_wrapper_script
    create_info_plist
    copy_config_file "${APP_BUNDLE_DIR}/Contents/MacOS"
    echo "✅ App bundle đã được tạo"
}

# Build simple DMG structure (used by fallback)
build_simple_dmg_structure() {
    echo "📦 Tạo DMG structure (fallback)..."
    cp "${EXECUTABLE_PATH}" "${DMG_DIR}/"
    chmod +x "${DMG_DIR}/${APP_NAME}"
    copy_config_file "${DMG_DIR}"
    copy_documentation "${DMG_DIR}"
}

# Print completion message
print_completion_message() {
    echo ""
    echo "✅ DMG đã được tạo: ${DMG_OUTPUT}/${DMG_NAME}"
    echo ""
    echo "📝 Lưu ý:"
    echo "   - DMG có thể cần code signing để tránh warning trên Mac"
    echo "   - User cần drag app vào Applications folder"
    echo "   - User cần cài Google Chrome (app sẽ tự động khởi động Chrome với CDP)"
    echo "   - config.ini đã được ẩn trong app bundle, user cấu hình qua GUI"
}

# ============================================================================
# MAIN FLOW
# ============================================================================

echo "=========================================="
echo "Creating DMG for Mac"
echo "=========================================="
echo ""

# Check if executable exists
if [ ! -f "${EXECUTABLE_PATH}" ]; then
    echo "❌ Không tìm thấy executable: ${EXECUTABLE_PATH}"
    echo "   Hãy build PyInstaller trước: bash scripts/build.sh"
    exit 1
fi

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "❌ create-dmg chưa được cài đặt, không thể tạo DMG"
    echo "   Vui lòng cài đặt: brew install create-dmg"
    exit 1
fi

# Main flow: Create app bundle and DMG with create-dmg
cleanup_build
build_app_bundle
copy_documentation "${DMG_DIR}"
create_dmg_with_tool
print_completion_message
