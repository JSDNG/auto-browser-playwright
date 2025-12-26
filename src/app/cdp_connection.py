"""
Module automation cho Grok Imagine video generation qua CDP.

CLI Usage:
    python src/app/cdp_connection.py grok <filename>          # Grok via CDP với _grok_imagine_interact
    python src/app/cdp_connection.py cdp [filename]           # Automation via CDP với get_automation_config
"""
import asyncio
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation
from src.models.input import AutomationInput, ActionConfig, ExtractConfig, ViewportConfig


def _check_cdp_available(cdp_endpoint: str = "http://localhost:9224") -> bool:
    """Check if CDP endpoint is available."""
    try:
        response = urlopen(f"{cdp_endpoint}/json", timeout=2)
        return response.getcode() == 200
    except (URLError, Exception):
        return False


def _print_results(result: dict):
    """Helper function để in kết quả automation."""
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"URL: {result.get('url')}")
        if result.get('extracted_data'):
            print("\nExtracted Data:")
            for key, value in result.get('extracted_data', {}).items():
                print(f"  - {key}: {value}")
        if result.get('action_data'):
            print("\nAction Data:")
            for key, value in result.get('action_data', {}).items():
                print(f"  - {key}: {value}")
    else:
        print(f"Error: {result.get('error')}")
    print("=" * 60)


async def _wait_and_click_element(automation: PlaywrightAutomation, selector: str, element_name: str, 
                                   logger=None, max_retries: int = 3, wait_timeout: int = 15000, use_css: bool = False):
    """
    Helper function để đợi element visible và click, với retry mechanism.
    Sau khi click, đợi network idle để DOM cập nhật.
    
    Args:
        automation: PlaywrightAutomation instance
        selector: XPath hoặc CSS selector của element (nếu use_css=True thì dùng CSS, ngược lại dùng XPath)
        element_name: Tên element để log
        logger: Logger instance (nếu None thì dùng print())
        max_retries: Số lần retry tối đa
        wait_timeout: Timeout cho mỗi lần đợi (ms)
        use_css: Nếu True thì dùng CSS selector, nếu False thì dùng XPath
    
    Returns:
        bool: True nếu click thành công, False nếu không
    """
    log_func = logger.info if logger else print
    log_warn = logger.warning if logger else print
    
    playright_selector = selector if use_css else f"xpath={selector}"
    
    for attempt in range(1, max_retries + 1):
        try:
            # Đợi element visible (quét lại HTML mỗi lần)
            log_func(f"  [Lần thử {attempt}/{max_retries}] Đang đợi {element_name} xuất hiện...")
            
            # Đợi element visible
            await automation.page.wait_for_selector(
                playright_selector, 
                state="visible", 
                timeout=wait_timeout
            )
            
            # Re-query element để đảm bảo lấy element mới nhất
            element = await automation.page.query_selector(playright_selector)
            if element:
                # Kiểm tra element có visible không
                is_visible = await element.is_visible()
                if not is_visible:
                    log_warn(f"  ⚠️ Element {element_name} tồn tại nhưng chưa visible, đợi thêm...")
                    await asyncio.sleep(2)
                    continue
                
                try:
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                except:
                    pass
                
                try:
                    await element.click(timeout=5000)
                except:
                    try:
                        await element.click(force=True, timeout=5000)
                    except Exception as click_error:
                        log_warn(f"  ⚠️ Lỗi khi click: {click_error}, thử lại...")
                        await asyncio.sleep(1)
                        continue
                
                log_func(f"  ✓ Đã click {element_name}")
                
                try:
                    await automation.page.wait_for_load_state("networkidle", timeout=3000)
                except:
                    await asyncio.sleep(1.5)
                
                return True
            else:
                log_warn(f"  ⚠️ Không tìm thấy {element_name} sau khi wait_for_selector")
                
        except Exception as e:
            if attempt < max_retries:
                log_warn(f"  ⚠️ Lỗi khi tìm {element_name} (lần {attempt}): {e}, thử lại...")
                await asyncio.sleep(2)
            else:
                log_warn(f"  ❌ Không tìm thấy {element_name} sau {max_retries} lần thử: {e}")
    
    return False

