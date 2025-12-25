"""
Module launch Playwright với HideMyAcc profile và spy Etsy.

Có 2 hàm chính:
- launch_hidemyacc_profile_for_api(): Dùng cho API server
- launch_with_profile(): Dùng cho CLI

Xem docs/ETSY_SPY_API.md để biết chi tiết cách sử dụng.
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
    cdp_port: int = 9223,
    proxy_server: str = None,
    proxy_username: str = None,
    proxy_password: str = None
) -> tuple:
    """
    Launch HideMyAcc profile cho API server - chỉ launch, KHÔNG đóng profile.
    
    Logic hoạt động:
    1. Lần đầu tiên (profile chưa mở):
       - Kiểm tra CDP port → không thấy
       - Dùng direct launch (launch_with_profile) → Playwright điều khiển trực tiếp
       - Marco browser được launch với --remote-debugging-port để mở CDP port
       - Profile được giữ mở (không đóng)
    
    2. Lần sau (profile đã mở):
       - Kiểm tra CDP port → thấy đang chạy
       - Dùng CDP connection (connect_over_cdp) → Playwright điều khiển QUA CDP
       - Tái sử dụng Marco browser đang chạy, không launch mới
    
    Returns: (automation, profile_info) hoặc (None, None) nếu lỗi.
    Profile sẽ được giữ mở - không tự động đóng.
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
    
    # Logic: Kiểm tra xem CDP đã chạy chưa (profile đã mở)
    # - Lần đầu tiên: CDP chưa chạy → dùng direct launch (launch_with_profile)
    # - Lần sau: CDP đã chạy → dùng CDP connection (connect_over_cdp)
    print(f"Đang kiểm tra CDP port {cdp_port}...")
    if manager.check_cdp_running(cdp_port):
        print(f"✓ CDP đã chạy tại port {cdp_port} - profile đã mở!")
        print("  [Lần sau] Sẽ kết nối với Marco browser đang chạy QUA CDP thay vì launch mới.")
        print()
        
        # Kết nối với Marco browser đang chạy QUA CDP
        # Đây là cách điều khiển QUA CDP (khác với direct launch)
        # Tăng timeout lên 60 giây cho mỗi operation để tránh timeout khi xử lý nhiều trang
        automation = PlaywrightAutomation(headless=False, timeout=60000)
        try:
            cdp_endpoint = f"http://localhost:{cdp_port}"
            print(f"Đang kết nối với Marco browser qua CDP tại {cdp_endpoint}...")
            await automation.connect_over_cdp(cdp_endpoint)
            print("✓ Đã kết nối thành công với Marco browser đang chạy QUA CDP!")
            print()
            
            profile_info = {
                "profile_id": profile['name'],
                "profile_name": profile.get('name', profile['name']),
                "user_data_dir": profile['user_data_dir'],
                "cdp_port": cdp_port,
                "reused": True  # Đánh dấu là đã tái sử dụng
            }
            
            return automation, profile_info
            
        except Exception as e:
            print(f"❌ Lỗi khi kết nối với Chrome qua CDP: {e}")
            print("  Sẽ thử launch mới...")
            print()
            import traceback
            traceback.print_exc()
            # Tiếp tục với launch mới nếu kết nối thất bại
    
    # Nếu CDP chưa chạy hoặc kết nối thất bại, launch mới
    # [Lần đầu tiên] Sử dụng direct launch (launch_with_profile) - Playwright điều khiển trực tiếp
    print("CDP chưa chạy hoặc không thể kết nối - sẽ launch Marco browser mới...")
    print("[Lần đầu tiên] Sử dụng direct launch - Playwright điều khiển trực tiếp, không qua CDP")
    print()
    
    # Tự động tìm Marco browser
    executable_path = manager._find_marco_browser()
    if executable_path:
        print(f"✓ Tìm thấy Marco browser: {executable_path}")
    else:
        print("⚠️  Không tìm thấy Marco browser, sẽ dùng Chrome mặc định")
    
    # Cấu hình proxy (nếu có)
    proxy = None
    if proxy_server:
        proxy = {
            "server": proxy_server,
            "username": proxy_username,
            "password": proxy_password
        }
        print(f"✓ Proxy với authentication: {proxy_server}")
    else:
        print("✓ Không sử dụng proxy")
    
    hidemyacc_data = "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"
    
    extra_args = [
        "--lang=en-US",
        "--disable-encryption",
        "--restore-last-session",
        f"--hidemyacc-data={hidemyacc_data}",
        "--disable-features=ExtensionsToolbarMenu,ChromeLabs,ReadLater,TriggerNetworkDataMigration,ChromeWhatsNewUI,ViewportHeightClientHintHeader",
        "--flag-switches-begin",
        "--flag-switches-end",
        f"--remote-debugging-port={cdp_port}",  # Mở CDP port để cho phép kết nối lại sau này (nếu cần)
    ]
    
    print(f"✓ CDP Port: {cdp_port} (để kết nối lại sau này nếu cần)")
    print()
    
    # Launch Playwright với profile
    # Lưu ý: Playwright điều khiển Marco browser TRỰC TIẾP qua launch_persistent_context,
    # KHÔNG qua CDP. --remote-debugging-port chỉ để mở CDP port cho kết nối sau này.
    automation = PlaywrightAutomation(headless=False)
    
    try:
        print("Đang launch Playwright với HideMyAcc profile...")
        print("(Playwright điều khiển trực tiếp, không qua CDP)")
        print()
        
        await automation.launch_with_profile(
            profile['user_data_dir'],
            executable_path=executable_path,
            proxy=proxy,
            extra_args=extra_args,
            require_executable=True
        )
        
        print("✓ Đã launch thành công!")
        print("⚠️  Profile sẽ KHÔNG tự động đóng - giữ mở để sử dụng.")
        print()
        
        profile_info = {
            "profile_id": profile['name'],
            "profile_name": profile.get('name', profile['name']),
            "user_data_dir": profile['user_data_dir'],
            "cdp_port": cdp_port,
            "reused": False  # Đánh dấu là launch mới
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
    
    Xem docs/ETSY_SPY_API.md để biết chi tiết cách sử dụng.
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
        print(f"Bắt đầu spy Etsy: keyword='{search_input.keyword}', pages={search_input.pages}")
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
        print(f"✓ Hoàn thành spy: {len(all_data)} sản phẩm duy nhất từ {search_input.pages} trang")
        print("=" * 60)
        print()
        
        if all_data:
            print("Một số sản phẩm đã spy:")
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
    
    parser = argparse.ArgumentParser(description="Test launch Playwright với HideMyAcc profile và spy Etsy")
    parser.add_argument("--profile", "-p", help="HideMyAcc profile ID/name")
    parser.add_argument("--no-proxy", action="store_true",
                       help="Tắt proxy (mặc định True khi chạy trực tiếp - không dùng proxy)")
    parser.add_argument("--with-proxy", action="store_true",
                       help="Bật proxy (mặc định không dùng proxy khi chạy trực tiếp)")
    parser.add_argument("--keyword", "-k", default="t-shirt",
                       help="Từ khóa để search trên Etsy (mặc định: t-shirt)")
    parser.add_argument("--pages", type=int, default=5,
                       help="Số trang để spy (mặc định: 5)")
    
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