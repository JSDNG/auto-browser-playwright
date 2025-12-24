"""
FastAPI server để gen video với Grok và điều khiển browser automation.

Cung cấp endpoints:
- /api/v1/grok/launch: Launch Chrome, navigate đến Grok Imagine và nhập prompt để gen video

Xem docs/CDP_CONNECTION.md để biết chi tiết cách sử dụng.
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
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
import logging

from src.models import GrokInput
from src.app.cdp_connection import grok_gen_video_direct


# =========================
# CẤU HÌNH CỐ ĐỊNH (INLINE)
# =========================

# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5674

# CDP port cho Chrome
CONFIG_CDP_PORT = 9224


# Setup logging (đơn giản, log ra stdout/terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Grok Video Generation API",
    description="API để điều khiển Chrome và gen video với Grok qua Playwright",
    version="1.0.0",
)

# Create API router với prefix /api/v1
api_router = APIRouter(prefix="/api/v1")


class GrokLaunchResponse(BaseModel):
    """Response cho việc gen video với Grok"""
    success: bool
    message: str
    url: Optional[str] = None
    error: Optional[str] = None


@api_router.post("/grok/launch", response_model=GrokLaunchResponse)
async def launch_grok(grok_input: GrokInput) -> GrokLaunchResponse:
    """
    Launch Chrome, navigate đến Grok Imagine (https://grok.com/imagine) và nhập prompt để gen video.
    
    Sử dụng Chrome trực tiếp. Gọi hàm từ cdp_connection.py để xử lý logic.
    """
    logger.info(f"Nhận yêu cầu gen video với Grok: prompt='{grok_input.text[:50]}...'")
    
    try:
        # Gọi hàm từ cdp_connection.py để xử lý logic
        result = await grok_gen_video_direct(text=grok_input.text)
        
        if result.get("success"):
            return GrokLaunchResponse(
                success=True,
                message=result.get("message", "Đã gen video thành công"),
                url=result.get("url")
            )
        else:
            return GrokLaunchResponse(
                success=False,
                message="Lỗi khi gen video với Grok",
                error=result.get("error")
            )
        
    except Exception as e:
        logger.exception(f"Lỗi khi launch Grok: {e}")
        return GrokLaunchResponse(
            success=False,
            message="Lỗi server khi thực hiện gen video",
            error=str(e)
        )


# Include API router vào app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    # Dùng cấu hình cố định để tránh phụ thuộc environment
    uvicorn.run(app, host=CONFIG_API_HOST, port=CONFIG_API_PORT)

