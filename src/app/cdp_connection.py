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
    """Kết nối với Chrome đang chạy qua CDP và thu thập dữ liệu Etsy"""

    print("=" * 60)
    print("Kết nối Playwright với Chrome qua CDP")
    print("=" * 60)
    print()

    automation = PlaywrightAutomation()
    captured_data = []

    # Hàm xử lý response từ Etsy API
    async def handle_etsy(response):
        """Bắt và xử lý response từ Etsy API"""
        try:
            # Lọc các API endpoint quan trọng của Etsy
            if ("bespoke.etsy.com" in response.url or
                "/api/" in response.url or
                "listing" in response.url) and response.status == 200:

                # Chỉ xử lý JSON responses
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    try:
                        json_data = await response.json()
                        captured_data.append({
                            "url": response.url,
                            "status": response.status,
                            "data": json_data
                        })
                        print(f"✓ Đã bắt API: {response.url[:80]}...")
                    except Exception as e:
                        print(f"⚠ Không parse được JSON từ {response.url[:50]}...: {e}")
        except Exception as e:
            pass  # Bỏ qua lỗi để không làm gián đoạn flow

    try:
        # Kết nối với Chrome đang chạy qua CDP
        print("Đang kết nối với Chrome qua CDP tại http://localhost:9222...")
        await automation.connect_over_cdp("http://localhost:9222")
        print("✓ Đã kết nối thành công!")
        print()

        # Hiển thị thông tin
        print(f"Browser: {automation.browser}")
        print(f"Context: {automation.context}")
        print(f"Page URL hiện tại: {automation.page.url}")
        print()

        # Thiết lập listener để bắt network responses
        print("Đang thiết lập network interception...")
        automation.page.on("response", handle_etsy)
        print("✓ Network interception đã sẵn sàng!")
        print()

        # Điều hướng đến URL mới
        url = "https://www.etsy.com/listing/1382196280/custom-boat-tote-bag-canvas-tote-bag?ref=hp_editors_picks_primary-3&logging_key=1e4a37ab2e6157035f7997723d8d8b03643ba35a%3A1382196280"
        print(f"Đang điều hướng đến {url}...")
        await automation.navigate(url)
        print(f"✓ Đã điều hướng thành công!")
        print(f"Page title: {await automation.page.title()}")
        print()

        # Chờ để bắt các API responses
        print("Đang chờ và thu thập dữ liệu từ API responses...")
        await asyncio.sleep(5)

        # Hiển thị kết quả
        print()
        print("=" * 60)
        print(f"Đã bắt được {len(captured_data)} API responses")
        print("=" * 60)
        if captured_data:
            for i, item in enumerate(captured_data, 1):
                print(f"\n[{i}] URL: {item['url']}")
                print(f"    Status: {item['status']}")
                print(f"    Data keys: {list(item['data'].keys()) if isinstance(item['data'], dict) else 'Not a dict'}")
        else:
            print("\n⚠ Không bắt được API response nào. Etsy có thể đã thay đổi cấu trúc API.")
        print()
        
        # Lưu ý: KHÔNG đóng browser vì đây là Chrome của bạn
        print()
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
