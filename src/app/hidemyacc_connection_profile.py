"""
Module launch Playwright với HideMyAcc profile và scrape Etsy.

Có 2 hàm chính:
- launch_hidemyacc_profile_for_api(): Dùng cho API server
- launch_with_profile(): Dùng cho CLI

Xem docs/ETSY_SCRAPING_API.md để biết chi tiết cách sử dụng.
"""
import asyncio
import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation
from src.utils.hidemyacc import HideMyAccManager
from src.utils.heyetsy_parser import extract_heyetsy_data
from src.models import SearchInput
from urllib.parse import quote_plus


async def launch_hidemyacc_profile_for_api(
    profile_id: str = None,
    use_command_line_config: bool = False,
    cdp_port: int = 9223,
    proxy_server: str = None,
    proxy_username: str = None,
    proxy_password: str = None
) -> tuple:
    """
    Launch HideMyAcc profile cho API server - chỉ launch, không scrape.
    
    Returns: (automation, profile_info) hoặc (None, None) nếu lỗi.
    Xem docs/ETSY_SCRAPING_API.md để biết chi tiết.
    """
    print("=" * 60)
    print("Launch HideMyAcc Profile cho API")
    print("=" * 60)
    print()
    
    # Tìm profiles
    manager = HideMyAccManager()
    profiles = manager.find_profiles()
    
    if not profiles:
        print("❌ Không tìm thấy HideMyAcc profiles!")
        return None, None
    
    # Chọn profile
    if not profile_id:
        if len(profiles) > 1:
            print(f"⚠️  Nhiều profiles tìm thấy ({len(profiles)}), sử dụng profile đầu tiên")
        profile = profiles[0]
        profile_id = profile['name']
    else:
        profile = manager.get_profile_by_id(profile_id)
        if not profile:
            print(f"❌ Không tìm thấy profile: {profile_id}")
            return None, None
    
    print(f"Đang sử dụng profile: {profile['name']}")
    print(f"Profile path: {profile['user_data_dir']}")
    print()
    
    # Cấu hình từ command line
    # Luôn sử dụng cấu hình này khi use_command_line_config=True
    if use_command_line_config:
        # Tự động tìm Marco browser mới nhất trong ~/.hidemyacc/browser/
        # Marco browser là browser được HideMyAcc cung cấp, có fingerprinting tốt hơn Chrome thường
        executable_path = manager._find_marco_browser()
        if executable_path:
            print(f"✓ Tìm thấy Marco browser: {executable_path}")
        else:
            print("⚠️  Không tìm thấy Marco browser, sẽ dùng Chrome mặc định")
        
        # Cấu hình proxy: chỉ dùng proxy từ API request, không dùng default hardcode
        # Proxy được truyền vào từ API request body (optional)
        proxy = None
        if proxy_server:
            # Có proxy server từ API - phải có đầy đủ username và password
            # Format: {"server": "http://host:port", "username": "...", "password": "..."}
            proxy = {
                "server": proxy_server,
                "username": proxy_username,
                "password": proxy_password
            }
            print(f"✓ Proxy với authentication: {proxy_server}")
        else:
            # Không có proxy từ API - không dùng proxy
            # Browser sẽ dùng connection trực tiếp (không qua proxy)
            print("✓ Không sử dụng proxy")
        
        hidemyacc_data = "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"
        
        # Extra args từ command line configuration
        # --hidemyacc-data là arg riêng của HideMyAcc, cần thiết để kết nối đúng profile
        # hidemyacc_data là encoded string chứa thông tin profile configuration
        # --remote-debugging-port cho phép kết nối CDP (nếu cần debug)
        extra_args = [
            "--lang=en-US",
            "--disable-encryption",
            "--restore-last-session",
            f"--hidemyacc-data={hidemyacc_data}",
            "--disable-features=ExtensionsToolbarMenu,ChromeLabs,ReadLater,TriggerNetworkDataMigration,ChromeWhatsNewUI,ViewportHeightClientHintHeader",
            "--flag-switches-begin",
            "--flag-switches-end",
            "--origin-trial-disabled-features=CanvasTextNg|WebAssemblyCustomDescriptors",
            f"--remote-debugging-port={cdp_port}",  # CDP port để có thể kết nối qua CDP nếu cần
        ]
        
        print("✓ Sử dụng cấu hình từ command line")
        print(f"  Executable: {executable_path}")
        print(f"  Proxy: {proxy['server'] if proxy else 'None'}")
        print(f"  CDP Port: {cdp_port}")
        print()
    else:
        executable_path = manager._find_marco_browser()
        proxy = None
        extra_args = [
            f"--remote-debugging-port={cdp_port}",  # Thêm CDP port
        ]
        
        if executable_path:
            print(f"✓ Tìm thấy Marco browser: {executable_path}")
        else:
            print("⚠️  Không tìm thấy Marco browser, sẽ sử dụng Chrome mặc định")
        print(f"  CDP Port: {cdp_port}")
        print()
    
    # Launch Playwright với profile
    # headless=False để hiển thị browser (có thể debug và xem quá trình)
    automation = PlaywrightAutomation(headless=False)
    
    try:
        print("Đang launch Playwright với HideMyAcc profile...")
        print()
        
        # Launch browser với profile qua user-data-dir
        # Playwright sẽ sử dụng profile có sẵn thay vì tạo profile mới
        # require_executable=True để đảm bảo dùng đúng Marco browser, không fallback Chromium
        await automation.launch_with_profile(
            profile['user_data_dir'],
            executable_path=executable_path,
            proxy=proxy,
            extra_args=extra_args,
            require_executable=True  # Bắt buộc dùng đúng executable để không fallback Chromium mặc định
        )
        
        print("✓ Đã launch thành công!")
        print()
        
        profile_info = {
            "profile_id": profile['name'],
            "profile_name": profile.get('name', profile['name']),
            "user_data_dir": profile['user_data_dir'],
            "cdp_port": cdp_port
        }
        
        return automation, profile_info
        
    except Exception as e:
        print(f"❌ Lỗi khi launch profile: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def launch_with_profile(
    profile_id: str = None, 
    use_command_line_config: bool = False, 
    disable_proxy: bool = False,
    keyword: str = "t-shirt",
    pages: int = 5
):
    """
    Launch HideMyAcc profile và thực hiện scraping Etsy - dùng cho CLI.
    
    Xem docs/ETSY_SCRAPING_API.md để biết chi tiết cách sử dụng.
    """
    print("=" * 60)
    print("Test Launch Playwright với HideMyAcc Profile")
    print("=" * 60)
    print()
    
    # Tìm profiles
    manager = HideMyAccManager()
    profiles = manager.find_profiles()
    
    if not profiles:
        print("❌ Không tìm thấy HideMyAcc profiles!")
        return None
    
    # Chọn profile
    if not profile_id:
        print(f"Tìm thấy {len(profiles)} profile(s):")
        print()
        for i, profile in enumerate(profiles, 1):
            print(f"  [{i}] {profile['name']}")
        print()
        
        if len(profiles) > 1:
            print("⚠️  Cần chỉ định profile_id")
            print("   Ví dụ: python3 src/app/test_hidemyacc_profile.py --profile hma_xxx")
            return None
        else:
            profile = profiles[0]
            profile_id = profile['name']
    else:
        profile = manager.get_profile_by_id(profile_id)
        if not profile:
            print(f"❌ Không tìm thấy profile: {profile_id}")
            return None
    
    print(f"Đang sử dụng profile: {profile['name']}")
    print(f"Profile path: {profile['user_data_dir']}")
    print()
    
    # Luôn dùng cấu hình từ command line (executable path, extra args, hidemyacc-data)
    # Tự động tìm Marco browser mới nhất thay vì hardcode path
    executable_path = manager._find_marco_browser()
    if executable_path:
        print(f"✓ Tìm thấy Marco browser: {executable_path}")
    else:
        print("⚠️  Không tìm thấy Marco browser, sẽ dùng Chrome mặc định")
    
    # Proxy: chỉ dùng nếu không có flag disable_proxy
    proxy = None
    if not disable_proxy:
        # Playwright cần plain text, không phải base64
        import base64
        try:
            # Decode base64 username/password
            username_decoded = base64.b64decode("OWJhMGJjZjhlOQ==").decode('utf-8')
            password_decoded = base64.b64decode("TVJFN1lBU2c=").decode('utf-8')
            print(f"[DEBUG] Proxy credentials decoded successfully")
            print(f"[DEBUG] Proxy username: {username_decoded}")
            print(f"[DEBUG] Proxy password: {'*' * len(password_decoded)}")
            
            proxy = {
                "server": "http://149.20.240.190:4444",
                "username": username_decoded,  # Decoded từ base64
                "password": password_decoded    # Decoded từ base64
            }
            print(f"✓ Sử dụng proxy mặc định (hardcode): {proxy['server']}")
        except Exception as e:
            print(f"❌ Lỗi: Không thể decode proxy credentials: {e}")
            print("   Proxy credentials có thể không đúng format base64")
            import traceback
            traceback.print_exc()
            proxy = None  # Không dùng proxy nếu không decode được
    else:
        print("✓ Proxy đã bị tắt (--no-proxy flag hoặc chạy trực tiếp)")
    
    # Extra args từ command line (luôn dùng)
    # --hidemyacc-data là arg riêng của HideMyAcc, cần thiết để kết nối đúng profile
    hidemyacc_data = "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"
    extra_args = [
        "--lang=en-US",
        "--disable-encryption",
        "--restore-last-session",
        f"--hidemyacc-data={hidemyacc_data}",
        "--disable-features=ExtensionsToolbarMenu,ChromeLabs,ReadLater,TriggerNetworkDataMigration,ChromeWhatsNewUI,ViewportHeightClientHintHeader",
        "--flag-switches-begin",
        "--flag-switches-end",
        "--origin-trial-disabled-features=CanvasTextNg|WebAssemblyCustomDescriptors",
    ]
    
    print("✓ Sử dụng cấu hình từ command line")
    print(f"  Executable: {executable_path}")
    print(f"  Proxy: {proxy['server'] if proxy else 'None (không dùng proxy)'}")
    print(f"  Extra args: {len(extra_args)} arguments (bao gồm --hidemyacc-data)")
    print()
    
    # Launch Playwright với profile
    automation = PlaywrightAutomation(headless=False)
    
    try:
        print("Đang launch Playwright với HideMyAcc profile...")
        print("(Sử dụng launch_persistent_context với executable_path - giống JavaScript example)")
        print()
        
        # Proxy đã được xử lý trong phần use_command_line_config
        # Không cần xử lý lại ở đây vì proxy đã được set đúng trong if/else block trên
        
        # Launch với cấu hình từ command line hoặc tự động tìm
        await automation.launch_with_profile(
            profile['user_data_dir'],
            executable_path=executable_path,
            proxy=proxy,
            extra_args=extra_args,
            require_executable=True  # Bắt buộc dùng đúng executable để không fallback Chromium mặc định
        )
        
        print("✓ Đã launch thành công!")
        print()
        print(f"Context: {automation.context}")
        print(f"Page URL hiện tại: {automation.page.url}")
        print()
        
        # Thực hiện search trên Etsy giống như cdp_connection.py
        search_input = SearchInput(keyword=keyword, pages=pages)
        print("=" * 60)
        print(f"Bắt đầu crawl Etsy: keyword='{search_input.keyword}', pages={search_input.pages}")
        print("=" * 60)
        print()
        
        all_data = {}
        
        for page_num in range(1, search_input.pages + 1):
            target_url = (
                f"https://www.etsy.com/search?q={quote_plus(search_input.keyword)}"
                f"&page={page_num}&ref=pagination"
            )
            print(f"Đang điều hướng đến trang {page_num}: {target_url}")
            try:
                await automation.navigate(target_url)
                print(f"✓ Trang {page_num} - title: {await automation.page.title()}")
                print(f"  URL: {automation.page.url}")
                
                # Chờ trang tải ổn định (10 giây)
                await asyncio.sleep(10)
                
                print("Đang lấy body và trích xuất dữ liệu...")
                try:
                    body_html = await automation.page.evaluate(
                        """
                        () => {
                            const clone = document.body.cloneNode(true);
                            clone.querySelectorAll('script, style').forEach((el) => el.remove());
                            return clone.outerHTML;
                        }
                        """
                    )
                    
                    cleaned_body = re.sub(r"\s+", " ", body_html).strip()
                    
                    # Trích xuất dữ liệu HeyEtsy từ body
                    extracted = extract_heyetsy_data(cleaned_body)
                    for item in extracted:
                        if not item.get("title") or not item.get("image"):
                            continue
                        lid = item.get("listing_id")
                        if lid and lid not in all_data:
                            all_data[lid] = item
                    
                    print(f"✓ Trang {page_num}: trích được {len(extracted)} mục (tổng duy nhất: {len(all_data)})")
                except Exception as extract_error:
                    print(f"❌ Lỗi khi xử lý trang {page_num}: {extract_error}")
                    import traceback
                    traceback.print_exc()
            except Exception as nav_error:
                print(f"❌ Lỗi khi navigate trang {page_num}: {nav_error}")
                import traceback
                traceback.print_exc()
                print()
        
        # Hiển thị kết quả
        print()
        print("=" * 60)
        print(f"✓ Hoàn thành crawl: {len(all_data)} sản phẩm duy nhất từ {search_input.pages} trang")
        print("=" * 60)
        print()
        
        if all_data:
            print("Một số sản phẩm đã crawl:")
            for i, (lid, item) in enumerate(list(all_data.items())[:5], 1):
                print(f"  [{i}] {item.get('title', 'N/A')[:50]}...")
                print(f"      Listing ID: {lid}")
                print(f"      Sold 24H: {item.get('sold_24h', 'N/A')}")
                print()
            if len(all_data) > 5:
                print(f"  ... và {len(all_data) - 5} sản phẩm khác")
                print()
        
        # KHÔNG ĐÓNG BROWSER - giữ mở để bạn có thể sử dụng
        print("=" * 60)
        print("✓ Browser đã được launch và giữ mở!")
        print("  Browser sẽ KHÔNG tự động đóng.")
        print("  Bạn có thể tiếp tục sử dụng browser này.")
        print("=" * 60)
        print()
        print("⚠️  Lưu ý: Để đóng browser, hãy đóng cửa sổ browser thủ công")
        print("   hoặc gọi automation.close() trong code của bạn.")
        print()
        print("📌 Browser đang chạy... Bạn có thể thấy cửa sổ browser đang mở.")
        print("   Script sẽ chờ để giữ browser mở (nhấn Ctrl+C để thoát script nhưng browser vẫn mở).")
        print()
        
        # Giữ script chạy để browser không đóng
        # Sử dụng asyncio.sleep với loop vô hạn để giữ browser mở
        try:
            while True:
                await asyncio.sleep(1)
                # In thông tin định kỳ để user biết script vẫn chạy
        except KeyboardInterrupt:
            print()
            print("⚠️  Nhận được tín hiệu dừng (Ctrl+C)")
            print("   Browser vẫn đang mở, bạn có thể tiếp tục sử dụng.")
            print("   Để đóng browser, hãy đóng cửa sổ browser thủ công.")
            print()
        
        # Không gọi automation.close() - giữ browser mở
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main function cho CLI - parse arguments và gọi launch_with_profile()."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test launch Playwright với HideMyAcc profile và crawl Etsy")
    parser.add_argument("--profile", "-p", help="HideMyAcc profile ID/name")
    parser.add_argument("--no-proxy", action="store_true",
                       help="Tắt proxy (mặc định True khi chạy trực tiếp - không dùng proxy)")
    parser.add_argument("--with-proxy", action="store_true",
                       help="Bật proxy (mặc định không dùng proxy khi chạy trực tiếp)")
    parser.add_argument("--keyword", "-k", default="t-shirt",
                       help="Từ khóa để search trên Etsy (mặc định: t-shirt)")
    parser.add_argument("--pages", type=int, default=5,
                       help="Số trang để crawl (mặc định: 5)")
    
    args = parser.parse_args()
    
    # Logic: Luôn dùng command line config (executable + args), chỉ check proxy
    # Mặc định: disable_proxy=True (không dùng proxy) trừ khi có --with-proxy
    disable_proxy = args.no_proxy or not args.with_proxy
    
    await launch_with_profile(
        args.profile, 
        use_command_line_config=True,  # Luôn True - luôn dùng config
        disable_proxy=disable_proxy,
        keyword=args.keyword,
        pages=args.pages
    )


if __name__ == "__main__":
    asyncio.run(main())