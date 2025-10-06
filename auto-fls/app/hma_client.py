"""
HideMyAcc API Client
Handles all communication with HideMyAcc API
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from loguru import logger
from .config import Config

class HMAClient:
    """HideMyAcc API Client"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.HMA_API_BASE
        self.api_key = config.HMA_API_KEY
        self.session = requests.Session()
        
        # Set default headers
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to HMA API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"HMA API {method} {url}")
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            logger.info(f"HMA API Response: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 402:
                raise Exception("HMA License expired or payment required")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise Exception(f"Bad Request: {error_data.get('errors', 'Unknown error')}")
            else:
                response.raise_for_status()
                
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to HMA server. Please check if HMA is running.")
        except requests.exceptions.Timeout:
            raise Exception("HMA API request timeout")
        except Exception as e:
            logger.error(f"HMA API Error: {e}")
            raise
    
    def start_profile(self, profile_id: str, open_tabs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Start a HideMyAcc profile"""
        endpoint = f"/profiles/start/{profile_id}"
        
        payload = {}
        if open_tabs:
            payload['open_tabs'] = open_tabs
        
        return self._make_request('POST', endpoint, json=payload)
    
    def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        """Stop a HideMyAcc profile"""
        endpoint = f"/profiles/stop/{profile_id}"
        return self._make_request('POST', endpoint)
    
    def get_profile_status(self, profile_id: str) -> Dict[str, Any]:
        """Get profile status"""
        endpoint = f"/profiles/{profile_id}/status"
        return self._make_request('GET', endpoint)
    
    def list_profiles(self) -> Dict[str, Any]:
        """List all profiles"""
        endpoint = "/profiles"
        return self._make_request('GET', endpoint)
    
    def get_profile_info(self, profile_id: str) -> Dict[str, Any]:
        """Get detailed profile information"""
        endpoint = f"/profiles/{profile_id}"
        return self._make_request('GET', endpoint)
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new profile"""
        endpoint = "/profiles"
        return self._make_request('POST', endpoint, json=profile_data)
    
    def update_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update profile settings"""
        endpoint = f"/profiles/{profile_id}"
        return self._make_request('PUT', endpoint, json=profile_data)
    
    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        """Delete a profile"""
        endpoint = f"/profiles/{profile_id}"
        return self._make_request('DELETE', endpoint)
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get HMA server status"""
        endpoint = "/status"
        return self._make_request('GET', endpoint)
    
    def health_check(self) -> bool:
        """Check if HMA server is healthy"""
        try:
            self.get_server_status()
            return True
        except Exception:
            return False
    
    def get_default_profile_id(self) -> str:
        """Get default profile ID from config"""
        return self.config.DEFAULT_PROFILE_ID
    
    def get_backup_profile_id(self) -> str:
        """Get backup profile ID from config"""
        return self.config.BACKUP_PROFILE_ID
    
    def start_default_profile(self, open_tabs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Start default profile"""
        profile_id = self.get_default_profile_id()
        return self.start_profile(profile_id, open_tabs)
    
    def start_backup_profile(self, open_tabs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Start backup profile if default fails"""
        profile_id = self.get_backup_profile_id()
        return self.start_profile(profile_id, open_tabs)

class ProfileManager:
    """Profile management utilities"""
    
    def __init__(self, hma_client: HMAClient):
        self.hma_client = hma_client
        self.active_profiles: Dict[str, Dict[str, Any]] = {}
    
    def start_profile_with_retry(self, profile_id: str, max_retries: int = 3, 
                                open_tabs: Optional[List[str]] = None, 
                                use_backup: bool = True) -> Dict[str, Any]:
        """Start profile with retry logic and backup profile support"""
        for attempt in range(max_retries):
            try:
                result = self.hma_client.start_profile(profile_id, open_tabs)
                
                if result.get('code') == 1 and result.get('data', {}).get('success'):
                    # Store active profile info
                    self.active_profiles[profile_id] = {
                        'started_at': time.time(),
                        'port': result['data'].get('port'),
                        'ws_url': result['data'].get('wsUrl'),
                        'user_agent': result['data'].get('userAgent'),
                        'open_tabs': open_tabs or []
                    }
                    
                    logger.info(f"Profile {profile_id} started successfully on port {result['data'].get('port')}")
                    return result
                else:
                    raise Exception(f"Profile start failed: {result}")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # Try backup profile if enabled and this is the default profile
                    if use_backup and profile_id == self.hma_client.get_default_profile_id():
                        logger.info("Trying backup profile...")
                        return self.start_backup_profile_with_retry(open_tabs)
                    raise
    
    def stop_profile_safe(self, profile_id: str) -> bool:
        """Safely stop profile"""
        try:
            self.hma_client.stop_profile(profile_id)
            if profile_id in self.active_profiles:
                del self.active_profiles[profile_id]
            logger.info(f"Profile {profile_id} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop profile {profile_id}: {e}")
            return False
    
    def get_active_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all active profiles"""
        return self.active_profiles.copy()
    
    def start_backup_profile_with_retry(self, open_tabs: Optional[List[str]] = None, 
                                       max_retries: int = 3) -> Dict[str, Any]:
        """Start backup profile with retry logic"""
        backup_profile_id = self.hma_client.get_backup_profile_id()
        return self.start_profile_with_retry(backup_profile_id, max_retries, open_tabs, use_backup=False)
    
    def start_default_profile_with_retry(self, open_tabs: Optional[List[str]] = None, 
                                        max_retries: int = 3) -> Dict[str, Any]:
        """Start default profile with retry logic"""
        default_profile_id = self.hma_client.get_default_profile_id()
        return self.start_profile_with_retry(default_profile_id, max_retries, open_tabs, use_backup=True)
    
    def get_profile_uptime(self, profile_id: str) -> Optional[str]:
        """Get profile uptime in human readable format"""
        if profile_id not in self.active_profiles:
            return None
        
        started_at = self.active_profiles[profile_id]['started_at']
        uptime_seconds = time.time() - started_at
        
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
    
    def is_profile_active(self, profile_id: str) -> bool:
        """Check if profile is currently active"""
        return profile_id in self.active_profiles
    
    def get_profile_info(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about active profile"""
        return self.active_profiles.get(profile_id)
    
    def cleanup_expired_profiles(self, max_age_seconds: int = 7200):
        """Cleanup profiles older than max_age_seconds"""
        current_time = time.time()
        expired_profiles = []
        
        for profile_id, info in self.active_profiles.items():
            if current_time - info['started_at'] > max_age_seconds:
                expired_profiles.append(profile_id)
        
        for profile_id in expired_profiles:
            logger.info(f"Cleaning up expired profile: {profile_id}")
            self.stop_profile_safe(profile_id)
    
    def get_active_profiles_summary(self) -> Dict[str, Any]:
        """Get summary of all active profiles"""
        summary = {
            'total_active': len(self.active_profiles),
            'profiles': {}
        }
        
        for profile_id, info in self.active_profiles.items():
            summary['profiles'][profile_id] = {
                'port': info.get('port'),
                'uptime': self.get_profile_uptime(profile_id),
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['started_at'])),
                'open_tabs': info.get('open_tabs', [])
            }
        
        return summary
