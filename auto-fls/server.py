"""
Auto Flash Sale Server
Main Flask application entry point
"""

import os
import sys
import time
import threading
from loguru import logger

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure loguru
    logger.remove()  # Remove default handler
    
    # Add file handler
    logger.add(
        "logs/auto_fls.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    
    # Add console handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    )

# App creation is now handled by app/__init__.py

def background_cleanup(profile_manager):
    """Background task for cleanup"""
    while True:
        try:
            logger.info("Running background cleanup...")
            profile_manager.cleanup_expired_profiles()
            time.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Background cleanup error: {e}")
            time.sleep(60)

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    logger.info("Starting Auto Flash Sale Server...")
    
    # Create Flask app using app/__init__.py
    app, hma_client, profile_manager = create_app()
    
    # Test HMA connection
    try:
        if hma_client.health_check():
            logger.info("✅ HMA server connection successful")
        else:
            logger.warning("⚠️ HMA server connection failed - some features may not work")
    except Exception as e:
        logger.error(f"❌ HMA server connection error: {e}")
    
    # Start background cleanup thread
    cleanup_thread = threading.Thread(
        target=background_cleanup,
        args=(profile_manager,),
        daemon=True,
        name="CleanupThread"
    )
    cleanup_thread.start()
    logger.info("Background cleanup thread started")
    
    # Get server configuration from app config
    from app.config import Config
    config = Config()
    
    # Start Flask server
    try:
        logger.info("🚀 Server starting...")
        app.run(
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
