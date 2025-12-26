"""
Module kết nối Playwright với Chrome đang chạy qua CDP để gen video với Grok.

Sử dụng:
- CLI: python3 src/app/cdp_connection.py [filename]
- API: Import hàm grok_gen_video_via_cdp() trong api_server.py

Functions:
- grok_gen_video_via_cdp(): Navigate đến Grok Imagine và thực hiện các bước click để gen video qua CDP

Xem docs/CDP_CONNECTION.md để biết chi tiết.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation

async def _wait_and_click_element(automation: PlaywrightAutomation, xpath: str, element_name: str, 
                                   logger=None, max_retries: int = 3, wait_timeout: int = 10000):
    """
    Helper function để đợi element visible và click, với retry mechanism.
    Sau khi click, đợi network idle để DOM cập nhật.
    
    Args:
        automation: PlaywrightAutomation instance
        xpath: XPath selector của element
        element_name: Tên element để log
        logger: Logger instance (nếu None thì dùng print())
        max_retries: Số lần retry tối đa
        wait_timeout: Timeout cho mỗi lần đợi (ms)
    
    Returns:
        bool: True nếu click thành công, False nếu không
    """
    log_func = logger.info if logger else print
    log_warn = logger.warning if logger else print
    
    selector = f"xpath={xpath}"
    
    for attempt in range(1, max_retries + 1):
        try:
            # Đợi element visible (quét lại HTML mỗi lần)
            log_func(f"  [Lần thử {attempt}/{max_retries}] Đang đợi {element_name} xuất hiện...")
            await automation.page.wait_for_selector(
                selector, 
                state="visible", 
                timeout=wait_timeout
            )
            
            # Re-query element để đảm bảo lấy element mới nhất
            element = await automation.page.query_selector(selector)
            if element:
                # Kiểm tra element có visible không
                is_visible = await element.is_visible()
                if not is_visible:
                    log_warn(f"  ⚠️ Element {element_name} tồn tại nhưng chưa visible, đợi thêm...")
                    await asyncio.sleep(1)
                    continue
                
                # Click element
                await element.click()
                log_func(f"  ✓ Đã click {element_name}")
                
                # Đợi network idle để DOM cập nhật (quan trọng cho các nút ẩn)
                try:
                    await automation.page.wait_for_load_state("networkidle", timeout=3000)
                except:
                    # Nếu không có network activity, đợi một chút để DOM render
                    await asyncio.sleep(1)
                
                return True
            else:
                log_warn(f"  ⚠️ Không tìm thấy {element_name} sau khi wait_for_selector")
                
        except Exception as e:
            if attempt < max_retries:
                log_warn(f"  ⚠️ Lỗi khi tìm {element_name} (lần {attempt}): {e}, thử lại...")
                await asyncio.sleep(1)  # Đợi một chút trước khi retry
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
    
    # Kiểm tra URL hiện tại
    current_url = automation.page.url
    log_func(f"URL hiện tại: {current_url}")
    
    # Kiểm tra nếu đã ở trang Grok Imagine thì không cần navigate
    if current_url.rstrip('/') == grok_url.rstrip('/') or current_url.startswith(grok_url + '/'):
        log_func(f"✓ Đã ở trang Grok Imagine, bỏ qua bước navigate")
    else:
        log_func(f"Đang điều hướng đến Grok Imagine: {grok_url}")
        await automation.navigate(grok_url)
        log_func(f"✓ Đã navigate - title: {await automation.page.title()}")

    # Chờ trang load và các element render
    log_func("Đang chờ trang load...")
    try:
        await automation.page.wait_for_load_state("networkidle", timeout=10000)
    except:
        await asyncio.sleep(3)  # Fallback nếu không có network activity

    # Bước 1: Click nút đầu tiên
    log_func("Bước 1: Đang tìm và click nút đầu tiên...")
    button1_xpath = "/html/body/div[2]/div[2]/div/div/div/div/div[2]/div/form/div/div/div[2]/div[2]/button"
    button1_found = await _wait_and_click_element(automation, button1_xpath, "nút đầu tiên", logger)
    if not button1_found:
        log_warn("❌ Bước 1 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 1: Không thể click nút đầu tiên",
            "url": automation.page.url,
            "input_found": False
        }

    # Bước 2: Click nút thứ hai (sẽ hiện sau khi click nút đầu tiên)
    log_func("Bước 2: Đang tìm và click nút thứ hai...")
    button2_xpath = "/html/body/div[6]/div/div[3]"
    button2_found = await _wait_and_click_element(automation, button2_xpath, "nút thứ hai", logger)
    if not button2_found:
        log_warn("❌ Bước 2 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 2: Không thể click nút thứ hai",
            "url": automation.page.url,
            "input_found": False
        }

    # Bước 3: Click input field (sẽ hiện sau khi click nút thứ hai)
    log_func("Bước 3: Đang tìm và click input field...")
    input_xpath = "/html/body/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/input"
    input_found = await _wait_and_click_element(automation, input_xpath, "input field", logger)
    if not input_found:
        log_warn("❌ Bước 3 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 3: Không thể click input field",
            "url": automation.page.url,
            "input_found": False
        }

    # Bước 4: Nhập filename vào input
    if filename:
        log_func(f"Bước 4: Đang nhập filename: {filename}")
        try:
            # Re-query input để đảm bảo lấy element mới nhất
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

    # Bước 5: Click nút thứ ba (sẽ hiện sau khi nhập filename)
    log_func("Bước 5: Đang tìm và click nút thứ ba...")
    button3_xpath = "/html/body/div[2]/div/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[2]"
    button3_found = await _wait_and_click_element(automation, button3_xpath, "nút thứ ba", logger)
    if not button3_found:
        log_warn("❌ Bước 5 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 5: Không thể click nút thứ ba",
            "url": automation.page.url,
            "input_found": True
        }

    # Bước 6: Click nút thứ tư (sẽ hiện sau khi click nút thứ ba)
    log_func("Bước 6: Đang tìm và click nút thứ tư...")
    button4_xpath = "/html/body/div[2]/div/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div[2]"
    button4_found = await _wait_and_click_element(automation, button4_xpath, "nút thứ tư", logger, wait_timeout=15000)
    if not button4_found:
        log_warn("❌ Bước 6 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 6: Không thể click nút thứ tư",
            "url": automation.page.url,
            "input_found": True
        }

    # Bước 7: Click nút thứ năm (sẽ hiện sau khi click nút thứ tư)
    log_func("Bước 7: Đang tìm và click nút thứ năm...")
    button5_xpath = "/html/body/div[2]/div/div[3]/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div/div[1]"
    button5_found = await _wait_and_click_element(automation, button5_xpath, "nút thứ năm", logger, wait_timeout=15000)
    if not button5_found:
        log_warn("❌ Bước 7 thất bại, dừng quá trình")
        return {
            "success": False,
            "message": "Bước 7: Không thể click nút thứ năm",
            "url": automation.page.url,
            "input_found": True
        }

    current_url = automation.page.url
    page_title = await automation.page.title()
    
    log_func(f"✓ Hoàn thành")
    log_func(f"  URL hiện tại: {current_url}")
    log_func(f"  Title: {page_title}")

    message = f"Đã navigate đến Grok Imagine và thực hiện các bước click thành công"
    if not input_found:
        message += " (không tìm thấy input field)"
    
    return {
        "success": True,
        "message": message,
        "url": current_url,
        "input_found": input_found
    }


async def grok_gen_video_via_cdp(filename: str = ""):
    """
    Gen video với Grok Imagine qua CDP connection.
    
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
    
    print("=" * 60)
    print(f"Bắt đầu gen video với Grok")
    print(f"Filename: '{filename}'")
    print("=" * 60)

    automation = PlaywrightAutomation()

    try:
        # Kết nối với Chrome đang chạy qua CDP
        cdp_url = "http://localhost:9224"
        print(f"Đang kết nối với Chrome qua CDP tại {cdp_url}...")
        await automation.connect_over_cdp(cdp_url)
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


async def grok_gen_video_direct(filename: str = ""):
    """
    Gen video với Grok Imagine bằng cách launch Chrome trực tiếp (không qua CDP).
    
    Navigate đến Grok Imagine (https://grok.com/imagine) và thực hiện các bước click để tạo video.
    
    Args:
        filename: Tên file để nhập vào input field
    """
    automation = PlaywrightAutomation(headless=False)

    try:
        # Launch Chrome trực tiếp
        await automation.launch()

        # Gọi hàm helper để xử lý logic (không dùng logger vì đây là direct launch)
        result = await _grok_imagine_interact(automation, filename, logger=None)

        await automation.detach()
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def connect_to_chrome_via_cdp():
    """Entry point cho CLI - nhận filename từ command line để gen video với Grok."""

    # Nhận filename từ command line (CLI: arg1=filename)
    filename = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not filename:
        print("⚠️ Vui lòng cung cấp filename để gen video")
        print("Sử dụng: python3 src/app/cdp_connection.py \"filename\"")
        return

    await grok_gen_video_via_cdp(filename=filename)


if __name__ == "__main__":
    asyncio.run(connect_to_chrome_via_cdp())
