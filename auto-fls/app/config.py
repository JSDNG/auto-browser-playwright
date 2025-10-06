"""
Configuration management for Auto Flash Sale
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

class Config:
    """Base configuration class"""
    
    # HideMyAcc Configuration
    HMA_API_BASE: str = os.getenv('HMA_API_BASE', 'http://127.0.0.1:2268')
    HMA_API_KEY: Optional[str] = os.getenv('HMA_API_KEY')
    
    # Server Configuration
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '5001'))
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'jwt-secret-key')
    
    # External Services
    N8N_WEBHOOK_URL: Optional[str] = os.getenv('N8N_WEBHOOK_URL')
    PUBLIC_BASE_URL: str = os.getenv('PUBLIC_BASE_URL', 'http://localhost:5001')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = os.getenv('RATE_LIMIT_PER_MINUTE', '60 per minute')
    RATE_LIMIT_BURST: int = int(os.getenv('RATE_LIMIT_BURST', '10'))
    
    # Profile Management
    DEFAULT_PROFILE_TIMEOUT: int = int(os.getenv('DEFAULT_PROFILE_TIMEOUT', '1800'))
    MAX_CONCURRENT_PROFILES: int = int(os.getenv('MAX_CONCURRENT_PROFILES', '5'))
    
    # Profile Configuration
    DEFAULT_PROFILE_ID: str = os.getenv('DEFAULT_PROFILE_ID', '6898c8f7effa52a76ed48168')
    BACKUP_PROFILE_ID: str = os.getenv('BACKUP_PROFILE_ID', '689c58b2effa52a76e7b76be')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/auto_fls.log')
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///auto_fls.db')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    HMA_API_BASE = 'http://test-hma-server:2268'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
