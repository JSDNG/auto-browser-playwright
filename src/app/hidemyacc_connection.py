r"""
Kết nối Playwright với HideMyAcc profile qua CDP

Tính năng tự động:
- ✅ Tự động tìm HideMyAcc profiles
- ✅ Tự động khởi động Chrome với profile + CDP (nếu chưa chạy)
- ✅ Tự động kết nối Playwright

Hướng dẫn sử dụng:
1. Liệt kê HideMyAcc profiles có sẵn (tùy chọn):
   python3 -m src.utils.hidemyacc

2. Chạy script - Code sẽ tự động làm mọi thứ:
   python3 src/app/hidemyacc_connection.py --profile profile_name

Hoặc nếu Chrome đã chạy sẵn:
   python3 src/app/hidemyacc_connection.py --profile profile_name --no-auto-launch
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.automation import PlaywrightAutomation
from src.utils.hidemyacc import HideMyAccManager


async def connect_to_hidemyacc_profile(profile_id: str = None, cdp_port: int = 9223, auto_launch: bool = True):
    """
    Kết nối với HideMyAcc profile qua CDP
    
    Args:
        profile_id: ID của HideMyAcc profile (None để tự động chọn profile đầu tiên)
        cdp_port: Port cho CDP (mặc định 9223)
        auto_launch: Tự động khởi động Chrome nếu chưa chạy (mặc định True)
    """
    
    print("=" * 60)
    print("Kết nối Playwright với HideMyAcc profile qua CDP")
    print("=" * 60)
    print()
    
    # Tìm profiles
    manager = HideMyAccManager()
    profiles = manager.find_profiles()
    
    if not profiles:
        print("❌ Không tìm thấy HideMyAcc profiles!")
        print()
        print("Kiểm tra:")
        print("1. HideMyAcc đã được cài đặt chưa?")
        print("2. Đã tạo profiles trong HideMyAcc chưa?")
        return None
    
    # Chọn profile
    if not profile_id:
        print(f"Tìm thấy {len(profiles)} profile(s):")
        print()
        for i, profile in enumerate(profiles, 1):
            print(f"  [{i}] {profile['name']}")
        print()
        
        # Nếu có nhiều profile, yêu cầu chọn
        if len(profiles) > 1:
            print("⚠️  Cần chỉ định profile_id khi gọi hàm")
            print("   Ví dụ: connect_to_hidemyacc_profile('profile_name', 9223)")
            print()
            print("Hoặc chạy với --profile:")
            print("  python3 src/app/hidemyacc_connection.py --profile profile_name")
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
    
    # Kiểm tra CDP đã chạy chưa
    if not manager.check_cdp_running(cdp_port):
        if auto_launch:
            print("CDP chưa chạy. Đang tự động khởi động Chrome với HideMyAcc profile...")
            print()
            success = manager.launch_chrome_with_profile(profile_id, cdp_port)
            if not success:
                print()
                print("❌ Không thể khởi động Chrome tự động")
                print("Hãy thử khởi động thủ công:")
                print(f"  ./scripts/start_chrome_with_hidemyacc.sh {cdp_port} {profile_id}")
                return None
            print()
        else:
            print(f"❌ CDP chưa chạy tại port {cdp_port}")
            print()
            print("Có 2 cách để khởi động:")
            print(f"1. Tự động: Đặt auto_launch=True (mặc định)")
            print(f"2. Thủ công: ./scripts/start_chrome_with_hidemyacc.sh {cdp_port} {profile_id}")
            return None
    else:
        print(f"✓ CDP đang chạy tại port {cdp_port}")
        print()
    
    automation = PlaywrightAutomation()
    
    try:
        # Kết nối với Chrome đang chạy qua CDP
        cdp_endpoint = f"http://localhost:{cdp_port}"
        print(f"Đang kết nối với Chrome qua CDP tại {cdp_endpoint}...")
        await automation.connect_over_cdp(cdp_endpoint)
        print("✓ Đã kết nối thành công!")
        print()
        
        # Hiển thị thông tin
        print(f"Browser: {automation.browser}")
        print(f"Context: {automation.context}")
        print(f"Page URL hiện tại: {automation.page.url}")
        print()
        
        return automation
        
    except Exception as e:
        print(f"❌ Lỗi khi kết nối: {e}")
        print()
        print("Kiểm tra:")
        print(f"1. Chrome đã khởi động với HideMyAcc profile + CDP port {cdp_port} chưa?")
        print(f"2. Thử truy cập http://localhost:{cdp_port}/json để xác nhận CDP đang chạy")
        return None


async def main():
    """Main function với interactive selection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kết nối Playwright với HideMyAcc profile qua CDP")
    parser.add_argument("--profile", "-p", help="HideMyAcc profile ID/name")
    parser.add_argument("--port", type=int, default=9223, help="CDP port (default: 9223)")
    parser.add_argument("--no-auto-launch", action="store_true", help="Không tự động khởi động Chrome")
    
    args = parser.parse_args()
    
    automation = await connect_to_hidemyacc_profile(
        args.profile, 
        args.port, 
        auto_launch=not args.no_auto_launch
    )
    
    if automation:
        try:
            url = "https://www.etsy.com/listing/1382196280/custom-boat-tote-bag-canvas-tote-bag?ref=hp_editors_picks_primary-3&logging_key=1e4a37ab2e6157035f7997723d8d8b03643ba35a%3A1382196280"
            print(f"Đang điều hướng đến {url}...")
            await automation.navigate(url)
            print(f"✓ Đã điều hướng thành công!")
            print(f"Page title: {await automation.page.title()}")
            print()
            
            # Chờ một chút để xem kết quả
            print("Đang chờ 5 giây để bạn xem kết quả...")
            await asyncio.sleep(5)
            
            # Lưu ý: KHÔNG đóng browser vì đây là Chrome của bạn
            print()
            print("⚠️  Lưu ý: Browser sẽ KHÔNG bị đóng vì đây là HideMyAcc profile")
            print("   Chỉ detach khỏi Playwright...")
            await automation.detach()
            print("✓ Đã detach thành công!")
        except Exception as e:
            print(f"❌ Lỗi trong quá trình automation: {e}")


if __name__ == "__main__":
    asyncio.run(main())