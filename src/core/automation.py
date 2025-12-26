from src.models.input import ViewportConfig, AutomationInput
from src.core.actions import ActionExecutor
from src.core.extractor import DataExtractor
from playwright.async_api import async_playwright
import asyncio
import platform
from typing import Dict, Any, Optional

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

    async def connect_over_cdp(self, cdp_endpoint: str = "http://localhost:9224"):
        """
        Kết nối với Chrome instance đang chạy qua CDP (Chrome DevTools Protocol)
        
        Method này kết nối với browser đã được khởi động sẵn thông qua CDP endpoint.
        Browser phải được launch với --remote-debugging-port để mở CDP port.
        
        Args:
            cdp_endpoint: CDP endpoint URL (default: http://localhost:9224)
                          Format: http://localhost:PORT hoặc ws://localhost:PORT
                          Playwright tự động convert http:// sang ws://
        
        Yêu cầu:
            Chrome phải được khởi động với flag: --remote-debugging-port=PORT
            Ví dụ: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port=9224
        
        Lưu ý:
            - Method này điều khiển browser QUA CDP
            - Dùng khi browser đã được launch sẵn từ bên ngoài
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

    async def run_automation(self, config: AutomationInput, logger=None) -> Dict[str, Any]:
        """
        Run complete automation flow based on configuration.
        
        Args:
            config: AutomationInput configuration
            logger: Optional logger instance
            
        Returns:
            dict with keys: success, url, extracted_data, action_data
        """
        log_func = logger.info if logger else print
        log_error = logger.error if logger else print
        
        try:
            # Initialize action executor and data extractor
            action_executor = ActionExecutor(self.page)
            data_extractor = DataExtractor(self.page)
            
            # Navigate to URL
            log_func(f"Navigating to: {config.url}")
            await self.navigate(config.url)
            
            # Wait for initial selector if specified
            if config.wait_for_selector:
                log_func(f"Waiting for selector: {config.wait_for_selector}")
                await self.wait_for_selector(config.wait_for_selector, timeout=config.timeout)
            
            # Execute actions
            if config.actions:
                log_func(f"Executing {len(config.actions)} actions...")
                for i, action in enumerate(config.actions, 1):
                    try:
                        log_func(f"  [{i}/{len(config.actions)}] Executing {action.type} on {action.selector or 'N/A'}")
                        await action_executor.execute(action)
                    except Exception as e:
                        log_error(f"  Error executing action {i}: {e}")
                        # Continue with next action instead of failing completely
                        continue
            
            # Extract data
            extracted_data = {}
            if config.extract:
                log_func(f"Extracting {len(config.extract)} data points...")
                for extract_config in config.extract:
                    try:
                        log_func(f"  Extracting: {extract_config.name}")
                        result = await data_extractor.extract(extract_config)
                        extracted_data[extract_config.name] = result
                    except Exception as e:
                        log_error(f"  Error extracting {extract_config.name}: {e}")
                        extracted_data[extract_config.name] = None
            
            # Get action extracted data (from get_text, get_attribute, etc.)
            action_data = action_executor.get_extracted_data()
            
            return {
                "success": True,
                "url": self.page.url,
                "extracted_data": extracted_data,
                "action_data": action_data
            }
            
        except Exception as e:
            log_error(f"Automation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": self.page.url if self.page else None,
                "extracted_data": {},
                "action_data": {}
            }