"""
Config cho CDP Tracking API, đọc từ file .env (nếu có).

Nếu không có .env hoặc thiếu biến nào, sẽ dùng giá trị mặc định tương ứng
bên dưới. Xem `.env-example` để biết danh sách đầy đủ các biến hỗ trợ.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _get_list(name: str, default: list) -> list:
    value = os.getenv(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


# Host & port cho API (Uvicorn)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = _get_int("API_PORT", 5673)

# CDP endpoint cho Chrome (Chrome phải chạy với --remote-debugging-port=9222)
CDP_ENDPOINT = os.getenv("CDP_ENDPOINT", "http://localhost:9222")

# Thời gian chờ sau khi vào trang tracking (giây)
WAIT_TIME_SECONDS = _get_int("WAIT_TIME_SECONDS", 2)

# Các cụm text cần có trong body để coi là "delivered"
REQUIRED_PHRASES = _get_list(
    "REQUIRED_PHRASES",
    ["Your item was delivered", "Latest Update", "Delivered"],
)
