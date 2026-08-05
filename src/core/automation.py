from src.models.input import ViewportConfig
from playwright.async_api import async_playwright

class PlaywrightAutomation:
    def __init__(self, headless: bool = False, timeout: int = 30000, viewport: ViewportConfig = None):
        self.headless = headless
        self.timeout = timeout
        self.viewport = viewport or ViewportConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def connect_over_cdp(self, cdp_endpoint: str = "http://localhost:9222"):
        """
        Connect to an existing Chrome instance via CDP (Chrome DevTools Protocol)
        
        Args:
            cdp_endpoint: CDP endpoint URL (default: http://localhost:9222)
                          Format: http://localhost:PORT hoặc ws://localhost:PORT
        
        Yêu cầu:
            Chrome phải được khởi động với flag: --remote-debugging-port=9222
            Ví dụ: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9222
        """
        self.playwright = await async_playwright().start()
        
        # Connect to existing Chrome via CDP
        # Playwright tự động detect nếu là http:// thì sẽ convert sang ws://
        self.browser = await self.playwright.chromium.connect_over_cdp(cdp_endpoint)
        
        # Lấy context hiện có hoặc tạo mới
        contexts = self.browser.contexts
        if contexts:
            # Sử dụng context đầu tiên đã có sẵn
            self.context = contexts[0]
            pages = self.context.pages
            if pages:
                # Sử dụng page đầu tiên đã có sẵn
                self.page = pages[0]
            else:
                # Tạo page mới trong context hiện có
                self.page = await self.context.new_page()
        else:
            # Tạo context và page mới
            self.context = await self.browser.new_context(
                viewport={'width': self.viewport.width, 'height': self.viewport.height}
            )
            self.page = await self.context.new_page()

    async def navigate(self, url: str):
        """Navigate to URL"""
        await self.page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")

    async def wait_for_selector(self, selector: str, timeout: int = None):
        """Wait for selector"""
        await self.page.wait_for_selector(selector, timeout=timeout or self.timeout)

    async def close(self):
        """Close browser"""
        if self.page:
            await self.page.close()
        if self.context:
            # Với persistent context, close context sẽ đóng browser
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def detach(self):
        """Detach without closing browser"""
        # Reset references without closing
        self.page = None
        self.context = None
        self.browser = None
        if self.playwright:
            await self.playwright.stop()
        self.playwright = None