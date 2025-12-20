r"""
Kết nối Playwright với Chrome đang chạy qua CDP

Hướng dẫn sử dụng:
1. Khởi động Chrome với CDP:
   macOS: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223
   Linux: google-chrome --remote-debugging-port=9223
   Windows: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9223

2. Chạy script này:
   python3 src/app/cdp_connection.py
"""
import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.heyetsy_parser import extract_heyetsy_data
from src.core.automation import PlaywrightAutomation
from src.models import SearchInput

WEBHOOK_URL = "https://n8n.supover.com/webhook/crawler-etsy"


def _payload_to_json_bytes(data_iterable):
    """Convert iterable of mappings to JSON bytes."""
    return json.dumps(list(data_iterable), ensure_ascii=False).encode("utf-8")


def _post_json(webhook_url: str, payload: bytes):
    """Send JSON payload to webhook via POST."""
    request = Request(webhook_url, data=payload, method="POST")
    # Gửi JSON bytes nhưng Content-Type cần là application/json
    request.add_header("Content-Type", "application/json")
    request.add_header("Content-Length", str(len(payload)))
    with urlopen(request, timeout=30) as response:
        return response.read()


async def scrape_etsy_via_cdp(keyword: str = "t-shirt", pages: int = 5):
    """
    Core logic to scrape Etsy data and send to webhook.
    Can be called from CLI or from FastAPI.
    """
    search_input = SearchInput(keyword=keyword, pages=pages)
    print("=" * 60)
    print(f"Bắt đầu crawl Etsy: keyword='{search_input.keyword}', pages={search_input.pages}")
    print("=" * 60)

    automation = PlaywrightAutomation()
    all_data = {}

    try:
        # Kết nối với Chrome đang chạy qua CDP
        cdp_url = "http://localhost:9223"
        print(f"Đang kết nối với Chrome qua CDP tại {cdp_url}...")
        await automation.connect_over_cdp(cdp_url)
        print("✓ Đã kết nối thành công!")

        for page_num in range(1, search_input.pages + 1):
            target_url = (
                f"https://www.etsy.com/search?q={quote_plus(search_input.keyword)}"
                f"&page={page_num}&ref=pagination"
            )
            print(f"Đang điều hướng đến trang {page_num}: {target_url}")
            await automation.navigate(target_url)
            print(f"✓ Trang {page_num} - title: {await automation.page.title()}")

            # Chờ trang tải ổn định (10 giây)
            await asyncio.sleep(10)

            print("Đang lấy body và trích xuất dữ liệu...")
            try:
                body_html = await automation.page.evaluate(
                    """
                    () => {
                        const clone = document.body.cloneNode(true);
                        clone.querySelectorAll('script, style').forEach((el) => el.remove());
                        return clone.outerHTML;
                    }
                    """
                )

                cleaned_body = re.sub(r"\s+", " ", body_html).strip()

                # Trích xuất dữ liệu HeyEtsy từ body
                extracted = extract_heyetsy_data(cleaned_body)
                for item in extracted:
                    if not item.get("title") or not item.get("image"):
                        continue
                    lid = item.get("listing_id")
                    if lid and lid not in all_data:
                        all_data[lid] = item

                print(f"✓ Trang {page_num}: trích được {len(extracted)} mục (tổng duy nhất: {len(all_data)})")
            except Exception as e:
                print(f"❌ Lỗi khi xử lý trang {page_num}: {e}")

        # Gửi dữ liệu tới webhook
        if all_data:
            try:
                json_payload = _payload_to_json_bytes(all_data.values())
                print(f"Đang gửi {len(all_data)} mục tới webhook: {WEBHOOK_URL}")
                await asyncio.to_thread(_post_json, WEBHOOK_URL, json_payload)
                print("✓ Đã gửi dữ liệu thành công!")
            except Exception as e:
                print(f"❌ Lỗi khi gửi webhook: {e}")
        else:
            print("⚠️ Không có dữ liệu để gửi.")

        await automation.detach()
        return {
            "success": True,
            "count": len(all_data),
            "message": f"Đã crawl xong {len(all_data)} sản phẩm từ {search_input.pages} trang."
        }

    except Exception as e:
        print(f"❌ Lỗi trong quá trình scrape: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def connect_to_chrome_via_cdp():
    """Kết nối với Chrome đang chạy qua CDP và lưu dữ liệu HeyEtsy."""

    # Nhận từ khóa và số trang (CLI: arg1=keyword, arg2=pages)
    keyword = sys.argv[1] if len(sys.argv) > 1 else "t-shirt"
    pages_arg = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        pages_val = int(pages_arg) if pages_arg is not None else 5
    except Exception:
        pages_val = 5

    await scrape_etsy_via_cdp(keyword=keyword, pages=pages_val)


if __name__ == "__main__":
    asyncio.run(connect_to_chrome_via_cdp())
