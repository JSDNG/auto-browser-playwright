"""
Core business logic for CDP-based automation.
Currently only exposes PlaywrightAutomation used by api_server/cdp_connection.
"""

from src.core.automation import PlaywrightAutomation

__all__ = [
    "PlaywrightAutomation",
]