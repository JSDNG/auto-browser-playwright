r"""
Kết nối Playwright với Chrome đang chạy qua CDP

Hướng dẫn sử dụng:
1. Khởi động Chrome với CDP:
   macOS: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   Linux: google-chrome --remote-debugging-port=9222
   Windows: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

2. Chạy script này:
   python3 src/app/cdp_connection.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation


async def connect_to_chrome_via_cdp():
    """Kết nối với Chrome đang chạy qua CDP và kiểm tra is_delivered"""

    print("=" * 60)
    print("Kết nối Playwright với Chrome qua CDP")
    print("=" * 60)
    print()

    automation = PlaywrightAutomation()

    try:
        # Kết nối với Chrome đang chạy qua CDP
        print("Đang kết nối với Chrome qua CDP tại http://localhost:9222...")
        await automation.connect_over_cdp("http://localhost:9222")
        print("✓ Đã kết nối thành công!")
        print()

        # Điều hướng đến URL
        url = "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
        print(f"Đang điều hướng đến {url}...")
        await automation.navigate(url)
        print(f"✓ Đã điều hướng thành công!")
        
        # Chờ trang load hoàn toàn
        print("Đang chờ trang load hoàn toàn...")
        await asyncio.sleep(2)
        
        # Lấy text content của body
        body_text = await automation.page.evaluate("() => document.body.innerText")
        body_text_lower = body_text.lower() if body_text else ""
        
        # Kiểm tra điều kiện delivered
        required_phrases = ["Your item was delivered", "Latest Update", "Delivered"]
        found_phrases = []
        missing_phrases = []
        
        for phrase in required_phrases:
            if phrase.lower() in body_text_lower:
                found_phrases.append(phrase)
            else:
                missing_phrases.append(phrase)
        
        # Kiểm tra nếu cả 3 cụm từ đều có
        is_delivered = len(found_phrases) == len(required_phrases)
        
        # Print kết quả
        print("=" * 60)
        print("Kiểm tra trạng thái delivered:")
        print("=" * 60)
        print(f"is_delivered = {str(is_delivered).lower()}")
        if found_phrases:
            print(f"✓ Tìm thấy ({len(found_phrases)}/{len(required_phrases)}): {', '.join(found_phrases)}")
        if missing_phrases:
            print(f"✗ Thiếu ({len(missing_phrases)}/{len(required_phrases)}): {', '.join(missing_phrases)}")
        print()
        
        # Lưu ý: KHÔNG đóng browser vì đây là Chrome của bạn
        print("⚠️  Lưu ý: Browser sẽ KHÔNG bị đóng vì đây là Chrome của bạn")
        print("   Chỉ detach khỏi Playwright...")
        await automation.detach()
        print("✓ Đã detach thành công!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print()
        print("Kiểm tra:")
        print("1. Chrome đã khởi động với --remote-debugging-port=9222 chưa?")
        print("2. Thử truy cập http://localhost:9222/json để xác nhận CDP đang chạy")
        print("3. Port có đúng không? (mặc định 9222)")


if __name__ == "__main__":
    asyncio.run(connect_to_chrome_via_cdp())
