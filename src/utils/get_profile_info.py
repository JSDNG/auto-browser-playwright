"""
Utility để lấy thông tin chi tiết của HideMyAcc profile
"""
import os
import json
import sqlite3
import platform
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime
import stat



class ProfileInfoExtractor:
    """Lấy thông tin chi tiết từ HideMyAcc profile"""
    
    def __init__(self):
        self.manager = HideMyAccManager()
    
    def get_profile_info(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy toàn bộ thông tin chi tiết của profile
        
        Args:
            profile_id: ID của profile cần lấy thông tin
            
        Returns:
            Dict chứa tất cả thông tin của profile, hoặc None nếu không tìm thấy
        """
        # Tìm profile cơ bản
        profile = self.manager.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        info = {
            "basic_info": self._get_basic_info(profile),
            "paths": self._get_path_info(profile),
            "preferences": self._get_preferences(profile),
            "databases": self._get_database_info(profile),
            "extensions": self._get_extensions_info(profile),
            "files": self._get_files_info(profile),
            "fingerprint": self._get_fingerprint_info(profile),
            "statistics": self._get_statistics(profile),
        }
        
        return info
    
    def _get_basic_info(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin cơ bản của profile"""
        return {
            "id": profile.get("id"),
            "name": profile.get("name"),
            "path": profile.get("path"),
            "user_data_dir": profile.get("user_data_dir"),
        }
    
    def _get_path_info(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin về các đường dẫn"""
        user_data_dir = Path(profile.get("user_data_dir", ""))
        profile_path = Path(profile.get("path", ""))
        
        paths = {
            "profile_directory": str(profile_path) if profile_path.exists() else None,
            "user_data_directory": str(user_data_dir) if user_data_dir.exists() else None,
            "default_profile": None,
            "cache_directory": None,
            "extensions_directory": None,
        }
        
        # Tìm Default profile
        default_paths = [
            user_data_dir / "Default",
            profile_path / "Default",
            profile_path / "User Data" / "Default",
        ]
        for path in default_paths:
            if path.exists():
                paths["default_profile"] = str(path)
                break
        
        # Tìm cache directory
        cache_paths = [
            user_data_dir / "Default" / "Cache",
            profile_path / "Cache",
        ]
        for path in cache_paths:
            if path.exists():
                paths["cache_directory"] = str(path)
                break
        
        # Tìm extensions directory
        ext_paths = [
            user_data_dir / "Default" / "Extensions",
            profile_path / "Extensions",
        ]
        for path in ext_paths:
            if path.exists():
                paths["extensions_directory"] = str(path)
                break
        
        return paths
    
    def _get_preferences(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin từ Preferences file"""
        user_data_dir = Path(profile.get("user_data_dir", ""))
        prefs = {}
        
        # Tìm Preferences file
        pref_paths = [
            user_data_dir / "Default" / "Preferences",
            user_data_dir / "Preferences",
        ]
        
        pref_file = None
        for path in pref_paths:
            if path.exists() and path.is_file():
                pref_file = path
                break
        
        if not pref_file:
            return {"error": "Preferences file not found"}
        
        try:
            with open(pref_file, 'r', encoding='utf-8') as f:
                prefs_data = json.load(f)
            
            # Lấy các thông tin quan trọng
            prefs = {
                "file_path": str(pref_file),
                "file_size": pref_file.stat().st_size,
                "profile": prefs_data.get("profile", {}),
                "account_info": prefs_data.get("account_info", {}),
                "browser": prefs_data.get("browser", {}),
                "extensions": prefs_data.get("extensions", {}),
                "session": prefs_data.get("session", {}),
                "homepage": prefs_data.get("homepage", ""),
                "homepage_is_newtabpage": prefs_data.get("homepage_is_newtabpage", False),
                "first_run_time": prefs_data.get("first_run_time"),
                "last_active_profiles": prefs_data.get("last_active_profiles", []),
                "profile_info_cache": prefs_data.get("profile_info_cache", {}),
            }
            
            # Lấy thông tin về settings
            if "profile" in prefs_data:
                profile_info = prefs_data["profile"]
                prefs["profile_name"] = profile_info.get("name", "")
                prefs["profile_avatar_index"] = profile_info.get("avatar_index", 0)
                prefs["profile_is_using_default_name"] = profile_info.get("is_using_default_name", True)
            
            # Lấy thông tin về browser settings
            if "browser" in prefs_data:
                browser_info = prefs_data["browser"]
                prefs["has_seen_welcome_page"] = browser_info.get("has_seen_welcome_page", False)
                prefs["show_home_button"] = browser_info.get("show_home_button", False)
            
        except json.JSONDecodeError as e:
            prefs = {"error": f"Failed to parse Preferences: {e}"}
        except Exception as e:
            prefs = {"error": f"Failed to read Preferences: {e}"}
        
        return prefs
    
    def _get_database_info(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin từ các database files"""
        user_data_dir = Path(profile.get("user_data_dir", ""))
        default_path = user_data_dir / "Default"
        
        if not default_path.exists():
            return {"error": "Default profile directory not found"}
        
        databases = {}
        
        # Danh sách các database files quan trọng
        db_files = {
            "Cookies": "cookies",
            "History": "history",
            "Login Data": "login_data",
            "Web Data": "web_data",
            "Top Sites": "top_sites",
            "Shortcuts": "shortcuts",
            "Favicons": "favicons",
            "Local Storage": "local_storage",
        }
        
        for db_name, key in db_files.items():
            db_path = default_path / db_name
            if db_path.exists():
                try:
                    stat_info = db_path.stat()
                    db_info = {
                        "path": str(db_path),
                        "size": stat_info.st_size,
                        "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    }
                    
                    # Thử đọc một số thông tin từ database
                    if db_name == "Cookies":
                        db_info["count"] = self._count_cookies(db_path)
                    elif db_name == "History":
                        db_info["count"] = self._count_history_entries(db_path)
                    elif db_name == "Login Data":
                        db_info["count"] = self._count_logins(db_path)
                    
                    databases[key] = db_info
                except Exception as e:
                    databases[key] = {"error": str(e)}
        
        return databases
    
    def _count_cookies(self, db_path: Path) -> Optional[int]:
        """Đếm số lượng cookies"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cookies")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return None
    
    def _count_history_entries(self, db_path: Path) -> Optional[int]:
        """Đếm số lượng history entries"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM urls")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return None
    
    def _count_logins(self, db_path: Path) -> Optional[int]:
        """Đếm số lượng saved logins"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logins")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return None
    
    def _get_extensions_info(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin về extensions"""
        user_data_dir = Path(profile.get("user_data_dir", ""))
        ext_dir = user_data_dir / "Default" / "Extensions"
        
        if not ext_dir.exists():
            return {"error": "Extensions directory not found", "count": 0}
        
        extensions = {
            "directory": str(ext_dir),
            "extensions": [],
            "count": 0,
        }
        
        try:
            # Liệt kê các extensions
            for ext_id_dir in ext_dir.iterdir():
                if ext_id_dir.is_dir():
                    # Tìm version directories
                    for version_dir in ext_id_dir.iterdir():
                        if version_dir.is_dir():
                            manifest_path = version_dir / "manifest.json"
                            if manifest_path.exists():
                                try:
                                    with open(manifest_path, 'r', encoding='utf-8') as f:
                                        manifest = json.load(f)
                                    
                                    ext_info = {
                                        "id": ext_id_dir.name,
                                        "version": version_dir.name,
                                        "name": manifest.get("name", ""),
                                        "description": manifest.get("description", ""),
                                        "version_number": manifest.get("version", ""),
                                        "permissions": manifest.get("permissions", []),
                                        "path": str(version_dir),
                                    }
                                    extensions["extensions"].append(ext_info)
                                except:
                                    pass
            
            extensions["count"] = len(extensions["extensions"])
        except Exception as e:
            extensions["error"] = str(e)
        
        return extensions
    
    def _get_files_info(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin về các files quan trọng"""
        user_data_dir = Path(profile.get("user_data_dir", ""))
        default_path = user_data_dir / "Default"
        
        if not default_path.exists():
            return {"error": "Default profile directory not found"}
        
        files_info = {
            "important_files": {},
            "total_size_mb": 0,
        }
        
        # Các files quan trọng
        important_files = [
            "Bookmarks",
            "Bookmarks.bak",
            "Current Session",
            "Current Tabs",
            "Last Session",
            "Last Tabs",
            "Preferences",
            "Secure Preferences",
            "State",
            "Sync Data",
        ]
        
        total_size = 0
        for filename in important_files:
            file_path = default_path / filename
            if file_path.exists():
                try:
                    stat_info = file_path.stat()
                    size = stat_info.st_size
                    total_size += size
                    files_info["important_files"][filename] = {
                        "path": str(file_path),
                        "size": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    }
                except:
                    pass
        
        files_info["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        return files_info
    
    def _get_fingerprint_info(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thông tin về fingerprint settings từ HideMyAcc"""
        profile_path = Path(profile.get("path", ""))
        
        fingerprint = {
            "config_files": [],
            "settings": {},
        }
        
        # Tìm các file config của HideMyAcc
        config_paths = [
            profile_path / "config.json",
            profile_path / "settings.json",
            profile_path / "fingerprint.json",
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    fingerprint["config_files"].append(str(config_path))
                    fingerprint["settings"].update(config_data)
                except:
                    pass
        
        # Tìm trong Preferences về fingerprint
        user_data_dir = Path(profile.get("user_data_dir", ""))
        pref_path = user_data_dir / "Default" / "Preferences"
        if pref_path.exists():
            try:
                with open(pref_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                # Tìm các settings liên quan đến fingerprint
                if "profile" in prefs:
                    profile_info = prefs["profile"]
                    fingerprint["profile_name"] = profile_info.get("name", "")
            except:
                pass
        else:
            print("Preferences file not found")
            return fingerprint
        
        return fingerprint
    
    def _get_statistics(self, profile: Dict[str, str]) -> Dict[str, Any]:
        """Lấy thống kê tổng quan"""
        user_data_dir = Path(profile.get("user_data_dir", ""))
        
        stats = {
            "total_size_mb": 0,
            "file_count": 0,
            "directory_count": 0,
            "oldest_file": None,
            "newest_file": None,
        }
        
        if not user_data_dir.exists():
            return stats
        
        try:
            total_size = 0
            file_count = 0
            dir_count = 0
            oldest_time = None
            newest_time = None
            
            for root, dirs, files in os.walk(user_data_dir):
                dir_count += len(dirs)
                for file in files:
                    file_path = Path(root) / file
                    try:
                        stat_info = file_path.stat()
                        total_size += stat_info.st_size
                        file_count += 1
                        
                        mtime = stat_info.st_mtime
                        if oldest_time is None or mtime < oldest_time:
                            oldest_time = mtime
                        if newest_time is None or mtime > newest_time:
                            newest_time = mtime
                    except:
                        pass
            
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            stats["file_count"] = file_count
            stats["directory_count"] = dir_count
            if oldest_time:
                stats["oldest_file"] = datetime.fromtimestamp(oldest_time).isoformat()
            if newest_time:
                stats["newest_file"] = datetime.fromtimestamp(newest_time).isoformat()
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def print_profile_info(self, profile_id: str, output_format: str = "pretty") -> None:
        """
        In thông tin profile ra console
        
        Args:
            profile_id: ID của profile
            output_format: "pretty" (đẹp) hoặc "json" (JSON format)
        """
        info = self.get_profile_info(profile_id)
        
        if not info:
            print(f"❌ Không tìm thấy profile: {profile_id}")
            return
        
        if output_format == "json":
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            self._print_pretty(info)
    
    def _print_pretty(self, info: Dict[str, Any]) -> None:
        """In thông tin dạng đẹp"""
        print("=" * 80)
        print("THÔNG TIN CHI TIẾT PROFILE HIDEMYACC")
        print("=" * 80)
        print()
        
        # Basic Info
        if "basic_info" in info:
            basic = info["basic_info"]
            print("📋 THÔNG TIN CƠ BẢN")
            print("-" * 80)
            print(f"  ID: {basic.get('id')}")
            print(f"  Name: {basic.get('name')}")
            print(f"  Path: {basic.get('path')}")
            print(f"  User Data Dir: {basic.get('user_data_dir')}")
            print()
        
        # Paths
        if "paths" in info:
            paths = info["paths"]
            print("📁 ĐƯỜNG DẪN")
            print("-" * 80)
            for key, value in paths.items():
                if value:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            print()
        
        # Statistics
        if "statistics" in info:
            stats = info["statistics"]
            print("📊 THỐNG KÊ")
            print("-" * 80)
            print(f"  Tổng dung lượng: {stats.get('total_size_mb', 0)} MB")
            print(f"  Số lượng files: {stats.get('file_count', 0):,}")
            print(f"  Số lượng thư mục: {stats.get('directory_count', 0):,}")
            if stats.get('oldest_file'):
                print(f"  File cũ nhất: {stats.get('oldest_file')}")
            if stats.get('newest_file'):
                print(f"  File mới nhất: {stats.get('newest_file')}")
            print()
        
        # Preferences
        if "preferences" in info:
            prefs = info["preferences"]
            if "error" not in prefs:
                print("⚙️  PREFERENCES")
                print("-" * 80)
                if prefs.get("file_path"):
                    print(f"  File: {prefs.get('file_path')}")
                    print(f"  Size: {prefs.get('file_size', 0):,} bytes")
                if prefs.get("profile_name"):
                    print(f"  Profile Name: {prefs.get('profile_name')}")
                if prefs.get("homepage"):
                    print(f"  Homepage: {prefs.get('homepage')}")
                print()
        
        # Databases
        if "databases" in info:
            dbs = info["databases"]
            if "error" not in dbs:
                print("💾 DATABASES")
                print("-" * 80)
                for key, db_info in dbs.items():
                    if isinstance(db_info, dict) and "error" not in db_info:
                        print(f"  {key.replace('_', ' ').title()}:")
                        print(f"    Path: {db_info.get('path')}")
                        print(f"    Size: {db_info.get('size_mb', 0)} MB")
                        if db_info.get('count') is not None:
                            print(f"    Count: {db_info.get('count'):,}")
                        print(f"    Modified: {db_info.get('modified')}")
                print()
        
        # Extensions
        if "extensions" in info:
            exts = info["extensions"]
            if "error" not in exts:
                print("🔌 EXTENSIONS")
                print("-" * 80)
                print(f"  Số lượng: {exts.get('count', 0)}")
                for ext in exts.get("extensions", [])[:10]:  # Hiển thị tối đa 10
                    print(f"    - {ext.get('name')} (v{ext.get('version_number')})")
                if exts.get('count', 0) > 10:
                    print(f"    ... và {exts.get('count', 0) - 10} extensions khác")
                print()
        
        # Files
        if "files" in info:
            files = info["files"]
            if "error" not in files:
                print("📄 FILES QUAN TRỌNG")
                print("-" * 80)
                for filename, file_info in files.get("important_files", {}).items():
                    print(f"  {filename}: {file_info.get('size_mb', 0)} MB")
                print(f"  Tổng size: {files.get('total_size_mb', 0)} MB")
                print()
        
        # Fingerprint
        if "fingerprint" in info:
            fp = info["fingerprint"]
            if fp.get("config_files"):
                print("🔒 FINGERPRINT SETTINGS")
                print("-" * 80)
                for config_file in fp.get("config_files", []):
                    print(f"  Config: {config_file}")
                if fp.get("settings"):
                    print(f"  Settings keys: {', '.join(fp.get('settings', {}).keys())}")
                print()
        
        print("=" * 80)


def main():
    """CLI để lấy thông tin profile"""
    import sys
    
    if len(sys.argv) < 2:
        print("❌ Thiếu tham số PROFILE_ID")
        print()
        print("Cú pháp:")
        print("  python3 -m src.utils.get_profile_info [PROFILE_ID] [--json]")
        print()
        print("Ví dụ:")
        print("  python3 -m src.utils.get_profile_info profile1")
        print("  python3 -m src.utils.get_profile_info profile1 --json")
        print()
        print("Để xem danh sách profiles:")
        sys.exit(1)
    
    profile_id = sys.argv[1]
    output_format = "json" if "--json" in sys.argv else "pretty"
    
    extractor = ProfileInfoExtractor()
    extractor.print_profile_info(profile_id, output_format)


if __name__ == "__main__":
    main()