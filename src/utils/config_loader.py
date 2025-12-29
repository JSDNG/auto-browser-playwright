"""
Utility để đọc config từ config.ini file.
"""
import sys
import configparser
from pathlib import Path
from typing import Optional, Dict, Any


def load_config_ini(config_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Đọc config từ config.ini file.
    
    Args:
        config_path: Đường dẫn đến config.ini (mặc định: config.ini trong project root hoặc cùng thư mục executable)
    
    Returns:
        Dict chứa config đã parse, hoặc None nếu không tìm thấy file
    
    Raises:
        configparser.Error: Nếu có lỗi khi parse config
    """
    if config_path is None:
        # Tìm config.ini trong project root hoặc cùng thư mục với executable
        # Nếu chạy từ executable, tìm trong thư mục chứa executable
        if getattr(sys, 'frozen', False):
            # Chạy từ PyInstaller executable
            base_path = Path(sys.executable).parent
        else:
            # Chạy từ source code
            base_path = Path(__file__).parent.parent.parent
        
        config_path = base_path / "config.ini"
    else:
        config_path = Path(config_path)
    
    # Thử đọc config.ini.example nếu config.ini không tồn tại
    if not config_path.exists():
        example_path = config_path.parent / "config.ini.example"
        if example_path.exists():
            config_path = example_path
        else:
            # Không raise error, trả về None
            return None
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        
        # Parse config thành dict
        result = {
            "search": {
                "keyword": config.get("search", "keyword", fallback="t-shirt"),
                "pages": config.getint("search", "pages", fallback=5),
            },
            "filter": {
                "created_date_months": config.getint("filter", "created_date_months", fallback=2),
            },
            "webhook": {
                "url": config.get("webhook", "url", fallback="https://spyetsy.supover.com/webhook"),
            },
            "api": {
                "host": config.get("api", "host", fallback="0.0.0.0"),
                "port": config.getint("api", "port", fallback=5674),
            },
            "cdp": {
                "port": config.getint("cdp", "port", fallback=9223),
            },
        }
        
        return result
    except (configparser.Error, Exception) as e:
        # Nếu có lỗi khi parse, trả về None để dùng default
        return None


def get_search_config() -> Dict[str, Any]:
    """
    Lấy config cho search (keyword, pages, filter).
    Convenience function để dùng trong code.
    
    Returns:
        Dict với keys: keyword, pages, created_date_months
    """
    config = load_config_ini()
    if config is None:
        # Fallback về default nếu không có config.ini
        return {
            "keyword": "t-shirt",
            "pages": 5,
            "created_date_months": 2,
        }
    
    return {
        "keyword": config["search"]["keyword"],
        "pages": config["search"]["pages"],
        "created_date_months": config["filter"]["created_date_months"],
    }

