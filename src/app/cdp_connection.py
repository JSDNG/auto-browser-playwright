"""
Script đơn giản:
- Kết nối Playwright với một Chrome đã chạy sẵn qua CDP
- Điều hướng tới URL (mặc định: https://grok.com/) để test TM

Hướng dẫn nhanh:
1. Khởi động Chrome với CDP:
   macOS: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9224
   Linux: google-chrome --remote-debugging-port=9224
   Windows: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9224

2. Chạy script:
   python3 src/app/cdp_connection.py
   hoặc chỉ định URL khác:
   python3 src/app/cdp_connection.py https://grok.com/
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation


async def open_url_via_cdp(url: str = "https://grok.com/") -> None:
    """
    Kết nối tới Chrome đang chạy qua CDP rồi mở URL để test.
    """
    cdp_url = "http://localhost:9224"
    print("=" * 60)
    print(f"Kết nối Chrome qua CDP tại {cdp_url}")
    print(f"URL cần mở: {url}")
    print("=" * 60)

    automation = PlaywrightAutomation()

    try:
        # Kết nối tới Chrome đang chạy
        await automation.connect_over_cdp(cdp_url)
        print("✓ Đã kết nối Playwright với Chrome qua CDP")

        # Điều hướng tới URL
        await automation.navigate(url)
        title = await automation.page.title()
        print(f"✓ Đã mở trang, title: {title}")

        # Cho phép bạn quan sát trình duyệt một chút
        await asyncio.sleep(5)

    except Exception as e:
        print(f"❌ Lỗi khi mở URL qua CDP: {e}")
    finally:
        # Không đóng Chrome, chỉ detach Playwright
        await automation.detach()
        print("Đã detach Playwright, Chrome vẫn giữ nguyên.")


async def main():
    # Nếu có truyền URL qua CLI thì dùng, không thì mặc định grok.com
    url = sys.argv[1] if len(sys.argv) > 1 else "https://grok.com/"
    await open_url_via_cdp(url)


if __name__ == "__main__":
    asyncio.run(main())
