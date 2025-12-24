"""
Module kết nối Playwright với Chrome đang chạy qua CDP để gen video với Grok.

Sử dụng:
- CLI: python3 src/app/cdp_connection.py [text]
- API: Import hàm grok_gen_video_via_cdp() trong api_server.py

Functions:
- grok_gen_video_via_cdp(): Navigate đến Grok Imagine và nhập prompt để gen video qua CDP

Xem docs/CDP_CONNECTION.md để biết chi tiết.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation
from src.models import GrokInput

async def _grok_imagine_interact(automation: PlaywrightAutomation, text: str, logger=None):
    """
    Helper function xử lý logic navigate đến Grok Imagine, click element và nhập text.
    
    Args:
        automation: PlaywrightAutomation instance đã được khởi tạo và kết nối
        text: Text prompt để nhập vào input
        logger: Logger instance (nếu None thì dùng print())
    
    Returns:
        dict với keys: success, message, url, input_found
    """
    log_func = logger.info if logger else print
    log_warn = logger.warning if logger else print
    
    grok_input = GrokInput(text=text)
    grok_url = "https://grok.com/imagine"
    
    log_func(f"Đang điều hướng đến Grok Imagine: {grok_url}")
    await automation.navigate(grok_url)
    log_func(f"✓ Đã navigate - title: {await automation.page.title()}")

    # Chờ trang load và các element render (5 giây)
    log_func("Đang chờ trang load (5 giây)...")
    await asyncio.sleep(5)

    # Tìm input field để nhập text
    log_func("Đang tìm input field để nhập text...")
    input_selectors = [
        "textarea[placeholder*='message' i]",
        "textarea[placeholder*='ask' i]",
        "textarea[placeholder*='chat' i]",
        "textarea[placeholder*='imagine' i]",
        "textarea[placeholder*='describe' i]",
        "textarea[aria-label*='message' i]",
        "textarea[aria-label*='input' i]",
        "textarea",
        "input[type='text'][placeholder*='message' i]",
        "[contenteditable='true']",
        ".chat-input",
        "#chat-input",
    ]

    input_element = None
    for selector in input_selectors:
        try:
            input_element = await automation.page.query_selector(selector)
            if input_element:
                log_func(f"✓ Tìm thấy input với selector: {selector}")
                break
        except Exception as e:
            continue

    if not input_element:
        # Thử tìm bất kỳ textarea hoặc contenteditable nào
        try:
            input_element = await automation.page.query_selector("textarea")
            if not input_element:
                input_element = await automation.page.query_selector("[contenteditable='true']")
        except Exception as e:
            pass

    input_found = input_element is not None
    if input_element:
        # Nhập prompt vào input để gen video
        log_func(f"Đang nhập prompt vào input field...")
        await input_element.fill(grok_input.text)
        log_func(f"✓ Đã nhập prompt thành công")
        
        # Đợi 5 giây sau khi nhập text
        log_func("Đang đợi 5 giây sau khi nhập text...")
        await asyncio.sleep(5)
        
        # Tìm và click vào nút submit
        # Sử dụng cách tìm button từ form với selector đơn giản hơn
        log_func("Đang tìm nút submit...")
        button_found = False
        try:
            # Cách 1: Tìm button trong form bằng cách tìm từ input element đã có
            # Tìm form chứa input, sau đó tìm button trong div.ms-auto > div:nth-child(3)
            button_found = await automation.page.evaluate(
                """
                () => {
                    // Tìm form
                    const form = document.querySelector('form');
                    if (!form) return false;
                    
                    // Tìm div.ms-auto trong form
                    const msAutoDiv = form.querySelector('div.ms-auto');
                    if (!msAutoDiv) return false;
                    
                    // Tìm div thứ 3 trong msAutoDiv
                    const divs = msAutoDiv.querySelectorAll('div');
                    if (divs.length < 3) return false;
                    
                    const thirdDiv = divs[2]; // nth-child(3) = index 2
                    const button = thirdDiv.querySelector('button');
                    
                    if (button) {
                        button.click();
                        return true;
                    }
                    
                    return false;
                }
                """
            )
            
            if not button_found:
                # Fallback 1: Tìm button bằng XPath tương đối
                try:
                    button_xpath = "//body//form//div[contains(@class, 'ms-auto')]//div[3]/button"
                    button_element = await automation.page.query_selector(f"xpath={button_xpath}")
                    if button_element:
                        await button_element.click()
                        button_found = True
                        log_func("✓ Đã tìm thấy và click vào nút submit bằng XPath tương đối")
                except Exception as e:
                    log_warn(f"⚠️ Lỗi khi tìm button bằng XPath tương đối: {e}")
            
            if not button_found:
                # Fallback 2: Tìm button bằng full XPath
                try:
                    full_xpath = "/html/body/div[2]/div[2]/div/div/div/div[2]/div/form/div/div/div[2]/div[2]/div[2]/div[3]/button"
                    button_element = await automation.page.query_selector(f"xpath={full_xpath}")
                    if button_element:
                        await button_element.click()
                        button_found = True
                        log_func("✓ Đã tìm thấy và click vào nút submit bằng full XPath")
                except Exception as e:
                    log_warn(f"⚠️ Lỗi khi tìm button bằng full XPath: {e}")
            
            if button_found:
                log_func("✓ Đã tìm thấy và click vào nút submit")
            else:
                log_warn("⚠️ Không tìm thấy nút submit với tất cả các cách thử")
        except Exception as e:
            log_warn(f"⚠️ Lỗi khi tìm/click nút submit: {e}")
        
        # Đợi 60 giây sau khi click nút submit
        log_func("Đang đợi 60 giây sau khi click nút submit...")
        await asyncio.sleep(60)
        
        # Tìm và click nút download video
        log_func("Đang tìm nút download video...")
        download_button_found = False
        try:
            download_button_xpath = "/html/body/div[2]/div[2]/div/div/div/main/article/div[2]/div[2]/div/button[1]"
            download_button_element = await automation.page.query_selector(f"xpath={download_button_xpath}")
            if download_button_element:
                await download_button_element.click()
                download_button_found = True
                log_func("✓ Đã tìm thấy và click vào nút download video")
            else:
                log_warn("⚠️ Không tìm thấy nút download video")
        except Exception as e:
            log_warn(f"⚠️ Lỗi khi tìm/click nút download video: {e}")
        
        # Đợi thêm 10 giây sau khi click nút download video
        if download_button_found:
            log_func("Đang đợi 10 giây sau khi click nút download video...")
            await asyncio.sleep(10)
    else:
        log_warn("⚠️ Không tìm thấy input field để nhập text")

    current_url = automation.page.url
    page_title = await automation.page.title()
    
    log_func(f"✓ Hoàn thành")
    log_func(f"  URL hiện tại: {current_url}")
    log_func(f"  Title: {page_title}")

    message = f"Đã navigate đến Grok Imagine, nhập prompt để gen video và download video thành công"
    if not input_found:
        message += " (không tìm thấy input field, chỉ navigate)"
    
    return {
        "success": True,
        "message": message,
        "url": current_url,
        "input_found": input_found
    }


async def grok_gen_video_via_cdp(text: str = ""):
    """
    Gen video với Grok Imagine qua CDP connection.
    
    Navigate đến Grok Imagine (https://grok.com/imagine) và nhập prompt text để tạo video.
    Yêu cầu Chrome đã chạy với --remote-debugging-port=9224.
    """
    if not text:
        print("⚠️ Text không được để trống")
        return {
            "success": False,
            "error": "Text không được để trống"
        }
    
    print("=" * 60)
    print(f"Bắt đầu gen video với Grok: prompt='{text[:50]}...'")
    print("=" * 60)

    automation = PlaywrightAutomation()

    try:
        # Kết nối với Chrome đang chạy qua CDP
        cdp_url = "http://localhost:9224"
        print(f"Đang kết nối với Chrome qua CDP tại {cdp_url}...")
        await automation.connect_over_cdp(cdp_url)
        print("✓ Đã kết nối thành công!")

        # Gọi hàm helper để xử lý logic
        result = await _grok_imagine_interact(automation, text, logger=None)

        await automation.detach()
        return result

    except Exception as e:
        print(f"❌ Lỗi trong quá trình gen video với Grok: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def grok_gen_video_direct(text: str = ""):
    """
    Gen video với Grok Imagine bằng cách launch Chrome trực tiếp (không qua CDP).
    
    Navigate đến Grok Imagine (https://grok.com/imagine) và nhập prompt text để tạo video.
    """
    if not text:
        return {
            "success": False,
            "error": "Text không được để trống"
        }
    
    automation = PlaywrightAutomation(headless=False)

    try:
        # Launch Chrome trực tiếp
        await automation.launch()

        # Gọi hàm helper để xử lý logic (không dùng logger vì đây là direct launch)
        result = await _grok_imagine_interact(automation, text, logger=None)

        await automation.detach()
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def connect_to_chrome_via_cdp():
    """Entry point cho CLI - nhận text prompt từ command line để gen video với Grok."""

    # Nhận prompt text từ command line (CLI: arg1=text)
    text = sys.argv[1] if len(sys.argv) > 1 else ""
    if not text:
        print("⚠️ Vui lòng cung cấp prompt text để gen video")
        print("Sử dụng: python3 src/app/cdp_connection.py \"your prompt text\"")
        return

    await grok_gen_video_via_cdp(text=text)


if __name__ == "__main__":
    asyncio.run(connect_to_chrome_via_cdp())
