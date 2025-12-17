from src.models.input import ViewportConfig
from playwright.async_api import async_playwright
import asyncio
import platform

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class PlaywrightAutomation:
    def __init__(self, headless: bool = False, timeout: int = 30000, viewport: ViewportConfig = None):
        self.headless = headless
        self.timeout = timeout
        self.viewport = viewport or ViewportConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def launch(self):
        """Launch browser using system Chrome"""
        self.playwright = await async_playwright().start()
        # Use system Chrome instead of Playwright's browser
        self.browser = await self.playwright.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
            "--disable-blink-features=AutomationControlled", # TẮT CỜ ROBOT (Quan trọng nhất)
            "--no-sandbox",
            "--disable-infobars"
        ])
        
        self.context = await self.browser.new_context(
            viewport={'width': self.viewport.width, 'height': self.viewport.height}
        )
        self.page = await self.context.new_page()

    async def launch_with_profile(self, user_data_dir: str, executable_path: str = None, channel: str = None, 
                                   proxy: dict = None, extra_args: list = None, require_executable: bool = False):
        """
        Launch browser với user-data-dir (profile) cụ thể
        
        Args:
            user_data_dir: Đường dẫn đến user data directory của profile
            executable_path: Đường dẫn đến browser executable (ví dụ: Marco browser từ HideMyAcc)
            channel: Browser channel (ví dụ: "chrome") - chỉ dùng nếu không có executable_path
            proxy: Proxy settings dict với keys: server, username (optional), password (optional)
                   Ví dụ: {"server": "http://proxy:port", "username": "user", "password": "pass"}
            extra_args: Danh sách args bổ sung (sẽ được thêm vào args mặc định)
        
        Lưu ý:
            - Sử dụng launch_persistent_context để load profile trực tiếp
            - Profile sẽ được load với tất cả cookies, extensions, settings
            - Không thể launch nhiều instance cùng lúc với cùng user_data_dir
            - Ưu tiên executable_path hơn channel
        """
        self.playwright = await async_playwright().start()
        
        # Chuẩn bị args
        # Luôn thêm các args quan trọng cho automation
        essential_args = [
            "--disable-blink-features=AutomationControlled",  # TẮT CỜ ROBOT (quan trọng nhất)
            "--no-sandbox",
            "--disable-infobars",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        
        if extra_args:
            # Nếu có extra_args, sử dụng chúng (từ command line)
            # Vẫn giữ essential_args để đảm bảo automation hoạt động
            browser_args = essential_args + extra_args
        else:
            # Args mặc định nếu không có extra_args
            browser_args = essential_args + [
                "--lang=en-US",
                "--disable-encryption",
                "--restore-last-session",
                "--disable-features=ExtensionsToolbarMenu,ChromeLabs,ReadLater,TriggerNetworkDataMigration,ChromeWhatsNewUI,ViewportHeightClientHintHeader",
                "--flag-switches-begin",
                "--flag-switches-end",
                "--origin-trial-disabled-features=CanvasTextNg|WebAssemblyCustomDescriptors",
            ]
        
        # Launch với persistent context (user-data-dir)
        # launch_persistent_context trả về BrowserContext trực tiếp, không phải Browser
        launch_options = {
            "user_data_dir": user_data_dir,
            "headless": self.headless,
            "viewport": {'width': self.viewport.width, 'height': self.viewport.height},
            "args": browser_args,
        }
        
        # Thêm proxy nếu có
        if proxy:
            # Playwright proxy cần format: {server, username?, password?}
            proxy_config = {
                "server": proxy["server"]
            }
            # Thêm username/password nếu có (đã được decode từ base64 trong test script)
            if "username" in proxy and proxy["username"]:
                proxy_config["username"] = proxy["username"]
            if "password" in proxy and proxy["password"]:
                proxy_config["password"] = proxy["password"]
            launch_options["proxy"] = proxy_config
            print(f"[DEBUG] Proxy config: server={proxy_config['server']}, has_username={bool(proxy_config.get('username'))}, has_password={bool(proxy_config.get('password'))}")
        
        # Ưu tiên executable_path (ví dụ: Marco browser từ HideMyAcc)
        if executable_path:
            import os
            # Kiểm tra file có tồn tại không
            if os.path.exists(executable_path):
                launch_options["executable_path"] = executable_path
            else:
                print(f"⚠️  Warning: Executable path không tồn tại: {executable_path}")
                print("   Sẽ sử dụng browser mặc định")
        elif channel:
            launch_options["channel"] = channel
        # Nếu không có cả hai, Playwright sẽ dùng browser mặc định
        # Nếu yêu cầu bắt buộc có executable_path mà lại không set được, raise để tránh fallback Chromium mặc định
        if require_executable and "executable_path" not in launch_options:
            raise RuntimeError("Executable path bắt buộc nhưng không tìm thấy. Kiểm tra lại Marco/Chrome path.")
        
        # Debug: In ra một số thông tin quan trọng
        print()
        print("[DEBUG] Launch configuration:")
        if executable_path and "executable_path" in launch_options:
            print(f"  ✓ Executable: {launch_options['executable_path']}")
        else:
            print(f"  ⚠️  Executable: Not set (using default)")
        if proxy:
            print(f"  ✓ Proxy: {proxy['server']}")
        else:
            print(f"  ⚠️  Proxy: Not set")
        print(f"  ✓ User data dir: {user_data_dir}")
        print(f"  ✓ Browser args: {len(browser_args)} arguments")
        print()
        
        self.context = await self.playwright.chromium.launch_persistent_context(**launch_options)
        
        # Verify executable được sử dụng
        browser_type = self.context.browser
        if browser_type:
            print(f"[DEBUG] Actual browser: {browser_type.browser_type.name}")
            if hasattr(browser_type, 'browser_type') and hasattr(browser_type.browser_type, 'executable_path'):
                print(f"[DEBUG] Actual executable: {browser_type.browser_type.executable_path}")
        print()
        
        # Lấy page đầu tiên hoặc tạo mới
        pages = self.context.pages
        if pages:
            self.page = pages[0]
        else:
            self.page = await self.context.new_page()
        
        # Với launch_persistent_context, browser object là None
        # Context chứa browser instance bên trong
        self.browser = None  # Không có browser object riêng với persistent context

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