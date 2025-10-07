"""
Auto Flash Sale Server
Main Flask application entry point
"""

import os
import sys
import time
import threading
import requests
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
    
    # Auto-start TikTok Seller after server starts (only once)
    tiktok_url = "https://seller-us.tiktok.com/product"
    
    def auto_start_tiktok_seller():
        """Auto-start TikTok Seller after server is ready"""
        import time  # Import time at the beginning of function
        
        time.sleep(3)  # Wait for server to be ready
        
        try:
            logger.info("🤖 Auto-starting HideMyAcc profile...")
            
            # Start HideMyAcc profile
            logger.info("🤖 Starting HideMyAcc profile...")
            response = requests.post(
                f"http://localhost:{config.SERVER_PORT}/api/v1/start-flash-sale",
                json={
                    "use_backup": True
                },
                timeout=30
            )
            
            logger.info(f"📡 API Response: {response.status_code}")
            logger.info(f"📄 Response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ HideMyAcc profile started successfully!")
                logger.info(f"   Profile ID: {data['data']['profile_id']}")
                logger.info(f"   Port: {data['data']['port']}")
                logger.info(f"   WebSocket: {data['data']['ws_url']}")
                
                # HideMyAcc browser is now open - manual navigation required
                logger.info("🌐 HideMyAcc browser is now open!")
                logger.info("📋 Please manually navigate to TikTok in the HideMyAcc browser:")
                logger.info(f"   {tiktok_url}")
                logger.info("💡 Copy the URL above and paste it in the HideMyAcc browser address bar")
                logger.info("✅ Ready to use!")
                
            else:
                logger.warning(f"⚠️ Auto-start failed: {response.status_code}")
                logger.warning(f"📄 Error response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Auto-start error: {e}")
            logger.error(f"📄 Full error: {str(e)}")
    
    # Only start auto-start in the main worker process (not in reloader)
    # In Flask debug mode: WERKZEUG_RUN_MAIN='true' means we're in the main worker process
    import os
    is_main_worker = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    
    if is_main_worker:
        auto_start_thread = threading.Thread(
            target=auto_start_tiktok_seller,
            daemon=True,
            name="AutoStartThread"
        )
        auto_start_thread.start()
        logger.info("Auto-start thread started (main worker process)")
    else:
        logger.info("⏭️ Auto-start skipped (reloader process)")
    
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