async def _grok_imagine_interact(automation: PlaywrightAutomation, filename: str = "", logger=None):
    """
    Helper function xử lý logic navigate đến Grok Imagine, click element và nhập filename.
    
    Args:
        automation: PlaywrightAutomation instance đã được khởi tạo và kết nối
        filename: Tên file để nhập vào input field
        logger: Logger instance (nếu None thì dùng print())
    
    Returns:
        dict với keys: success, message, url, input_found
    """
    log_func = logger.info if logger else print
    log_warn = logger.warning if logger else print
    
    grok_url = "https://grok.com/imagine"
    
    current_url = automation.page.url
    log_func(f"URL hiện tại: {current_url}")
    
    if current_url.rstrip('/') != grok_url.rstrip('/') and not current_url.startswith(grok_url + '/'):
        log_func(f"Đang điều hướng đến Grok Imagine: {grok_url}")
        await automation.navigate(grok_url)
        log_func(f"✓ Đã navigate - title: {await automation.page.title()}")
    else:
        log_func(f"✓ Đã ở trang Grok Imagine, bỏ qua bước navigate")

    try:
        await automation.page.wait_for_load_state("networkidle", timeout=10000)
    except:
        await asyncio.sleep(3)
    
    await asyncio.sleep(2)

    log_func("Bước 1: Đang tìm và bấm nút mở drive...")
    button1_found = await _wait_and_click_element(automation, "#radix-_r_u_", "nút mở drive", logger, wait_timeout=20000, use_css=True)
    if not button1_found:
        log_warn("❌ Bước 1 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 1: Không thể bấm nút mở drive",
            "url": automation.page.url,
            "input_found": False
        }

    log_func("Bước 2: Đang tìm và bấm nút drive...")
    button2_found = await _wait_and_click_element(automation, "//*[@id=\"radix-_r_v_\"]/div[3]", "nút drive", logger)
    if not button2_found:
        log_warn("❌ Bước 2 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 2: Không thể bấm nút drive",
            "url": automation.page.url,
            "input_found": False
        }

    log_func("Bước 3: Đang tìm và bấm vào input field...")
    input_xpath = "//*[@id=\"doclist\"]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/input"
    input_found = await _wait_and_click_element(automation, input_xpath, "input field", logger)
    if not input_found:
        log_warn("❌ Bước 3 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 3: Không thể bấm vào input field",
            "url": automation.page.url,
            "input_found": False
        }

    if filename:
        log_func(f"Bước 4: Đang nhập filename: {filename}")
        try:
            input_element = await automation.page.query_selector(f"xpath={input_xpath}")
            if input_element:
                await input_element.fill(filename)
                log_func("  ✓ Đã nhập filename thành công")
            else:
                log_warn("  ⚠️ Không tìm thấy input field để nhập filename")
                return {
                    "success": False,
                    "message": "Bước 4: Không tìm thấy input field để nhập filename",
                    "url": automation.page.url,
                    "input_found": False
                }
        except Exception as e:
            log_warn(f"  ⚠️ Lỗi khi nhập filename: {e}")
            return {
                "success": False,
                "message": f"Bước 4: Lỗi khi nhập filename: {e}",
                "url": automation.page.url,
                "input_found": False
            }
    else:
        log_warn("  ⚠️ Filename không được cung cấp")
        return {
            "success": False,
            "message": "Bước 4: Filename không được cung cấp",
            "url": automation.page.url,
            "input_found": False
        }

    log_func("Bước 5: Đang tìm và bấm nút search tìm kiếm...")
    button3_found = await _wait_and_click_element(automation, "//*[@id=\"doclist\"]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/div[2]", "nút search tìm kiếm", logger)
    if not button3_found:
        log_warn("❌ Bước 5 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 5: Không thể bấm nút search tìm kiếm",
            "url": automation.page.url,
            "input_found": True
        }

    log_func("Bước 6: Đang tìm và bấm filename vừa tìm được...")
    button4_found = await _wait_and_click_element(automation, "//*[@id=\":19.docs.0.1_i9Vf5-ASWbUjevDgWBRR-EarJLYGHAx\"]/div[1]/div/div[2]/div", "filename vừa tìm được", logger, wait_timeout=15000)
    if not button4_found:
        log_warn("❌ Bước 6 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 6: Không thể bấm filename vừa tìm được",
            "url": automation.page.url,
            "input_found": True
        }

    log_func("Bước 7: Đang tìm và bấm nút select...")
    button5_found = await _wait_and_click_element(automation, "//*[@id=\"picker:ap:2\"]", "nút select", logger, wait_timeout=15000)
    if not button5_found:
        log_warn("❌ Bước 7 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 7: Không thể bấm nút select",
            "url": automation.page.url,
            "input_found": True
        }

    current_url = automation.page.url
    page_title = await automation.page.title()
    
    log_func(f"✓ Hoàn thành")
    log_func(f"  URL hiện tại: {current_url}")
    log_func(f"  Title: {page_title}")

    message = "Đã navigate đến Grok Imagine và thực hiện các bước click thành công"
    
    return {
        "success": True,
        "message": message,
        "url": current_url,
        "input_found": input_found
    }


