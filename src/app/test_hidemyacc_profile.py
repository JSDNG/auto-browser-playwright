"""
Test script để launch Playwright với HideMyAcc profile qua user-data-dir
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation
from src.utils.hidemyacc import HideMyAccManager


async def test_launch_with_profile(profile_id: str = None, use_command_line_config: bool = False, disable_proxy: bool = False):
    """
    Test launch Playwright với HideMyAcc profile qua user-data-dir
    
    Args:
        profile_id: Profile ID để sử dụng
        use_command_line_config: Nếu True, sử dụng cấu hình từ command line (proxy, args, executable)
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
    
    # Cấu hình từ command line (theo thông tin bạn cung cấp)
    if use_command_line_config:
        # Executable path từ command line
        executable_path = "/Users/mac/.hidemyacc/browser/marco-browser-140/Marco.app/Contents/MacOS/Marco"
        
        # Kiểm tra executable path có tồn tại không
        import os
        if not os.path.exists(executable_path):
            print(f"⚠️  Warning: Executable path không tồn tại: {executable_path}")
            print("   Đang tìm Marco browser tự động...")
            executable_path = manager._find_marco_browser()
            if executable_path:
                print(f"   Tìm thấy: {executable_path}")
            else:
                print("   Không tìm thấy, sẽ dùng Chrome mặc định")
        
        # Proxy settings từ command line (Base64 encoded)
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
        except Exception as e:
            print(f"❌ Lỗi: Không thể decode proxy credentials: {e}")
            print("   Proxy credentials có thể không đúng format base64")
            import traceback
            traceback.print_exc()
            proxy = None  # Không dùng proxy nếu không decode được
        
        # Extra args từ command line
        # Note: --proxy-server, --proxy-username, --proxy-password không cần vì đã dùng proxy option
        # --hidemyacc-data là arg riêng của HideMyAcc, có thể cần thiết
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
        print(f"  Proxy: {proxy['server']}")
        print()
    else:
        # Tìm Marco browser từ HideMyAcc (giống như JavaScript example)
        executable_path = manager._find_marco_browser()
        proxy = None
        extra_args = None
        
        if executable_path:
            print(f"✓ Tìm thấy Marco browser: {executable_path}")
        else:
            print("⚠️  Không tìm thấy Marco browser, sẽ sử dụng Chrome mặc định")
        print()
    
    # Launch Playwright với profile
    automation = PlaywrightAutomation(headless=False)
    
    try:
        print("Đang launch Playwright với HideMyAcc profile...")
        print("(Sử dụng launch_persistent_context với executable_path - giống JavaScript example)")
        print()
        
        # Tắt proxy nếu flag --no-proxy được set
        if disable_proxy:
            print("⚠️  Proxy đã bị tắt (--no-proxy flag)")
            proxy = None
        
        # Launch với cấu hình từ command line hoặc tự động tìm
        await automation.launch_with_profile(
            profile['user_data_dir'],
            executable_path=executable_path,
            proxy=proxy,
            extra_args=extra_args
        )
        
        print("✓ Đã launch thành công!")
        print()
        print(f"Context: {automation.context}")
        print(f"Page URL hiện tại: {automation.page.url}")
        print()
        
        # Test proxy connection trước (nếu có proxy)
        if proxy and not disable_proxy:
            print("Đang kiểm tra proxy connection...")
            try:
                # Thử navigate đến một trang đơn giản để test proxy
                test_proxy_url = "https://httpbin.org/ip"  # Simple endpoint để test
                print(f"  Test proxy với {test_proxy_url}...")
                await automation.page.goto(test_proxy_url, timeout=10000, wait_until="domcontentloaded")
                print("  ✓ Proxy connection OK!")
                print()
            except Exception as proxy_error:
                print(f"  ⚠️  Proxy test failed: {proxy_error}")
                print("  Có thể proxy không hoạt động, nhưng vẫn sẽ thử navigate...")
                print()
        
        # Test navigate với error handling tốt hơn
        test_url = "https://www.etsy.com"
        print(f"Đang điều hướng đến {test_url}...")
        try:
            # Tăng timeout cho proxy
            original_timeout = automation.timeout
            automation.timeout = 60000  # 60 seconds cho proxy
            await automation.navigate(test_url)
            automation.timeout = original_timeout
            print(f"✓ Đã điều hướng thành công!")
            print(f"Page title: {await automation.page.title()}")
            print(f"Page URL: {automation.page.url}")
            print()
        except Exception as nav_error:
            print(f"❌ Lỗi khi navigate: {nav_error}")
            print()
            print("Có thể do:")
            print("  1. Proxy server không hoạt động hoặc credentials không đúng")
            print("  2. Network connection issue")
            print("  3. Proxy authentication failed")
            print("  4. Proxy server đang bận hoặc timeout")
            print()
            print("Thử test với --no-proxy để kiểm tra:")
            print("  python3 src/app/test_hidemyacc_profile.py --profile 6898af88effa52a76ecbe4ec --use-command-line --no-proxy")
            print()
            # Không raise exception, giữ browser mở để user có thể kiểm tra
        
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
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test launch Playwright với HideMyAcc profile")
    parser.add_argument("--profile", "-p", help="HideMyAcc profile ID/name")
    parser.add_argument("--use-command-line", "-c", action="store_true", 
                       help="Sử dụng cấu hình từ command line (proxy, args, executable path)")
    parser.add_argument("--no-proxy", action="store_true",
                       help="Tắt proxy khi test (để debug)")
    
    args = parser.parse_args()
    
    await test_launch_with_profile(
        args.profile, 
        use_command_line_config=args.use_command_line,
        disable_proxy=args.no_proxy
    )


if __name__ == "__main__":
    asyncio.run(main())
