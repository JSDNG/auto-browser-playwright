"""
Validators for input validation and security checks.
"""

import re
import ipaddress
from typing import List, Optional
from urllib.parse import urlparse


class URLValidator:
    """Validator for URL security and format checks."""
    
    # Blocked domains and IP ranges
    BLOCKED_DOMAINS = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "local",
        "internal",
        "private"
    ]
    
    # Private IP ranges
    PRIVATE_IP_RANGES = [
        ipaddress.IPv4Network("10.0.0.0/8"),
        ipaddress.IPv4Network("172.16.0.0/12"),
        ipaddress.IPv4Network("192.168.0.0/16"),
        ipaddress.IPv4Network("127.0.0.0/8"),
        ipaddress.IPv4Network("169.254.0.0/16"),
        ipaddress.IPv6Network("::1/128"),
        ipaddress.IPv6Network("fc00::/7"),
        ipaddress.IPv6Network("fe80::/10")
    ]
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Check if URL is valid format."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ["http", "https"]
        except Exception:
            return False
    
    @classmethod
    def is_safe_url(cls, url: str) -> bool:
        """Check if URL is safe to access."""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ["http", "https"]:
                return False
            
            # Check hostname
            hostname = parsed.hostname
            if not hostname:
                return False
            
            # Check against blocked domains
            hostname_lower = hostname.lower()
            for blocked in cls.BLOCKED_DOMAINS:
                if blocked in hostname_lower:
                    return False
            
            # Check if hostname is an IP address
            try:
                ip = ipaddress.ip_address(hostname)
                
                # Check if IP is in private range
                for private_range in cls.PRIVATE_IP_RANGES:
                    if ip in private_range:
                        return False
                        
            except ValueError:
                # Not an IP address, continue with hostname checks
                pass
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r"\.local$",
                r"\.internal$",
                r"\.corp$",
                r"\.lan$",
                r"^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$"
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, hostname_lower):
                    return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate URL and return it if safe."""
        if not cls.is_valid_url(url):
            raise ValueError("Invalid URL format")
        
        if not cls.is_safe_url(url):
            raise ValueError("URL is not safe to access")
        
        return url


class SelectorValidator:
    """Validator for CSS selectors."""
    
    # Dangerous selector patterns
    DANGEROUS_PATTERNS = [
        r"javascript:",
        r"data:",
        r"<script",
        r"</script>",
        r"eval\(",
        r"document\.write"
    ]
    
    @classmethod
    def is_valid_selector(cls, selector: str) -> bool:
        """Check if CSS selector is valid."""
        if not selector or not selector.strip():
            return False
        
        # Check for dangerous patterns
        selector_lower = selector.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, selector_lower):
                return False
        
        # Basic CSS selector validation
        try:
            # Check for balanced brackets
            if selector.count("(") != selector.count(")"):
                return False
            if selector.count("[") != selector.count("]"):
                return False
            if selector.count("{") != selector.count("}"):
                return False
            
            # Check for basic CSS selector patterns
            valid_chars = re.compile(r'^[a-zA-Z0-9\-_#\.\[\]:\(\)\s\*\+\~\>\|"\'=,]+$')
            if not valid_chars.match(selector):
                return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def validate_selector(cls, selector: str) -> str:
        """Validate CSS selector and return it if safe."""
        if not cls.is_valid_selector(selector):
            raise ValueError("Invalid CSS selector")
        
        return selector.strip()


class InputValidator:
    """General input validator."""
    
    @classmethod
    def validate_timeout(cls, timeout: int) -> int:
        """Validate timeout value."""
        if not isinstance(timeout, int):
            raise ValueError("Timeout must be an integer")
        
        if timeout < 1000:
            raise ValueError("Timeout must be at least 1000ms")
        
        if timeout > 300000:  # 5 minutes
            raise ValueError("Timeout must not exceed 300000ms")
        
        return timeout
    
    @classmethod
    def validate_viewport(cls, viewport: dict) -> dict:
        """Validate viewport configuration."""
        if not isinstance(viewport, dict):
            raise ValueError("Viewport must be a dictionary")
        
        if "width" not in viewport or "height" not in viewport:
            raise ValueError("Viewport must contain width and height")
        
        width = viewport["width"]
        height = viewport["height"]
        
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("Viewport dimensions must be integers")
        
        if width < 100 or height < 100:
            raise ValueError("Viewport dimensions must be at least 100x100")
        
        if width > 3840 or height > 2160:
            raise ValueError("Viewport dimensions must not exceed 3840x2160")
        
        return viewport
    
    @classmethod
    def validate_text_input(cls, text: str, max_length: int = 10000) -> str:
        """Validate text input."""
        if not isinstance(text, str):
            raise ValueError("Text input must be a string")
        
        if len(text) > max_length:
            raise ValueError(f"Text input must not exceed {max_length} characters")
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            r"<script",
            r"</script>",
            r"javascript:",
            r"data:",
            r"eval\(",
            r"document\."
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, text_lower):
                raise ValueError("Text contains potentially dangerous content")
        
        return text
    
    @classmethod
    def validate_action_type(cls, action_type: str) -> str:
        """Validate action type."""
        valid_actions = [
            "click", "fill", "select", "wait", "press", 
            "hover", "check", "uncheck"
        ]
        
        if action_type not in valid_actions:
            raise ValueError(f"Invalid action type: {action_type}")
        
        return action_type
    
    @classmethod
    def validate_attribute_name(cls, attribute: str) -> str:
        """Validate HTML attribute name."""
        if not isinstance(attribute, str):
            raise ValueError("Attribute name must be a string")
        
        if not attribute.strip():
            raise ValueError("Attribute name cannot be empty")
        
        # Check for valid HTML attribute name pattern
        valid_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9\-_]*$')
        if not valid_pattern.match(attribute):
            raise ValueError("Invalid attribute name format")
        
        return attribute.strip()
    
    @classmethod
    def sanitize_string(cls, text: str) -> str:
        """Sanitize string input."""
        if not isinstance(text, str):
            return ""
        
        # Remove null bytes and other control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


class SecurityValidator:
    """Security-focused validator."""
    
    @classmethod
    def is_safe_javascript(cls, script: str) -> bool:
        """Check if JavaScript code is safe to execute."""
        if not script:
            return True
        
        # List of dangerous JavaScript patterns
        dangerous_patterns = [
            r"eval\s*\(",
            r"Function\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            r"document\.write",
            r"document\.writeln",
            r"innerHTML\s*=",
            r"outerHTML\s*=",
            r"location\s*=",
            r"window\.location",
            r"document\.location",
            r"XMLHttpRequest",
            r"fetch\s*\(",
            r"import\s*\(",
            r"require\s*\(",
            r"process\.",
            r"global\.",
            r"__dirname",
            r"__filename"
        ]
        
        script_lower = script.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, script_lower):
                return False
        
        return True
    
    @classmethod
    def validate_javascript(cls, script: str) -> str:
        """Validate JavaScript code."""
        if not cls.is_safe_javascript(script):
            raise ValueError("JavaScript code contains dangerous patterns")
        
        return script 