def get_automation_config(filename: str = "") -> AutomationInput:
    """
    Get automation configuration for Grok Imagine video generation.
    
    Args:
        filename: Filename to input into Grok Imagine (optional, can be set in actions)
    
    Returns:
        AutomationInput configuration for Grok gen video
    """
    config = AutomationInput(
        url="https://grok.com/imagine",
        headless=False,
        timeout=300000,
        viewport=ViewportConfig(width=1280, height=720),
        wait_for_selector="body",
        actions=[
            # Wait for page to load
            ActionConfig(
                type="wait",
                selector="body",
                timeout=10000
            ),
            # Bước 1: Bấm nút mở drive
            ActionConfig(
                type="click",
                selector="#radix-_r_u_",
                timeout=20000
            ),
            # Wait after clicking
            ActionConfig(
                type="wait",
                selector="body",
                timeout=2000
            ),
            # Bước 2: Bấm nút drive
            ActionConfig(
                type="click",
                selector="//*[@id=\"radix-_r_v_\"]/div[3]",
                timeout=20000
            ),
            # Wait after clicking
            ActionConfig(
                type="wait",
                selector="body",
                timeout=2000
            ),
            # Bước 3: Bấm vào input field
            ActionConfig(
                type="click",
                selector="//*[@id='doclist']/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/input",
                timeout=20000
            ),
            # Wait after clicking
            ActionConfig(
                type="wait",
                selector="body",
                timeout=1000
            ),
            # Bước 4: Nhập filename vào input
            ActionConfig(
                type="fill",
                selector="//*[@id=\"doclist\"]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/input",
                value=filename if filename else "YOUR_FILENAME_HERE",
                timeout=10000
            ),
            # Wait after filling
            ActionConfig(
                type="wait",
                selector="body",
                timeout=1000
            ),
            # Bước 5: Bấm nút search tìm kiếm
            ActionConfig(
                type="click",
                selector="//*[@id=\"doclist\"]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/div[2]",
                timeout=20000
            ),
            # Wait after clicking search
            ActionConfig(
                type="wait",
                selector="body",
                timeout=2000
            ),
            # Bước 6: Bấm filename vừa tìm được
            ActionConfig(
                type="click",
                selector="//*[@id=\":19.docs.0.1_i9Vf5-ASWbUjevDgWBRR-EarJLYGHAx\"]/div[1]/div/div[2]/div",
                timeout=15000
            ),
            # Wait after clicking filename
            ActionConfig(
                type="wait",
                selector="body",
                timeout=2000
            ),
            # Bước 7: Bấm nút select
            ActionConfig(
                type="click",
                selector="//*[@id=\"picker:ap:2\"]",
                timeout=15000
            ),
            # Final wait
            ActionConfig(
                type="wait",
                selector="body",
                timeout=5000
            )
        ],
        extract=[
            # Extract page title
            ExtractConfig(
                name="page_title",
                selector="title",
                multiple=False
            ),
            # Extract current URL
            ExtractConfig(
                name="current_url",
                selector="body",
                multiple=False
            )
        ]
    )
    return config


