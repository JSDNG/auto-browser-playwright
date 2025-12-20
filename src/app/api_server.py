"""
FastAPI server để crawl dữ liệu Etsy.

Cung cấp 2 endpoints:
- /api/v1/etsy/scrape: CDP connection (yêu cầu Chrome đã chạy với CDP)
- /api/v1/etsy/scrape_hidemyacc: HideMyAcc profile (tự động launch)

Xem docs/ETSY_SCRAPING_API.md để biết chi tiết cách sử dụng.
"""
# CRITICAL: Set Windows event loop policy FIRST, before any imports
import sys
import asyncio
import platform

# Fix Windows event loop issue - MUST be first
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from pathlib import Path

# Add project root to path BEFORE importing from src
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Optional
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import logging

from src.utils.hidemyacc import HideMyAccManager
from src.core.automation import PlaywrightAutomation
from src.models import SearchInput, HideMyAccSearchInput
from src.app.cdp_connection import scrape_etsy_via_cdp, _payload_to_json_bytes, _post_json, WEBHOOK_URL
from src.app.hidemyacc_connection_profile import launch_hidemyacc_profile_for_api
from src.utils.heyetsy_parser import extract_heyetsy_data
import re
import json
from urllib.parse import quote_plus
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# =========================
# CẤU HÌNH CỐ ĐỊNH (INLINE)
# =========================

# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5674

# CDP port cho Chrome/Marco (HideMyAcc)
CONFIG_CDP_PORT = 9223


# Setup logging (đơn giản, log ra stdout/terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HideMyAcc Automation API",
    description="API đơn giản để khởi động HideMyAcc profile + Chrome/Marco và kết nối Playwright qua CDP",
    version="1.0.0",
)

# Create API router với prefix /api/v1
api_router = APIRouter(prefix="/api/v1")


class HideMyAccConnectionResponse(BaseModel):
    """Response cho việc kết nối HideMyAcc profile"""

    success: bool
    message: str
    profile_id: Optional[str] = None
    profile_name: Optional[str] = None
    cdp_port: Optional[int] = None


# @api_router.post("/hidemyacc/connect", response_model=HideMyAccConnectionResponse)
# async def connect_hidemyacc_profile() -> HideMyAccConnectionResponse:
#     # ... existing implementation ...
#     pass


class EtsyScrapeResponse(BaseModel):
    """Response cho việc crawl Etsy"""

    success: bool
    message: str
    count: Optional[int] = 0
    error: Optional[str] = None


async def scrape_etsy_with_profile(
    keyword: str = "t-shirt",
    pages: int = 5,
    profile_id: str = None,
    use_command_line_config: bool = True,
    proxy_server: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
):
    """
    Scrape Etsy với HideMyAcc profile.
    
    Launch profile -> navigate -> extract -> gửi webhook -> detach.
    Xem docs/ETSY_SCRAPING_API.md để biết chi tiết.
    """
    search_input = SearchInput(keyword=keyword, pages=pages)
    logger.info(f"Bắt đầu scrape Etsy với profile: keyword='{search_input.keyword}', pages={search_input.pages}")
    
    automation = None
    all_data = {}
    
    try:
        # Bước 1: Launch HideMyAcc profile
        # - Tự động tìm Marco browser executable
        # - Cấu hình proxy nếu có (hoặc không dùng proxy)
        # - Launch Playwright với profile qua user-data-dir
        # - Trả về automation object để tiếp tục sử dụng
        logger.info("Đang launch HideMyAcc profile...")
        automation, profile_info = await launch_hidemyacc_profile_for_api(
            profile_id=profile_id,
            use_command_line_config=use_command_line_config,
            cdp_port=CONFIG_CDP_PORT,
            proxy_server=proxy_server,
            proxy_username=proxy_username,
            proxy_password=proxy_password
        )
        
        if not automation or not profile_info:
            return {
                "success": False,
                "error": "Không thể launch HideMyAcc profile"
            }
        
        logger.info(f"✓ Đã launch profile: {profile_info['profile_name']}")
        
        # Bước 2: Mở Etsy và thực hiện search
        # - Navigate đến từng trang Etsy search (page 1 đến page N)
        # - Chờ 10 giây để trang tải ổn định (Etsy là SPA, cần thời gian render)
        # - Extract HTML body và parse dữ liệu HeyEtsy
        logger.info("Đang mở Etsy và thực hiện search...")
        
        for page_num in range(1, search_input.pages + 1):
            target_url = (
                f"https://www.etsy.com/search?q={quote_plus(search_input.keyword)}"
                f"&page={page_num}&ref=pagination"
            )
            logger.info(f"Đang điều hướng đến trang {page_num}: {target_url}")
            await automation.navigate(target_url)
            logger.info(f"✓ Trang {page_num} - title: {await automation.page.title()}")
            
            # Chờ trang tải ổn định (10 giây)
            await asyncio.sleep(10)
            
            logger.info("Đang lấy body và trích xuất dữ liệu...")
            try:
                # Extract HTML body từ page (loại bỏ script và style tags để giảm kích thước)
                # Clone body để không ảnh hưởng đến DOM gốc
                body_html = await automation.page.evaluate(
                    """
                    () => {
                        const clone = document.body.cloneNode(true);
                        clone.querySelectorAll('script, style').forEach((el) => el.remove());
                        return clone.outerHTML;
                    }
                    """
                )
                
                # Normalize whitespace để dễ parse
                cleaned_body = re.sub(r"\s+", " ", body_html).strip()
                
                # Trích xuất dữ liệu HeyEtsy từ body HTML
                # Parser tìm các pattern đặc biệt trong HTML để extract product info
                extracted = extract_heyetsy_data(cleaned_body)
                
                # Lọc và deduplicate theo listing_id
                # Chỉ lấy items có title và image, loại bỏ duplicates
                for item in extracted:
                    if not item.get("title") or not item.get("image"):
                        continue
                    lid = item.get("listing_id")
                    if lid and lid not in all_data:
                        all_data[lid] = item
                
                logger.info(f"✓ Trang {page_num}: trích được {len(extracted)} mục (tổng duy nhất: {len(all_data)})")
            except Exception as e:
                logger.error(f"❌ Lỗi khi xử lý trang {page_num}: {e}")
        
        # Bước 3: Gửi dữ liệu tới webhook
        # - Convert dict values thành JSON bytes
        # - POST tới webhook n8n (async thread để không block)
        # - Webhook sẽ xử lý và lưu dữ liệu
        if all_data:
            try:
                json_payload = _payload_to_json_bytes(all_data.values())
                logger.info(f"Đang gửi {len(all_data)} mục tới webhook: {WEBHOOK_URL}")
                await asyncio.to_thread(_post_json, WEBHOOK_URL, json_payload)
                logger.info("✓ Đã gửi dữ liệu thành công!")
            except Exception as e:
                logger.error(f"❌ Lỗi khi gửi webhook: {e}")
        else:
            logger.warning("⚠️ Không có dữ liệu để gửi.")
        
        # Detach automation (không đóng browser)
        # Browser sẽ được giữ mở để có thể tiếp tục sử dụng hoặc debug
        await automation.detach()
        
        return {
            "success": True,
            "count": len(all_data),
            "message": f"Đã crawl xong {len(all_data)} sản phẩm từ {search_input.pages} trang."
        }
        
    except Exception as e:
        logger.exception(f"❌ Lỗi trong quá trình scrape: {e}")
        if automation:
            try:
                await automation.detach()
            except:
                pass
        return {
            "success": False,
            "error": str(e)
        }


