"""
FastAPI server để gọi CDP connection

LƯU Ý CONFIG (chỉnh trực tiếp trong file này và cdp_connection.py cho dễ deploy Windows):
- API_HOST: ip/host mà Uvicorn sẽ bind (mặc định: 0.0.0.0 để reverse proxy truy cập được)
- API_PORT: port local để service / reverse proxy trỏ vào (mặc định: 5673)
- CDP_ENDPOINT: endpoint CDP của Chrome (mặc định: http://localhost:9222)
- WAIT_TIME_SECONDS: thời gian chờ sau khi load trang tracking (mặc định: 2s)

Nếu bạn muốn đổi port / CDP endpoint cho môi trường khác, chỉ cần sửa các biến
CONFIG_* bên dưới, không cần .env cho đỡ rối.
"""
# CRITICAL: Set Windows event loop policy FIRST, before any imports
# This must be done before uvicorn or Playwright create any event loops
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

from typing import Optional, List, Union
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
import re
import logging
from src.app.cdp_connection import connect_to_chrome_via_cdp


# =========================
# CẤU HÌNH CỐ ĐỊNH (INLINE)
# =========================

# Host & port cho API (Uvicorn)
CONFIG_API_HOST = "0.0.0.0"
CONFIG_API_PORT = 5673

# CDP endpoint cho Chrome (Chrome phải chạy với --remote-debugging-port=9222)
CONFIG_CDP_ENDPOINT = "http://localhost:9222"

# Thời gian chờ sau khi vào trang tracking (giây)
CONFIG_WAIT_TIME_SECONDS = 2


# Setup logging (đơn giản, log ra stdout/terminal)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CDP Connection API",
    description="API để kết nối với Chrome qua CDP và kiểm tra trạng thái delivered",
    version="1.0.0"
)

# Create API router với prefix /api/v1
api_router = APIRouter(prefix="/api/v1")


class ShipmentItem(BaseModel):
    """Model cho một shipment item"""
    shipment_id: Union[int, str] = Field(..., description="ID của shipment (có thể là số hoặc string)")
    tracking_link: str = Field(..., description="Link tracking của shipment")


class ShipmentTrackingResponse(BaseModel):
    """Response model cho một shipment tracking"""
    shipment_id: Union[int, str]  # Giữ nguyên kiểu dữ liệu như input (số hoặc string)
    delivered: bool
    delivered_at: Optional[str] = None  # ISO 8601 format: "2025-12-13T05:01:00Z"


@api_router.post("/cdp/auto-check-tracking", response_model=List[ShipmentTrackingResponse])
async def check_delivery_status(shipments: List[ShipmentItem]):
    """
    Kết nối với Chrome qua CDP và kiểm tra trạng thái delivered cho nhiều shipments
    
    Request body: Mảng các object với shipment_id và tracking_link
    [
        {
            "shipment_id": "123",
            "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858307"
        },
        {
            "shipment_id": "456",
            "tracking_link": "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1=9434650105796013858308"
        }
    ]
    
    Response: Mảng các object với shipment_id, delivered, và delivered_at
    [
        {
            "shipment_id": "123",
            "delivered": True,
            "delivered_at": "2025-12-13T05:01:00Z"
        },
        {
            "shipment_id": "456",
            "delivered": False,
            "delivered_at": None
        }
    ]
    
    Yêu cầu:
    - Chrome phải được khởi động với --remote-debugging-port=9222 (hoặc port khác nếu chỉ định)
    
    Ví dụ khởi động Chrome:
    - macOS: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222
    - Linux: google-chrome --remote-debugging-port=9222
    - Windows: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome-debug"
    """
    if not shipments:
        raise HTTPException(
            status_code=400,
            detail="Shipments list cannot be empty"
        )
    
    # Validate input
    for idx, shipment in enumerate(shipments):
        # Validate shipment_id: có thể là số hoặc string, nhưng không được rỗng
        if shipment.shipment_id is None:
            raise HTTPException(
                status_code=400,
                detail=f"shipment_id cannot be None at index {idx}"
            )
        if isinstance(shipment.shipment_id, str) and not shipment.shipment_id.strip():
            raise HTTPException(
                status_code=400,
                detail=f"shipment_id cannot be empty string at index {idx}"
            )
        if not shipment.tracking_link or not shipment.tracking_link.strip():
            raise HTTPException(
                status_code=400,
                detail=f"tracking_link cannot be empty at index {idx}"
            )
    
    try:
        logger.info(f"Received batch request with {len(shipments)} shipments")
        
        # Dùng config cố định từ trên
        cdp_endpoint = CONFIG_CDP_ENDPOINT
        wait_time = CONFIG_WAIT_TIME_SECONDS
        results = []
        
        # Xử lý từng shipment tuần tự (giữ nguyên thứ tự)
        for idx, shipment in enumerate(shipments, 1):
            try:
                logger.info(f"[{idx}/{len(shipments)}] Processing shipment_id={shipment.shipment_id}")
                
                # Gọi hàm connect_to_chrome_via_cdp cho từng tracking link
                result = await connect_to_chrome_via_cdp(
                    url=shipment.tracking_link,
                    cdp_endpoint=cdp_endpoint,
                    wait_time=wait_time,
                    required_phrases=None  # Sử dụng mặc định
                )
                
                is_delivered = result.get("is_delivered", False)
                delivered_at = None  # Mặc định là null
                
                # Nếu delivered, lấy date từ DOM elements (không format, lấy raw data)
                if is_delivered and result.get("success", False):
                    # Lấy date từ .delivered-status .tb-date (tb-date nằm trong delivered-status)
                    delivered_at = result.get("delivered_date")  # Date từ .delivered-status .tb-date
                    
                    # Loại bỏ \n và \t nếu có trong delivered_at
                    if delivered_at:
                        delivered_at = delivered_at.replace("\n", " ").replace("\t", " ").strip()
                        # Loại bỏ khoảng trắng thừa (nhiều khoảng trắng liên tiếp)
                        delivered_at = " ".join(delivered_at.split())
                
                # Tạo ShipmentTrackingResponse
                shipment_result = ShipmentTrackingResponse(
                    shipment_id=shipment.shipment_id,
                    delivered=is_delivered,
                    delivered_at=delivered_at
                )
                
                results.append(shipment_result)
                    
                logger.info(f"[{idx}/{len(shipments)}] Completed shipment_id={shipment.shipment_id}, delivered={is_delivered}, delivered_at={delivered_at}")
                
            except Exception as e:
                logger.error(f"Error processing shipment_id={shipment.shipment_id}: {e}", exc_info=True)
                # Trả về kết quả với delivered=False nếu có lỗi (giữ nguyên thứ tự)
                results.append(ShipmentTrackingResponse(
                    shipment_id=shipment.shipment_id,
                    delivered=False,
                    delivered_at=None
                ))
        
        logger.info(f"Batch request completed: total={len(shipments)}, processed={len(results)}, delivered={sum(1 for r in results if r.delivered)}")
        
        # Trả về kết quả tổng hợp một lần (giữ nguyên thứ tự như input)
        return results
        
    except Exception as e:
        logger.error(f"Error processing batch request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Include API router vào app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    # Dùng cấu hình cố định để tránh phụ thuộc environment
    uvicorn.run(app, host=CONFIG_API_HOST, port=CONFIG_API_PORT)
