"""
FastAPI server đơn giản để làm việc với Chrome qua CDP

Mục đích:
- ✅ Kết nối tới Chrome đang chạy sẵn qua CDP
- ✅ Cung cấp API nền tảng để thực hiện các tác vụ tự động hoá (ví dụ: check TM trên Grok)

Cấu hình nhanh (chỉnh trực tiếp trong file cho dễ deploy, không cần .env):
- CONFIG_API_HOST: host mà Uvicorn sẽ bind (mặc định: 0.0.0.0)
- CONFIG_API_PORT: port local của API (mặc định: 5675)
- CONFIG_CDP_PORT: port CDP cho Chrome (mặc định: 9224)
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

from src.core.automation import PlaywrightAutomation


# =========================
# CẤU HÌNH CỐ ĐỊNH (INLINE)
# =========================

# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5675

# CDP port cho Chrome
CONFIG_CDP_PORT = 9224


# Setup logging (đơn giản, log ra stdout/terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app (có thể dùng cho nhiều luồng automation khác nhau, ví dụ: check TM trên Grok)
app = FastAPI(
    title="CDP Automation API",
    description="API đơn giản để kết nối Chrome qua CDP và thực hiện các tác vụ automation (ví dụ: check TM trên Grok).",
    version="1.0.0",
)

# Create API router với prefix /api/v1
api_router = APIRouter(prefix="/api/v1")


# =========================
# MODELS
# =========================


class OpenUrlRequest(BaseModel):
    """Body request để mở một URL cụ thể qua CDP."""

    url: str


class OpenUrlResponse(BaseModel):
    """Kết quả khi mở URL qua CDP."""

    success: bool
    message: str
    title: Optional[str] = None
    error: Optional[str] = None


#
# =========================
# HELPERS
# =========================


async def _open_url_via_cdp(target_url: str) -> OpenUrlResponse:
    """Helper: mở URL qua CDP và trả về OpenUrlResponse."""
    target_url = target_url.strip()
    if not target_url:
        raise HTTPException(status_code=400, detail="URL không được để trống")

    logger.info(f"[CDP] Yêu cầu mở URL: {target_url}")

    automation = PlaywrightAutomation()
    cdp_endpoint = f"http://localhost:{CONFIG_CDP_PORT}"

    try:
        # Kết nối tới Chrome đang chạy sẵn
        logger.info(f"[CDP] Kết nối tới Chrome qua CDP: {cdp_endpoint}")
        await automation.connect_over_cdp(cdp_endpoint)

        # Điều hướng tới URL
        await automation.navigate(target_url)
        title = await automation.page.title()
        logger.info(f"[CDP] Đã mở URL, title: {title}")

        # Không đóng Chrome – chỉ detach Playwright
        await automation.detach()

        return OpenUrlResponse(
            success=True,
            message="Đã mở URL trong Chrome qua CDP thành công.",
            title=title,
        )

    except Exception as e:
        logger.exception(f"[CDP] Lỗi khi mở URL qua CDP: {e}")
        # Cố gắng detach nếu có thể
        try:
            await automation.detach()
        except Exception:
            pass

        return OpenUrlResponse(
            success=False,
            message="Không thể mở URL trong Chrome qua CDP.",
            error=str(e),
        )


# =========================
# ROUTES
# =========================


@api_router.post("/cdp/auto-check-tm", response_model=OpenUrlResponse)
async def auto_check_tm_api(payload: OpenUrlRequest) -> OpenUrlResponse:
    """
    API chuyên dụng cho luồng **auto-check TM**:

    - Nhận URL (ví dụ: URL Grok với query TM cụ thể)
    - Mở trong Chrome (đang chạy với CDP)
    - Trả lại thông tin cơ bản (title, trạng thái success) để phía client/worker xử lý tiếp.

    Lưu ý: API này KHÔNG tự đọc kết quả TM, mà chỉ đảm bảo mở đúng URL trong session Chrome.
    """
    return await _open_url_via_cdp(payload.url)


# Include API router vào app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    # Dùng cấu hình cố định để tránh phụ thuộc environment
    uvicorn.run(app, host=CONFIG_API_HOST, port=CONFIG_API_PORT)

