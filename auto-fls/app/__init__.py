"""
Auto Flash Sale - HideMyAcc Automation
Main application package
"""

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger

from .config import Config
from .hma_client import HMAClient, ProfileManager
from .routes import api_bp, init_routes

__version__ = "1.0.0"
__author__ = "Auto FLS"
__description__ = "Automated Flash Sale using HideMyAcc API"

def create_app(config_class=Config):
    """
    Create and configure Flask application
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = config_class()
    
    # Set Flask configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    
    # Enable CORS
    CORS(app, origins="*")
    
    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["60 per minute"],
        storage_uri="memory://"
    )
    limiter.init_app(app)
    
    # Initialize HMA client and profile manager
    hma_client = HMAClient(config)
    profile_manager = ProfileManager(hma_client)
    
    # Initialize routes with dependencies
    init_routes(hma_client, profile_manager, config)
    
    # Register blueprints with API prefix
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Add API documentation endpoint
    @app.route('/api')
    def api_docs():
        """API documentation endpoint"""
        return {
            "name": "Auto Flash Sale API",
            "version": __version__,
            "description": __description__,
            "endpoints": {
                "health": {
                    "method": "GET",
                    "url": "/api/v1/health",
                    "description": "Check system health and HMA connection"
                },
                "start_flash_sale": {
                    "method": "POST", 
                    "url": "/api/v1/start-flash-sale",
                    "description": "Start Flash Sale automation",
                    "body": {
                        "profile_id": "string (optional, default from config)",
                        "open_tabs": "array (optional)",
                        "use_backup": "boolean (optional, default true)"
                    }
                }
            },
            "examples": {
                "start_flash_sale": {
                    "curl": "curl -X POST http://localhost:5001/api/v1/start-flash-sale -H 'Content-Type: application/json' -d '{\"open_tabs\": [\"https://seller.tiktok.com\"]}'"
                }
            }
        }
    
    # Add health check at root
    @app.route('/')
    def index():
        """Root endpoint"""
        return {
            "name": "Auto Flash Sale",
            "version": __version__,
            "description": __description__,
            "status": "running",
            "endpoints": {
                "health": "/api/v1/health",
                "start_flash_sale": "/api/v1/start-flash-sale"
            }
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return {
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "available_endpoints": [
                "GET /api/v1/health",
                "POST /api/v1/start-flash-sale"
            ]
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal server error: {error}")
        return {
            "error": "Internal Server Error",
            "message": "An internal server error occurred"
        }, 500
    
    # Log application startup
    logger.info("=" * 50)
    logger.info(f"Auto Flash Sale v{__version__} initialized")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"HMA API Base: {config.HMA_API_BASE}")
    logger.info(f"Default Profile ID: {config.DEFAULT_PROFILE_ID}")
    logger.info(f"Backup Profile ID: {config.BACKUP_PROFILE_ID}")
    logger.info(f"Server will run on: {config.SERVER_HOST}:{config.SERVER_PORT}")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/v1/health")
    logger.info("  POST /api/v1/start-flash-sale")
    logger.info("  GET  /api (API documentation)")
    logger.info("=" * 50)
    
    return app, hma_client, profile_manager

def create_app_simple():
    """
    Create simple Flask application without HMA dependencies
    Useful for testing or when HMA is not available
    
    Returns:
        Flask: Simple Flask application
    """
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['DEBUG'] = True
    
    # Enable CORS
    CORS(app)
    
    # Simple health check
    @app.route('/')
    def index():
        return {
            "name": "Auto Flash Sale",
            "version": __version__,
            "status": "running (simple mode)",
            "message": "HMA dependencies not loaded"
        }
    
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "mode": "simple",
            "version": __version__
        }
    
    return app
