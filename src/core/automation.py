from src.models.input import ViewportConfig
from playwright.async_api import async_playwright
import asyncio
import platform

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class PlaywrightAutomation:
    def __init__(self, headless: bool = True, timeout: int = 30000, viewport: ViewportConfig = None):
        self.headless = headless
        self.timeout = timeout
        self.viewport = viewport or ViewportConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def launch(self):
        """Launch browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ] if self.headless else [
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
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