#!/bin/bash
# Script để test DMG file
# Usage: bash installer/mac/test_dmg.sh

set -e

DMG_FILE="installer/mac/output/EtsyCrawlerDragonMedia-1.0.0.dmg"
MOUNT_POINT="/tmp/test_dmg_etsy"

echo "=========================================="
echo "Testing DMG File"
echo "=========================================="
echo ""

# Check if DMG exists
if [ ! -f "${DMG_FILE}" ]; then
    echo "❌ DMG file không tồn tại: ${DMG_FILE}"
    exit 1
fi

echo "📦 DMG File: ${DMG_FILE}"
echo "📊 File size: $(du -h "${DMG_FILE}" | cut -f1)"
echo ""

# Clean up old mount point
if [ -d "${MOUNT_POINT}" ]; then
    hdiutil detach "${MOUNT_POINT}" 2>/dev/null || true
    rm -rf "${MOUNT_POINT}"
fi

# Mount DMG
echo "🔍 Mounting DMG..."
hdiutil attach "${DMG_FILE}" -nobrowse -mountpoint "${MOUNT_POINT}" > /dev/null 2>&1
sleep 2

# Check contents
echo "📁 Contents of DMG:"
ls -la "${MOUNT_POINT}/"
echo ""

# Check if app bundle exists
if [ -d "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app" ]; then
    echo "✅ EtsyCrawlerDragonMedia.app found"
    
    # Check app structure
    if [ -f "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app/Contents/MacOS/EtsyCrawlerDragonMedia" ]; then
        echo "✅ Executable found"
        
        # Check executable permissions
        if [ -x "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app/Contents/MacOS/EtsyCrawlerDragonMedia" ]; then
            echo "✅ Executable has correct permissions"
        else
            echo "⚠️  Executable missing execute permission"
        fi
        
        # Check file size
        EXEC_SIZE=$(stat -f%z "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app/Contents/MacOS/EtsyCrawlerDragonMedia" 2>/dev/null || echo "0")
        if command -v numfmt &> /dev/null; then
            echo "   Size: $(numfmt --to=iec-i --suffix=B ${EXEC_SIZE} 2>/dev/null || echo "${EXEC_SIZE} bytes")"
        else
            # Fallback for macOS which doesn't have numfmt by default - use awk for calculation
            if [ ${EXEC_SIZE} -gt 1048576 ]; then
                SIZE_MB=$(awk "BEGIN {printf \"%.2f\", ${EXEC_SIZE}/1048576}")
                echo "   Size: ${SIZE_MB} MB"
            elif [ ${EXEC_SIZE} -gt 1024 ]; then
                SIZE_KB=$(awk "BEGIN {printf \"%.2f\", ${EXEC_SIZE}/1024}")
                echo "   Size: ${SIZE_KB} KB"
            else
                echo "   Size: ${EXEC_SIZE} bytes"
            fi
        fi
    else
        echo "❌ Executable not found in app bundle"
    fi
    
    # Check Info.plist
    if [ -f "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app/Contents/Info.plist" ]; then
        echo "✅ Info.plist found"
    else
        echo "⚠️  Info.plist not found"
    fi
else
    echo "⚠️  EtsyCrawlerDragonMedia.app not found (might be flat structure)"
    
    # Check for flat executable
    if [ -f "${MOUNT_POINT}/EtsyCrawlerDragonMedia" ]; then
        echo "✅ EtsyCrawlerDragonMedia executable found (flat structure)"
        if [ -x "${MOUNT_POINT}/EtsyCrawlerDragonMedia" ]; then
            echo "✅ Executable has correct permissions"
        fi
    fi
fi

# Check for Applications link
if [ -L "${MOUNT_POINT}/Applications" ]; then
    echo "✅ Applications link found"
else
    echo "⚠️  Applications link not found"
fi

# Check for README files
if [ -f "${MOUNT_POINT}/README.md" ]; then
    echo "✅ README.md found"
fi
if [ -f "${MOUNT_POINT}/README.txt" ]; then
    echo "✅ README.txt found"
fi
# Check config.ini in app bundle (should be hidden from user)
if [ -f "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app/Contents/MacOS/config.ini" ]; then
    echo "✅ config.ini found in app bundle (hidden from user)"
elif [ -f "${MOUNT_POINT}/config.ini" ]; then
    echo "⚠️  config.ini found in DMG root (should be in app bundle)"
fi

echo ""
echo "🔍 Checking code signature..."
if codesign -dv --verbose=4 "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app" 2>&1 | grep -q "code object is not signed"; then
    echo "⚠️  App is NOT code signed"
    echo "   Users may see security warnings when opening"
else
    codesign -dv --verbose=4 "${MOUNT_POINT}/EtsyCrawlerDragonMedia.app" 2>&1 | head -5
fi

echo ""
echo "🔍 Checking DMG signature..."
if codesign -dv --verbose=4 "${DMG_FILE}" 2>&1 | grep -q "code object is not signed"; then
    echo "⚠️  DMG is NOT code signed"
else
    codesign -dv --verbose=4 "${DMG_FILE}" 2>&1 | head -5
fi

# Unmount
echo ""
echo "🔓 Unmounting DMG..."
hdiutil detach "${MOUNT_POINT}" > /dev/null 2>&1
rm -rf "${MOUNT_POINT}"

echo ""
echo "✅ Test completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Open DMG manually: open ${DMG_FILE}"
echo "   2. Test drag & drop to Applications"
echo "   3. Test running the app"
echo "   4. Consider code signing for distribution"

