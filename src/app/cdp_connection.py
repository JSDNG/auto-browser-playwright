r"""
Kết nối Playwright với Chrome đang chạy qua CDP.

CONFIG: DEFAULT_CDP_ENDPOINT, DEFAULT_WAIT_TIME_SECONDS, DEFAULT_REQUIRED_PHRASES
được đọc từ `config.py` (nạp từ file `.env` ở project root) — sửa trong `.env`
nếu deploy ở môi trường khác (Chrome port khác, logic delivered khác).
DEFAULT_TRACKING_URL chỉ dùng để test nhanh CLI, giữ hardcode trong file này.

Hướng dẫn sử dụng CLI test nhanh:
1. Khởi động Chrome với CDP:
   macOS: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   Linux: google-chrome --remote-debugging-port=9222
   Windows: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug"

2. Chạy script này:
   python src/app/cdp_connection.py
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation
from config import CDP_ENDPOINT, WAIT_TIME_SECONDS, REQUIRED_PHRASES

# URL mặc định để test CLI (không dùng trong API batch)
DEFAULT_TRACKING_URL = "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9400150105794041827256"

# Đọc từ .env qua config.py (xem .env-example)
DEFAULT_CDP_ENDPOINT = CDP_ENDPOINT
DEFAULT_WAIT_TIME_SECONDS = WAIT_TIME_SECONDS
DEFAULT_REQUIRED_PHRASES = REQUIRED_PHRASES


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_to_chrome_via_cdp(
    url: str = DEFAULT_TRACKING_URL,
    cdp_endpoint: str = DEFAULT_CDP_ENDPOINT,
    wait_time: int = DEFAULT_WAIT_TIME_SECONDS,
    required_phrases: list = None
) -> dict:
    """
    Kết nối với Chrome đang chạy qua CDP và kiểm tra is_delivered.
    
    Args:
        url: URL cần điều hướng đến.
        cdp_endpoint: CDP endpoint (mặc định: DEFAULT_CDP_ENDPOINT).
        wait_time: Thời gian chờ trang load (giây, mặc định: DEFAULT_WAIT_TIME_SECONDS).
        required_phrases: Danh sách cụm từ cần kiểm tra (mặc định: DEFAULT_REQUIRED_PHRASES).
    
    Returns:
        dict: Kết quả với các keys:
            - success: bool
            - is_delivered: bool
            - found_phrases: list
            - missing_phrases: list
            - body_text: str (optional)
            - delivered_date: str | None
            - error: str (nếu có lỗi)
    """
    if required_phrases is None:
        required_phrases = DEFAULT_REQUIRED_PHRASES.copy()

    automation = PlaywrightAutomation()

    try:
        # Kết nối với Chrome đang chạy qua CDP
        await automation.connect_over_cdp(cdp_endpoint)

        # Điều hướng đến URL
        await automation.navigate(url)
        
        # Chờ trang load hoàn toàn
        await asyncio.sleep(wait_time)
        
        # Lấy text content của body
        body_text = await automation.page.evaluate("() => document.body.innerText")
        body_text_lower = body_text.lower() if body_text else ""
        
        # Kiểm tra điều kiện delivered
        found_phrases = []
        missing_phrases = []
        
        for phrase in required_phrases:
            if phrase.lower() in body_text_lower:
                found_phrases.append(phrase)
            else:
                missing_phrases.append(phrase)
        
        # Kiểm tra nếu cả 3 cụm từ đều có
        is_delivered = len(found_phrases) == len(required_phrases)
        
        # Lấy date: tìm trong class "delivered-status" (cha) -> tìm class "tb-date" (con) để lấy giá trị
        delivered_date = None
        
        try:
            # Tìm element cha có class "delivered-status"
            delivered_status_element = await automation.page.query_selector(".delivered-status")
            if delivered_status_element:
                # Trong element cha, tìm element con có class "tb-date"
                tb_date_element = await delivered_status_element.query_selector(".tb-date")
                if tb_date_element:
                    delivered_date = await tb_date_element.text_content()
                    if delivered_date:
                        # Loại bỏ \n và \t nếu có
                        delivered_date = delivered_date.replace("\n", " ").replace("\t", " ").strip()
                        # Loại bỏ khoảng trắng thừa (nhiều khoảng trắng liên tiếp)
                        delivered_date = " ".join(delivered_date.split())
                    else:
                        delivered_date = None
        except Exception as e:
            logger.warning(f"Could not extract date from .delivered-status .tb-date: {e}")
        
        # Detach khỏi Playwright (không đóng browser)
        await automation.detach()
        
        return {
            "success": True,
            "is_delivered": is_delivered,
            "found_phrases": found_phrases,
            "missing_phrases": missing_phrases,
            "body_text": body_text if body_text else "",  # Trả về toàn bộ để có thể parse thời gian
            "delivered_date": delivered_date  # Date từ .delivered-status .tb-date
        }
        
    except Exception as e:
        # Đảm bảo detach nếu có lỗi
        try:
            await automation.detach()
        except:
            pass
        
        return {
            "success": False,
            "is_delivered": False,
            "found_phrases": [],
            "missing_phrases": required_phrases,
            "error": str(e)
        }


async def connect_to_chrome_via_cdp_cli():
    """CLI wrapper cho hàm connect_to_chrome_via_cdp (giữ nguyên để tương thích)"""
    print("=" * 60)
    print("Kết nối Playwright với Chrome qua CDP")
    print("=" * 60)
    print()

    # Dùng cấu hình mặc định đã khai báo ở trên
    result = await connect_to_chrome_via_cdp(
        url=DEFAULT_TRACKING_URL,
        cdp_endpoint=DEFAULT_CDP_ENDPOINT,
        wait_time=DEFAULT_WAIT_TIME_SECONDS,
        required_phrases=DEFAULT_REQUIRED_PHRASES.copy(),
    )
    
    if result["success"]:
        print("=" * 60)
        print("Kiểm tra trạng thái delivered:")
        print("=" * 60)
        print(f"is_delivered = {str(result['is_delivered']).lower()}")
        if result["found_phrases"]:
            print(f"✓ Tìm thấy ({len(result['found_phrases'])}/{len(result['found_phrases']) + len(result['missing_phrases'])}): {', '.join(result['found_phrases'])}")
        if result["missing_phrases"]:
            print(f"✗ Thiếu ({len(result['missing_phrases'])}/{len(result['found_phrases']) + len(result['missing_phrases'])}): {', '.join(result['missing_phrases'])}")
        print()
        print("⚠️  Lưu ý: Browser sẽ KHÔNG bị đóng vì đây là Chrome của bạn")
        print("   Chỉ detach khỏi Playwright...")
        print("✓ Đã detach thành công!")
    else:
        print(f"❌ Lỗi: {result.get('error', 'Unknown error')}")
        print()
        print("Kiểm tra:")
        print("1. Chrome đã khởi động với --remote-debugging-port=9222 chưa?")
        print("2. Thử truy cập http://localhost:9222/json để xác nhận CDP đang chạy")
        print("3. Port có đúng không? (mặc định 9222)")


if __name__ == "__main__":
    asyncio.run(connect_to_chrome_via_cdp_cli())
