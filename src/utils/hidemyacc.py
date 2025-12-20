"""
Utility để tìm và quản lý HideMyAcc profiles
"""
import os
import json
import platform
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional
import sqlite3


class HideMyAccManager:
    """Quản lý HideMyAcc profiles"""
    
    # Các vị trí có thể chứa HideMyAcc profiles
    POSSIBLE_PATHS = {
        "darwin": [  # macOS
            Path.home() / ".hidemyacc",  # HideMyAcc-3 hidden folder
            Path.home() / "Library" / "Application Support" / "hidemyacc-3",
            Path.home() / "Library" / "Application Support" / "HideMyAcc",
            Path.home() / "Documents" / "HideMyAcc",
            Path("/Applications/HideMyAcc.app/Contents/Resources"),
        ],
        "linux": [
            Path.home() / ".config" / "HideMyAcc",
            Path.home() / "Documents" / "HideMyAcc",
        ],
        "windows": [
            Path.home() / "Documents" / "HideMyAcc",
            Path(os.environ.get("APPDATA", "")) / "HideMyAcc",
            Path(os.environ.get("LOCALAPPDATA", "")) / "HideMyAcc",
        ]
    }
    
    def __init__(self):
        self.system = platform.system().lower()
        self.base_path = self._find_hidemyacc_path()
    
    def _find_hidemyacc_path(self) -> Optional[Path]:
        """Tìm đường dẫn chính của HideMyAcc"""
        possible_paths = self.POSSIBLE_PATHS.get(self.system, [])
        
        for path in possible_paths:
            if path.exists():
                # Kiểm tra xem có thư mục Profiles hoặc profiles không
                profiles_path = path / "Profiles"
                profiles_path_lower = path / "profiles"
                if profiles_path.exists() or profiles_path_lower.exists():
                    return path
                # Hoặc có thể là cấu trúc khác
                if (path / "data").exists():
                    return path
                # Nếu là .hidemyacc và có thư mục profiles hoặc browser, cũng hợp lệ
                if path.name == ".hidemyacc" and ((path / "profiles").exists() or (path / "browser").exists()):
                    return path
        
        return None
    
    def find_profiles(self) -> List[Dict[str, str]]:
        """
        Tìm tất cả các profile của HideMyAcc
        Returns: List of dict với thông tin profile
        """
        if not self.base_path:
            return []
        
        profiles = []
        seen_profile_ids = set()  # Để tránh duplicate nếu profile tồn tại ở cả hai nơi
        
        # Thử các cấu trúc thư mục phổ biến
        # Ưu tiên lowercase "profiles" trước (thường là active profiles)
        possible_profile_dirs = [
            self.base_path / "profiles",  # Ưu tiên lowercase
            self.base_path / "Profiles",  # Uppercase
            self.base_path / "data" / "profiles",
        ]
        
        for profiles_dir in possible_profile_dirs:
            if profiles_dir.exists() and profiles_dir.is_dir():
                # Quét các thư mục trong Profiles
                for item in profiles_dir.iterdir():
                    if item.is_dir():
                        # Kiểm tra xem có phải là profile directory không
                        profile_path = self._get_profile_user_data(item)
                        if profile_path:
                            profile_id = item.name
                            # Chỉ thêm nếu chưa thấy (ưu tiên profile đầu tiên tìm thấy)
                            if profile_id not in seen_profile_ids:
                                seen_profile_ids.add(profile_id)
                                profiles.append({
                                    "id": profile_id,
                                    "name": profile_id,
                                    "path": str(item),
                                    "user_data_dir": str(profile_path),
                                })
        
        return profiles
    
    def _get_profile_user_data(self, profile_dir: Path) -> Optional[Path]:
        """
        Tìm user data directory trong profile
        HideMyAcc có thể lưu profile ở các cấu trúc khác nhau
        
        Lưu ý: user_data_dir là thư mục CHỨA "Default" folder, không phải chính "Default" folder
        Ví dụ: /Users/mac/.hidemyacc/profiles/hma_xxx/ (chứa Default/)
        """
        # Kiểm tra nếu profile_dir có chứa "Default" subdirectory
        # Đây là cấu trúc phổ biến của HideMyAcc
        default_path = profile_dir / "Default"
        if default_path.exists() and default_path.is_dir():
            # Kiểm tra xem Default có chứa Chrome profile files không
            if (default_path / "Preferences").exists() or (default_path / "Local Storage").exists():
                # user_data_dir là parent (profile_dir), không phải Default folder
                return profile_dir
        
        # Các cấu trúc khác có thể:
        possible_structures = [
            profile_dir / "User Data",
            profile_dir / "user_data",
            profile_dir,  # Có thể chính thư mục đó
        ]
        
        for path in possible_structures:
            if path.exists():
                # Kiểm tra có file Chrome profile không
                if (path / "Default").exists() or (path / "Preferences").exists():
                    return path
                if path.is_dir() and any(path.glob("*.db")):  # Có database file
                    return path
        
        return None
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, str]]:
        """
        Lấy thông tin profile theo ID
        
        Hỗ trợ các format:
        - Full name: "hma_6898af88effa52a76ecbe4ec"
        - ID only: "6898af88effa52a76ecbe4ec"
        - Name match: exact match với name/id
        """
        profiles = self.find_profiles()
        
        # Normalize profile_id - remove "hma_" prefix nếu có
        normalized_id = profile_id
        if profile_id.startswith("hma_"):
            normalized_id = profile_id[4:]  # Remove "hma_" prefix
        
        for profile in profiles:
            profile_name = profile["id"] or profile["name"]
            # Check exact match
            if profile["id"] == profile_id or profile["name"] == profile_id:
                return profile
            # Check normalized match (without hma_ prefix)
            if profile_name.startswith("hma_"):
                profile_id_part = profile_name[4:]
                if profile_id_part == normalized_id or profile_id_part == profile_id:
                    return profile
            # Check if profile name ends with the ID
            if profile_name.endswith(normalized_id) or profile_name.endswith(profile_id):
                return profile
        
        return None
    
    def list_profiles(self) -> None:
        """In danh sách profiles"""
        profiles = self.find_profiles()
        if not profiles:
            print("❌ Không tìm thấy HideMyAcc profiles")
            if not self.base_path:
                print(f"   HideMyAcc có thể không được cài đặt hoặc ở vị trí khác")
                print(f"   Đã tìm tại: {self.POSSIBLE_PATHS.get(self.system, [])}")
            return
        
        print(f"✓ Tìm thấy {len(profiles)} HideMyAcc profile(s):")
        print()
        for i, profile in enumerate(profiles, 1):
            print(f"[{i}] {profile['name']}")
            print(f"    ID: {profile['id']}")
            print(f"    Path: {profile['path']}")
            print(f"    User Data: {profile['user_data_dir']}")
            print()
    
    def check_cdp_running(self, port: int = 9223) -> bool:
        """Kiểm tra xem CDP có đang chạy tại port không"""
        try:
            url = f"http://localhost:{port}/json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except:
            return False
    
    def launch_chrome_with_profile(self, profile_id: str, port: int = 9223) -> bool:
        """
        Tự động khởi động Chrome với HideMyAcc profile + CDP
        
        Returns:
            True nếu khởi động thành công, False nếu thất bại
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            print(f"❌ Không tìm thấy profile: {profile_id}")
            return False
        
        # Kiểm tra CDP đã chạy chưa
        if self.check_cdp_running(port):
            print(f"✓ Chrome đã đang chạy với CDP tại port {port}")
            return True
        
        profile_path = profile['user_data_dir']
        
        print(f"Đang khởi động Chrome với HideMyAcc profile: {profile_id}")
        print(f"Profile path: {profile_path}")
        print(f"CDP port: {port}")
        
        # Xây dựng lệnh Chrome
        chrome_cmd = self._get_chrome_command(profile_path, port)
        if not chrome_cmd:
            return False
        
        try:
            # Khởi động Chrome
            process = subprocess.Popen(
                chrome_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Chờ Chrome khởi động
            print("Đang đợi Chrome khởi động...")
            for _ in range(10):  # Đợi tối đa 10 giây
                time.sleep(1)
                if self.check_cdp_running(port):
                    print(f"✓ Chrome đã khởi động thành công với CDP tại port {port}")
                    print(f"  PID: {process.pid}")
                    return True
            
            print("⚠️  Chrome đã khởi động nhưng CDP có thể chưa sẵn sàng")
            return False
            
        except Exception as e:
            print(f"❌ Lỗi khi khởi động Chrome: {e}")
            return False
    
    def _find_marco_browser(self) -> Optional[str]:
        """Tìm Marco browser từ HideMyAcc (HideMyAcc sử dụng Marco, không phải Chrome chính)"""
        if platform.system().lower() != "darwin":
            return None
        
        # Tìm phiên bản Marco mới nhất
        home = Path.home()
        marco_browser_dir = home / ".hidemyacc" / "browser"
        
        if not marco_browser_dir.exists():
            return None
        
        # Tìm tất cả các thư mục marco-browser-*
        marco_dirs = sorted(
            [d for d in marco_browser_dir.iterdir() if d.is_dir() and d.name.startswith("marco-browser-")],
            key=lambda x: x.name,
            reverse=True
        )
        
        # Thử từ phiên bản mới nhất
        for marco_dir in marco_dirs:
            marco_path = marco_dir / "Marco.app" / "Contents" / "MacOS" / "Marco"
            if marco_path.exists() and marco_path.is_file():
                return str(marco_path)
        
        return None
    
    def _get_chrome_command(self, profile_path: str, port: int) -> Optional[List[str]]:
        """Lấy lệnh Chrome phù hợp với hệ điều hành"""
        system = platform.system().lower()
        
        chrome_args = [
            "--remote-debugging-port", str(port),
            "--user-data-dir", profile_path,
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ]
        
        if system == "darwin":  # macOS
            # Ưu tiên tìm Marco browser từ HideMyAcc
            marco_path = self._find_marco_browser()
            if marco_path and os.path.exists(marco_path):
                print(f"✓ Sử dụng Marco browser từ HideMyAcc: {marco_path}")
                return [marco_path] + chrome_args
            
            # Fallback về Chrome chính nếu không tìm thấy Marco
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_path):
                print("⚠️  Không tìm thấy Marco browser, sử dụng Chrome chính")
                return [chrome_path] + chrome_args
            
            print("❌ Không tìm thấy Chrome hoặc Marco browser")
            return None
            
        elif system == "linux":
            # Thử các đường dẫn phổ biến
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return [path] + chrome_args
            print("❌ Không tìm thấy Chrome/Chromium")
            return None
            
        elif system == "windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return [path] + chrome_args
            print("❌ Không tìm thấy Chrome")
            return None
        
        return None


def main():
    """CLI để liệt kê profiles"""
    manager = HideMyAccManager()
    manager.list_profiles()


if __name__ == "__main__":
    main()