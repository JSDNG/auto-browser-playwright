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
- CONFIG_CDP_PORT: port CDP cho Chrome/Marco (mặc định: 9222)
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


# =========================
# CẤU HÌNH CỐ ĐỊNH (INLINE)
# =========================

# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5674

# CDP port cho Chrome/Marco (HideMyAcc)
CONFIG_CDP_PORT = 9222


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
    """
    Tự động:
    - Tìm HideMyAcc profiles (qua `HideMyAccManager`)
    - Chọn profile đầu tiên tìm được
    - Nếu CDP chưa chạy thì tự khởi động Chrome/Marco với profile đó
    - Kết nối Playwright với Chrome/Marco qua CDP

    ✅ KHÔNG cần body đầu vào.
    """
    manager = HideMyAccManager()
    profiles = manager.find_profiles()

    if not profiles:
        logger.error("Không tìm thấy HideMyAcc profiles nào trên máy")
        raise HTTPException(
            status_code=500,
            detail="Không tìm thấy HideMyAcc profiles. Hãy kiểm tra lại cài đặt HideMyAcc.",
        )

    # Đơn giản: lấy profile đầu tiên
    profile = profiles[0]
    profile_id = profile.get("id") or profile.get("name")
    profile_name = profile.get("name")

    logger.info(f"Đang sử dụng HideMyAcc profile: id={profile_id}, name={profile_name}")

    # Đảm bảo CDP đang chạy
    if manager.check_cdp_running(CONFIG_CDP_PORT):
        logger.info(f"CDP đã chạy sẵn tại port {CONFIG_CDP_PORT}")
    else:
        logger.info(f"CDP chưa chạy. Đang khởi động Chrome/Marco với profile {profile_id}...")
        started = manager.launch_chrome_with_profile(profile_id, CONFIG_CDP_PORT)
        if not started:
            logger.error("Không thể khởi động Chrome/Marco với HideMyAcc profile")
            raise HTTPException(
                status_code=500,
                detail="Không thể khởi động Chrome/Marco với HideMyAcc profile. Vui lòng kiểm tra cài đặt HideMyAcc.",
            )

    # Kết nối Playwright qua CDP
    automation = PlaywrightAutomation()
    cdp_endpoint = f"http://localhost:{CONFIG_CDP_PORT}"

    try:
        logger.info(f"Đang kết nối Playwright với Chrome qua CDP tại {cdp_endpoint}...")
        await automation.connect_over_cdp(cdp_endpoint)
        logger.info("Đã kết nối Playwright thành công với HideMyAcc profile.")

        # Ở đây ta chỉ test kết nối, không làm gì thêm -> detach để không đóng browser
        await automation.detach()
        logger.info("Đã detach khỏi Playwright, Chrome/Marco vẫn tiếp tục chạy.")

        return HideMyAccConnectionResponse(
            success=True,
            message="Kết nối HideMyAcc profile + Chrome/Marco + Playwright thành công.",
            profile_id=profile_id,
            profile_name=profile_name,
            cdp_port=CONFIG_CDP_PORT,
        )
    except Exception as e:
        logger.exception(f"Lỗi khi kết nối Playwright qua CDP: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi kết nối Playwright qua CDP: {e}",
        )


# Include API router vào app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    # Dùng cấu hình cố định để tránh phụ thuộc environment
    uvicorn.run(app, host=CONFIG_API_HOST, port=CONFIG_API_PORT)

