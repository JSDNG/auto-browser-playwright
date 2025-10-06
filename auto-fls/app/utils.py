"""
Utility functions for Auto Flash Sale
"""

import json
import time
import hashlib
import random
import string
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

def generate_session_id(profile_id: str) -> str:
    """Generate unique session ID"""
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"session_{profile_id}_{timestamp}_{random_str}"

def generate_request_id() -> str:
    """Generate unique request ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

def hash_profile_id(profile_id: str) -> str:
    """Create hash of profile ID for logging (privacy)"""
    return hashlib.md5(profile_id.encode()).hexdigest()[:8]

def format_timestamp(timestamp: Optional[float] = None) -> str:
    """Format timestamp to ISO string"""
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).isoformat()

def parse_iso_timestamp(iso_string: str) -> float:
    """Parse ISO timestamp to float"""
    return datetime.fromisoformat(iso_string.replace('Z', '+00:00')).timestamp()

def calculate_uptime(start_time: float) -> str:
    """Calculate uptime string from start time"""
    uptime_seconds = time.time() - start_time
    
    if uptime_seconds < 60:
        return f"{int(uptime_seconds)}s"
    elif uptime_seconds < 3600:
        minutes = int(uptime_seconds // 60)
        seconds = int(uptime_seconds % 60)
        return f"{minutes}m {seconds}s"
    else:
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def validate_profile_id(profile_id: str) -> bool:
    """Validate profile ID format"""
    if not profile_id or not isinstance(profile_id, str):
        return False
    
    # HMA profile IDs are typically 24 character hex strings
    if len(profile_id) != 24:
        return False
    
    try:
        int(profile_id, 16)
        return True
    except ValueError:
        return False

def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive data from logs"""
    sensitive_keys = ['api_key', 'password', 'token', 'secret', 'auth']
    sanitized = data.copy()
    
    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = '***REDACTED***'
    
    return sanitized

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            time.sleep(delay)

def format_error_response(error: str, error_code: str = "UNKNOWN_ERROR") -> Dict[str, Any]:
    """Format error response"""
    return {
        "success": False,
        "error": error,
        "error_code": error_code,
        "timestamp": format_timestamp()
    }

def format_success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Format success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": format_timestamp()
    }

def extract_port_from_ws_url(ws_url: str) -> Optional[int]:
    """Extract port number from WebSocket URL"""
    try:
        # ws://127.0.0.1:36807/devtools/browser/...
        parts = ws_url.split(':')
        if len(parts) >= 3:
            port_part = parts[2].split('/')[0]
            return int(port_part)
    except (ValueError, IndexError):
        pass
    return None

def build_webhook_payload(profile_id: str, status: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Build webhook payload for external services"""
    return {
        "profile_id": profile_id,
        "status": status,
        "data": data,
        "timestamp": format_timestamp(),
        "source": "auto-fls"
    }

def validate_webhook_url(url: str) -> bool:
    """Validate webhook URL format"""
    if not url:
        return False
    
    return url.startswith(('http://', 'https://'))

def create_profile_summary(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create profile summary for logging"""
    return {
        "profile_id_hash": hash_profile_id(profile_data.get('profile_id', '')),
        "port": profile_data.get('port'),
        "user_agent": profile_data.get('userAgent', '')[:50] + '...' if len(profile_data.get('userAgent', '')) > 50 else profile_data.get('userAgent', ''),
        "success": profile_data.get('success', False)
    }

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge configuration dictionaries"""
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged

def get_random_user_agent() -> str:
    """Get random user agent string"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
    ]
    return random.choice(user_agents)

def calculate_uptime(start_time: float) -> str:
    """Calculate uptime string from start time"""
    uptime_seconds = time.time() - start_time
    
    if uptime_seconds < 60:
        return f"{int(uptime_seconds)}s"
    elif uptime_seconds < 3600:
        minutes = int(uptime_seconds // 60)
        seconds = int(uptime_seconds % 60)
        return f"{minutes}m {seconds}s"
    else:
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
