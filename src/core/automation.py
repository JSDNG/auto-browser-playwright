"""
Playwright automation engine for browser control.
"""

import asyncio
import sys
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class PlaywrightAutomation:
    """Main automation engine using Playwright."""
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        viewport: Optional[Dict[str, int]] = None
    ):
        """Initialize automation engine."""
        self.headless = headless
        self.timeout = timeout
        self.viewport = viewport or {"width": 1280, "height": 720}
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def launch(self) -> None:
        """Launch browser and create context."""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch Chromium browser with stealth mode
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    # Anti-detection arguments
                    "--disable-automation",
                    "--disable-plugins-discovery",
                    "--disable-plugins",
                    "--disable-sync",
                    "--disable-background-networking",
                    "--disable-default-apps",
                    "--disable-component-update",
                    "--no-service-autorun",
                    "--disable-hang-monitor",
                    "--disable-popup-blocking",
                    "--disable-prompt-on-repost",
                    "--disable-client-side-phishing-detection",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-features=ChromeWhatsNewUI,HttpsUpgrades"
                ]
            )
            
            # Create browser context with stealth settings
            self.context = await self.browser.new_context(
                viewport=self.viewport,
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document"
                },
                permissions=["geolocation", "notifications"]
            )
            
            # Set default timeout
            self.context.set_default_timeout(self.timeout)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Add stealth JavaScript to hide automation traces
            await self.page.add_init_script("""
                // Hide webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Hide automation properties
                delete navigator.__proto__.webdriver;
                
                // Override plugins length
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Override chrome runtime
                if (window.chrome) {
                    Object.defineProperty(window.chrome, 'runtime', {
                        get: () => undefined,
                    });
                }
                
                // Add chrome object if missing
                if (!window.chrome) {
                    window.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                }
            """)
            
        except Exception as e:
            await self.close()
            raise Exception(f"Failed to launch browser: {e}")
    
    async def navigate(self, url: str) -> None:
        """Navigate to URL."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        try:
            # Navigate to URL with longer timeout for complex pages
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            if response is None:
                raise Exception(f"Failed to get response from {url}")
            
            if not response.ok:
                print(f"Warning: HTTP {response.status} for {url}", file=sys.stderr)
                # Don't fail on HTTP errors, some pages still work
            
            # Wait for page to be ready with multiple fallback strategies
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                try:
                    await self.page.wait_for_load_state("load", timeout=10000)
                except:
                    # Final fallback - just wait a bit
                    await asyncio.sleep(2)
                    print(f"Warning: Page may not be fully loaded", file=sys.stderr)
            
        except Exception as e:
            raise Exception(f"Failed to navigate to {url}: {e}")
    
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for element to be present."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        try:
            await self.page.wait_for_selector(
                selector,
                timeout=timeout or self.timeout
            )
        except Exception as e:
            raise Exception(f"Element not found: {selector} - {e}")
    
    async def wait_for_timeout(self, timeout: int) -> None:
        """Wait for specified timeout."""
        await asyncio.sleep(timeout / 1000)
    
    async def get_page_title(self) -> str:
        """Get page title."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        return await self.page.title()
    
    async def get_page_url(self) -> str:
        """Get current page URL."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        return self.page.url
    
    async def screenshot(self, path: Optional[str] = None) -> bytes:
        """Take screenshot."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        return await self.page.screenshot(
            path=path,
            full_page=True
        )
    
    async def get_page_content(self) -> str:
        """Get page HTML content."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        return await self.page.content()
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on page."""
        if not self.page:
            raise Exception("Browser not launched. Call launch() first.")
        
        return await self.page.evaluate(script)
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
        except Exception as e:
            # Log error but don't raise to avoid masking original errors
            print(f"Warning: Error during cleanup: {e}")
    
    async def detach(self) -> None:
        """Detach from browser without closing it."""
        try:
            # Just clear references without calling close methods
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
        except Exception as e:
            print(f"Warning: Error during detach: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.launch()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 