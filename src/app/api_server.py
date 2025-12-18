"""
FastAPI server đơn giản để làm việc với HideMyAcc

Mục đích:
- ✅ Tự động tìm HideMyAcc profile
- ✅ Tự động khởi động Chrome (Marco/Chrome) với profile đó + CDP
- ✅ Tự động kết nối Playwright qua CDP

API này KHÔNG cần body đầu vào – chỉ cần gọi endpoint là tự xử lý.

Cấu hình nhanh (chỉnh trực tiếp trong file cho dễ deploy, không cần .env):
- CONFIG_API_HOST: host mà Uvicorn sẽ bind (mặc định: 0.0.0.0)
- CONFIG_API_PORT: port local của API (mặc định: 5674)
- CONFIG_CDP_PORT: port CDP cho Chrome/Marco (mặc định: 9223)
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
from src.models import SearchInput
from src.app.cdp_connection import scrape_etsy_via_cdp


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


@api_router.post("/hidemyacc/connect", response_model=HideMyAccConnectionResponse)
async def connect_hidemyacc_profile() -> HideMyAccConnectionResponse:
    # ... existing implementation ...
    pass


class EtsyScrapeResponse(BaseModel):
    """Response cho việc crawl Etsy"""

    success: bool
    message: str
    count: Optional[int] = 0
    error: Optional[str] = None


@api_router.post("/etsy/scrape", response_model=EtsyScrapeResponse)
async def scrape_etsy(search_input: SearchInput) -> EtsyScrapeResponse:
    """
    Crawl dữ liệu từ Etsy theo keyword và số trang.
    Yêu cầu Chrome (hoặc HideMyAcc profile) đã được khởi động với CDP port 9223.
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


# Include API router vào app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    # Dùng cấu hình cố định để tránh phụ thuộc environment
    uvicorn.run(app, host=CONFIG_API_HOST, port=CONFIG_API_PORT)

