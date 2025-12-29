"""
Utility để kiểm tra và khởi động Chrome với CDP.
"""
import os
import subprocess
import platform
import urllib.request
import json
from pathlib import Path
from typing import Optional


def check_cdp_running(port: int = 9223) -> bool:
    """
    Kiểm tra xem Chrome CDP có đang chạy tại port không.
    
    Args:
        port: CDP port (mặc định: 9223)
    
    Returns:
        True nếu CDP đang chạy, False nếu không
    """
    try:
        url = f"http://localhost:{port}/json"
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read())
            return len(data) > 0  # Có ít nhất 1 tab
    except Exception:
        return False


def find_chrome_executable() -> Optional[str]:
    """
    Tìm đường dẫn đến Chrome executable.
    
    Returns:
        Đường dẫn đến Chrome, hoặc None nếu không tìm thấy
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows paths
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
        ]
        for path in possible_paths:
            expanded = Path(path).expanduser()
            if expanded.exists():
                return str(expanded)
    
    elif system == "Darwin":  # macOS
        chrome_path = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if chrome_path.exists():
            return str(chrome_path)
    
    elif system == "Linux":
        # Linux paths
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
        for path in possible_paths:
            if Path(path).exists():
                return path
    
    return None


def get_default_user_data_dir() -> str:
    """
    Lấy đường dẫn mặc định cho Chrome user data directory.
    Dùng temp directory để tránh bị block.
    
    Returns:
        Đường dẫn đến user data directory
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: C:\temp\chrome-cdp-profile
        user_data_dir = Path("C:\\temp\\chrome-cdp-profile")
    elif system == "Darwin":  # macOS
        # macOS: /tmp/chrome-cdp-profile
        user_data_dir = Path("/tmp/chrome-cdp-profile")
    else:  # Linux
        # Linux: /tmp/chrome-cdp-profile
        user_data_dir = Path("/tmp/chrome-cdp-profile")
    
    # Tạo thư mục nếu chưa có
    user_data_dir.mkdir(parents=True, exist_ok=True)
    return str(user_data_dir)


def launch_chrome_with_cdp(port: int = 9223, user_data_dir: Optional[str] = None) -> subprocess.Popen:
    """
    Khởi động Chrome với CDP port và user-data-dir để tránh bị block.
    
    Args:
        port: CDP port (mặc định: 9223)
        user_data_dir: User data directory (mặc định: dùng profile path cố định)
    
    Returns:
        Process object của Chrome
    
    Raises:
        FileNotFoundError: Nếu không tìm thấy Chrome executable
        subprocess.SubprocessError: Nếu không thể khởi động Chrome
    """
    chrome_path = find_chrome_executable()
    if not chrome_path:
        raise FileNotFoundError("Không tìm thấy Chrome. Vui lòng cài đặt Google Chrome.")
    
    # Dùng profile path cố định thay vì temp để tránh bị block
    if user_data_dir is None:
        user_data_dir = get_default_user_data_dir()
    
    # Đảm bảo thư mục tồn tại
    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    
    # Chrome arguments - thêm các flag để tránh bị phát hiện automation
    args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--disable-dev-shm-usage",
        "--no-sandbox",  # Cần thiết trong một số môi trường
    ]
    
    # Khởi động Chrome
    process = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True  # Tách khỏi parent process
    )
    
    return process

