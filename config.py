"""
Configuration file for Playwright automation.
"""

# Default configuration
DEFAULT_CONFIG = {
    "url": "https://meet.google.com/landing",
    "headless": False,
    "timeout": 60000,
    "viewport": {
        "width": 1280,
        "height": 720
    },
    "extract": [
        {
            "name": "title",
            "selector": "h1"
        },
        {
            "name": "page_title", 
            "selector": "title"
        }
    ]
}

# Alternative URLs for testing
ALTERNATIVE_URLS = {
    "google": "https://www.google.com",
    "example": "https://example.com",
    "github": "https://github.com",
    "meet": "https://meet.google.com/landing"
}

# Common selectors for different sites
SELECTORS = {
    "title": ["h1", "h2", "h3", "title", "[role='heading']", ".title", "#title"],
    "description": ["p", ".description", "#description", "meta[name='description']"],
    "links": ["a[href]"],
    "images": ["img[src]"],
    "buttons": ["button", "input[type='button']", "input[type='submit']"]
}

def get_config(url_key: str = "meet") -> dict:
    """Get configuration for specific URL."""
    config = DEFAULT_CONFIG.copy()
    
    if url_key in ALTERNATIVE_URLS:
        config["url"] = ALTERNATIVE_URLS[url_key]
    
    return config 