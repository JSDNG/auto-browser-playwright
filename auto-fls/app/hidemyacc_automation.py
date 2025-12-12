"""
HideMyAcc + Playwright CDP Automation
Kết hợp HideMyAcc API với Playwright qua Chrome DevTools Protocol
"""

import asyncio
import json
import time
import requests
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page


class HideMyAccPlaywright:
    """Wrapper class để tự động hóa HideMyAcc + Playwright"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.profile_id: Optional[str] = None
        # HideMyAcc API base URL (default port 2268)
        self.base_url = base_url or "http://127.0.0.1:2268"
        
    async def start_profile(self, profile_id: str, options: Optional[Dict] = None) -> Browser:
        """
        Khởi động profile HideMyAcc và kết nối Playwright qua CDP
        
        Args:
            profile_id: ID của profile HideMyAcc
            options: Các tùy chọn bổ sung (automation, debuggingPort, etc.)
        
        Returns:
            Browser object của Playwright
        """
        self.profile_id = profile_id
        
        # 1. Start profile qua HideMyAcc API
        print(f"🚀 Đang khởi động profile {profile_id}...")
        user_data = await self._start_hidemyacc_profile(profile_id, options)
        
        # 2. Lấy CDP endpoint từ wsUrl
        ws_url = user_data.get("wsUrl")
        if not ws_url:
            raise Exception("Không tìm thấy wsUrl trong response từ HideMyAcc API")
        
        print(f"🔗 WebSocket URL: {ws_url}")
        
        # 3. Đợi CDP sẵn sàng
        cdp_url = self._get_cdp_url(user_data)
        print(f"⏳ Đợi CDP sẵn sàng tại {cdp_url}...")
        await self._wait_for_cdp(cdp_url)
        
        # 4. Kết nối Playwright qua CDP
        # Playwright connect_over_cdp cần http:// URL (sẽ tự chuyển sang ws://)
        print(f"🎭 Kết nối Playwright qua CDP...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(cdp_url)
        
        print(f"✅ Kết nối thành công!")
        return self.browser
    
    async def _start_hidemyacc_profile(self, profile_id: str, options: Optional[Dict] = None) -> Dict:
        """Gọi API HideMyAcc để start profile"""
        
        # Cách 1: Nếu bạn có SDK Python của HideMyAcc
        try:
            from hidemyacc import Hidemyacc  # type: ignore
            hidemyacc = Hidemyacc()
            user_data = await hidemyacc.start(profile_id)
            return user_data
        except ImportError:
            pass
        
        # Cách 2: Gọi HTTP API trực tiếp (fallback)
        # HideMyAcc API endpoint: POST /profiles/start/{profile_id}
        url = f"{self.base_url}/profiles/start/{profile_id}"
        
        # Payload structure theo HideMyAcc API
        payload = {}
        if options and "open_tabs" in options:
            payload["open_tabs"] = options["open_tabs"]
        elif options:
            payload = options
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # HideMyAcc API trả về: {"code": 1, "data": {...}}
            # Nếu có data, trả về data, nếu không trả về toàn bộ response
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"Không thể start profile qua API: {e}")
    
    def _get_cdp_url(self, user_data: Dict) -> str:
        """Trích xuất CDP URL từ response của HideMyAcc API"""
        
        # HideMyAcc API trả về wsUrl trong data
        if "wsUrl" in user_data:
            ws_url = user_data["wsUrl"]
            # Chuyển ws:// thành http:// cho CDP endpoint
            if ws_url.startswith("ws://"):
                return ws_url.replace("ws://", "http://").split("/devtools")[0]
            return ws_url
        
        # Thử các field phổ biến khác
        if "cdpUrl" in user_data:
            return user_data["cdpUrl"]
        
        if "debuggerAddress" in user_data:
            return user_data["debuggerAddress"]
        
        if "wsEndpoint" in user_data:
            ws_url = user_data["wsEndpoint"]
            if ws_url.startswith("ws://"):
                return ws_url.replace("ws://", "http://").split("/devtools")[0]
            return ws_url
        
        # Fallback: tự build từ port
        port = user_data.get("port") or user_data.get("debuggingPort") or 9222
        return f"http://127.0.0.1:{port}"
    
    async def _wait_for_cdp(self, cdp_url: str, max_retries: int = 30, timeout: int = 2):
        """Đợi CDP endpoint sẵn sàng"""
        
        # Chuyển ws:// thành http://
        base_url = cdp_url.replace("ws://", "http://").split("/devtools")[0]
        check_url = f"{base_url}/json/version"
        
        for i in range(max_retries):
            try:
                response = requests.get(check_url, timeout=timeout)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    raise Exception(f"CDP không sẵn sàng sau {max_retries}s")
                await asyncio.sleep(1)
        
        return False
    
    async def get_page(self) -> Page:
        """Lấy page đầu tiên hoặc tạo page mới"""
        
        if not self.browser:
            raise Exception("Browser chưa được khởi động. Gọi start_profile() trước.")
        
        contexts = self.browser.contexts
        if not contexts:
            raise Exception("Không tìm thấy browser context")
        
        context = contexts[0]
        pages = context.pages
        
        # Trả về page đầu tiên hoặc tạo mới
        if pages:
            return pages[0]
        else:
            return await context.new_page()
    
    async def close(self):
        """Đóng kết nối Playwright và stop profile"""
        
        if self.browser:
            print("🔌 Đóng kết nối Playwright...")
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
        
        if self.profile_id:
            print(f"🛑 Dừng profile {self.profile_id}...")
            await self._stop_hidemyacc_profile(self.profile_id)
    
    async def _stop_hidemyacc_profile(self, profile_id: str):
        """Dừng profile qua API"""
        
        try:
            from hidemyacc import Hidemyacc  # type: ignore
            hidemyacc = Hidemyacc()
            await hidemyacc.stop(profile_id)
        except ImportError:
            # Fallback: HTTP API
            # HideMyAcc API endpoint: POST /profiles/stop/{profile_id}
            url = f"{self.base_url}/profiles/stop/{profile_id}"
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            try:
                response = requests.post(url, headers=headers, timeout=10)
                response.raise_for_status()
            except Exception as e:
                print(f"⚠️ Không thể stop profile: {e}")


# ==================== CÁCH SỬ DỤNG ====================

async def main():
    """Ví dụ sử dụng HideMyAccPlaywright"""
    
    automation = HideMyAccPlaywright()
    
    try:
        # 1. Khởi động profile
        await automation.start_profile("615d6c4b2a151505fe6ba060")
        
        # 2. Lấy page
        page = await automation.get_page()
        
        # 3. Automation TikTok
        print("\n📱 Đang truy cập TikTok...")
        await page.goto("https://www.tiktok.com", wait_until="networkidle")
        await page.screenshot(path="tiktok.png")
        print("✅ Screenshot TikTok đã lưu!")
        
        # 4. Scrape Etsy
        print("\n🛍️ Đang scrape Etsy...")
        await page.goto("https://www.etsy.com/search?q=trending", wait_until="domcontentloaded")
        
        # Đợi sản phẩm load
        await page.wait_for_selector(".wt-grid__item-xs-6", timeout=10000)
        
        # Lấy thông tin sản phẩm
        products = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('.wt-grid__item-xs-6');
                return Array.from(items).slice(0, 5).map(item => {
                    const title = item.querySelector('h3')?.textContent?.trim();
                    const price = item.querySelector('.currency-value')?.textContent?.trim();
                    const link = item.querySelector('a')?.href;
                    return { title, price, link };
                });
            }
        """)
        
        print("\n📦 Sản phẩm tìm được:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['title']}")
            print(f"   Giá: ${product['price']}")
            print(f"   Link: {product['link']}\n")
        
        # 5. Thêm human-like behavior
        print("🎭 Giả lập hành vi người dùng...")
        await page.mouse.move(100, 100)
        await asyncio.sleep(1)
        await page.mouse.move(300, 400)
        await asyncio.sleep(0.5)
        
        # Scroll trang
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(2)
        
        print("✅ Hoàn thành!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 6. Đóng kết nối
        await automation.close()


# ==================== TEST SCRIPT ====================

async def test_hidemyacc_api():
    """Test để xem HideMyAcc API trả về gì"""
    
    try:
        from hidemyacc import Hidemyacc  # type: ignore
        
        print("🧪 Test HideMyAcc API...")
        hidemyacc = Hidemyacc()
        user = await hidemyacc.start("6898c8f7effa52a76ed48168")
        
        print("\n=== Response từ HideMyAcc API ===")
        print(json.dumps(user, indent=2, ensure_ascii=False))
        print("=================================\n")
        
        # Kiểm tra các field quan trọng
        print("Kiểm tra các field:")
        print(f"  cdpUrl: {user.get('cdpUrl')}")
        print(f"  debuggerAddress: {user.get('debuggerAddress')}")
        print(f"  wsEndpoint: {user.get('wsEndpoint')}")
        print(f"  port: {user.get('port')}")
        print(f"  debuggingPort: {user.get('debuggingPort')}")
        
    except ImportError:
        print("⚠️ Không tìm thấy HideMyAcc SDK. Cần cài đặt hoặc cung cấp đường dẫn.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    # Chọn một trong hai:
    
    # Option 1: Chạy automation chính
    asyncio.run(main())
    
    # Option 2: Test API trước
    # asyncio.run(test_hidemyacc_api())