@api_router.post("/etsy/scrape", response_model=EtsyScrapeResponse)
async def scrape_etsy(search_input: SearchInput) -> EtsyScrapeResponse:
    """
    Crawl Etsy qua CDP Connection.
    
    Yêu cầu Chrome đã chạy với --remote-debugging-port=9223.
    Xem docs/ETSY_SCRAPING_API.md để biết chi tiết.
    """
    logger.info(f"Nhận yêu cầu scrape Etsy: keyword='{search_input.keyword}', pages={search_input.pages}")

    try:
        result = await scrape_etsy_via_cdp(
            keyword=search_input.keyword, pages=search_input.pages
        )

        if result.get("success"):
            return EtsyScrapeResponse(
                success=True,
                message=result.get("message", "Crawl thành công"),
                count=result.get("count", 0),
            )
        else:
            return EtsyScrapeResponse(
                success=False,
                message="Crawl thất bại",
                error=result.get("error"),
            )
    except Exception as e:
        logger.exception(f"Lỗi khi thực hiện scrape Etsy: {e}")
        return EtsyScrapeResponse(
            success=False, message="Lỗi server khi thực hiện scrape", error=str(e)
        )


@api_router.post("/etsy/scrape_hidemyacc", response_model=EtsyScrapeResponse)
async def scrape_etsy_hidemyacc(search_input: HideMyAccSearchInput) -> EtsyScrapeResponse:
    """
    Crawl Etsy với HideMyAcc profile - tự động launch và scrape.
    
    Xem docs/ETSY_SCRAPING_API.md để biết chi tiết request/response format.
    """
    logger.info(f"Nhận yêu cầu scrape Etsy với HideMyAcc: keyword='{search_input.keyword}', pages={search_input.pages}, profile_id={search_input.profile_id}")

    try:
        # Sử dụng hàm mới với profile
        result = await scrape_etsy_with_profile(
            keyword=search_input.keyword,
            pages=search_input.pages,
            profile_id=search_input.profile_id,  # Bắt buộc phải có
            use_command_line_config=True,  # Sử dụng cấu hình từ command line
            proxy_server=search_input.proxy_server,
            proxy_username=search_input.proxy_username,
            proxy_password=search_input.proxy_password
        )

        if result.get("success"):
            return EtsyScrapeResponse(
                success=True,
                message=result.get("message", "Crawl thành công"),
                count=result.get("count", 0),
            )
        else:
            return EtsyScrapeResponse(
                success=False,
                message="Crawl thất bại",
                error=result.get("error"),
            )
    except Exception as e:
        logger.exception(f"Lỗi khi thực hiện scrape Etsy với HideMyAcc: {e}")
        return EtsyScrapeResponse(
            success=False, message="Lỗi server khi thực hiện scrape", error=str(e)
        )


# Include API router vào app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    # Dùng cấu hình cố định để tránh phụ thuộc environment
    uvicorn.run(app, host=CONFIG_API_HOST, port=CONFIG_API_PORT)