async def grok_gen_video_via_cdp(filename: str = ""):
    """
    Gen video với Grok Imagine qua CDP connection sử dụng _grok_imagine_interact.
    
    Navigate đến Grok Imagine (https://grok.com/imagine) và thực hiện các bước click để tạo video.
    Yêu cầu Chrome đã chạy với --remote-debugging-port=9224.
    
    Args:
        filename: Tên file để nhập vào input field
    """
    if not filename:
        print("⚠️ Filename không được để trống")
        return {
            "success": False,
            "error": "Filename không được để trống"
        }
    
    cdp_endpoint = "http://localhost:9224"
    
    # Check CDP trước
    if not _check_cdp_available(cdp_endpoint):
        print(f"❌ CDP không có sẵn tại {cdp_endpoint}")
        print("⚠️ Vui lòng khởi động Chrome với --remote-debugging-port=9224")
        return {
            "success": False,
            "error": f"CDP không có sẵn tại {cdp_endpoint}"
        }
    
    print("=" * 60)
    print(f"Bắt đầu gen video với Grok (sử dụng _grok_imagine_interact)")
    print(f"Filename: '{filename}'")
    print("=" * 60)

    automation = PlaywrightAutomation()

    try:
        # Kết nối với Chrome đang chạy qua CDP
        print(f"Đang kết nối với Chrome qua CDP tại {cdp_endpoint}...")
        await automation.connect_over_cdp(cdp_endpoint)
        print("✓ Đã kết nối thành công!")

        # Gọi hàm helper để xử lý logic
        result = await _grok_imagine_interact(automation, filename, logger=None)

        await automation.detach()
        return result

    except Exception as e:
        print(f"❌ Lỗi trong quá trình gen video với Grok: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def run_automation_via_cdp(config: AutomationInput = None, cdp_endpoint: str = "http://localhost:9224"):
    """
    Run automation via CDP connection sử dụng get_automation_config.
    
    Args:
        config: AutomationInput configuration (if None, uses default from get_automation_config)
        cdp_endpoint: CDP endpoint URL
    
    Returns:
        dict with automation results
    """
    # Check CDP trước
    if not _check_cdp_available(cdp_endpoint):
        print(f"❌ CDP không có sẵn tại {cdp_endpoint}")
        print("⚠️ Vui lòng khởi động Chrome với --remote-debugging-port=9224")
        return {
            "success": False,
            "error": f"CDP không có sẵn tại {cdp_endpoint}"
        }
    
    if config is None:
        config = get_automation_config()
    
    automation = PlaywrightAutomation(headless=config.headless, timeout=config.timeout, viewport=config.viewport)
    
    try:
        # Connect to Chrome via CDP
        print(f"Connecting to Chrome via CDP at {cdp_endpoint}...")
        await automation.connect_over_cdp(cdp_endpoint)
        print("✓ Connected successfully!")
        
        # Run automation
        results = await automation.run_automation(config)
        
        await automation.detach()
        return results
        
    except Exception as e:
        print(f"❌ Error running automation: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def main_cli():
    """
    Main CLI entry point với nhiều mode:
    
    Usage:
        python src/app/cdp_connection.py grok <filename>          # Grok via CDP với _grok_imagine_interact
        python src/app/cdp_connection.py cdp [filename]            # Automation via CDP với get_automation_config
    """
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Automation CLI - Usage:")
        print("=" * 60)
        print("  python src/app/cdp_connection.py grok <filename>")
        print("    → Chạy Grok Imagine qua CDP với _grok_imagine_interact")
        print("    → Cần Chrome đã chạy với --remote-debugging-port=9224")
        print()
        print("  python src/app/cdp_connection.py cdp [filename]")
        print("    → Chạy automation với config qua CDP (get_automation_config)")
        print("    → Cần Chrome đã chạy với --remote-debugging-port=9224")
        print("=" * 60)
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "grok":
            # Grok via CDP với _grok_imagine_interact
            if len(sys.argv) < 3:
                print("❌ Error: Please provide filename")
                print("Usage: python src/app/cdp_connection.py grok <filename>")
                return
            filename = sys.argv[2]
            print("=" * 60)
            print(f"Running Grok Imagine via CDP với _grok_imagine_interact")
            print(f"Filename: {filename}")
            print("=" * 60)
            result = await grok_gen_video_via_cdp(filename=filename)
            print("\n" + "=" * 60)
            print("Result:", result)
            print("=" * 60)
            
        elif command == "cdp":
            # Automation via CDP với config
            filename = sys.argv[2] if len(sys.argv) > 2 else ""
            print("=" * 60)
            print("Running automation via CDP với get_automation_config")
            print("⚠️  Make sure Chrome is running with --remote-debugging-port=9224")
            if filename:
                print(f"Filename: {filename}")
            print("=" * 60)
            config = get_automation_config(filename=filename) if filename else get_automation_config()
            result = await run_automation_via_cdp(config=config)
            _print_results(result)
            
        else:
            print(f"❌ Unknown command: {command}")
            print("\nAvailable commands:")
            print("  grok <filename>          - Grok via CDP với _grok_imagine_interact")
            print("  cdp [filename]            - Automation via CDP với get_automation_config")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main_cli())
