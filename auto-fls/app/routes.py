"""
API Routes for Auto Flash Sale - Simplified Version
Only 2 main endpoints: /health & /start-flash-sale
"""

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Dict, Any
from loguru import logger

from .config import Config
from .hma_client import HMAClient, ProfileManager
from .utils import (
    validate_profile_id, format_error_response, format_success_response,
    generate_session_id, create_profile_summary
)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Global variables (will be initialized in server.py)
hma_client: HMAClient = None
profile_manager: ProfileManager = None
config: Config = None

def init_routes(hma_client_instance: HMAClient, profile_manager_instance: ProfileManager, config_instance: Config):
    """Initialize routes with dependencies"""
    global hma_client, profile_manager, config
    hma_client = hma_client_instance
    profile_manager = profile_manager_instance
    config = config_instance

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        hma_healthy = hma_client.health_check()
        
        return jsonify({
            "status": "healthy" if hma_healthy else "degraded",
            "hma_server": "connected" if hma_healthy else "disconnected",
            "active_profiles": len(profile_manager.get_active_profiles()),
            "timestamp": format_success_response({})["timestamp"]
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify(format_error_response("Health check failed", "HEALTH_CHECK_ERROR")), 500

@api_bp.route('/start-flash-sale', methods=['POST'])
@limiter.limit("10 per minute")
def start_flash_sale():
    """Start Flash Sale - Main endpoint for automation"""
    try:
        # Get request data
        data = request.get_json() or {}
        profile_id = data.get('profile_id', config.DEFAULT_PROFILE_ID)
        open_tabs = data.get('open_tabs', [])
        use_backup = data.get('use_backup', True)
        
        # Validate profile ID
        if not validate_profile_id(profile_id):
            return jsonify(format_error_response("Invalid profile ID format", "INVALID_PROFILE_ID")), 400
        
        # Check if profile is already active
        active_profiles = profile_manager.get_active_profiles()
        if profile_id in active_profiles:
            return jsonify(format_error_response("Profile is already running", "PROFILE_ALREADY_RUNNING")), 409
        
        # Start profile with retry and backup support
        result = profile_manager.start_profile_with_retry(
            profile_id, 
            open_tabs=open_tabs, 
            use_backup=use_backup
        )
        
        # Create session info
        session_id = generate_session_id(profile_id)
        
        response_data = {
            "session_id": session_id,
            "profile_id": profile_id,
            "port": result['data'].get('port'),
            "ws_url": result['data'].get('wsUrl'),
            "user_agent": result['data'].get('userAgent'),
            "started_at": format_success_response({})["timestamp"],
            "flash_sale_status": "started"
        }
        
        logger.info(f"Flash Sale started for profile {profile_id}", extra=create_profile_summary(response_data))
        
        return jsonify(format_success_response(response_data, "Flash Sale started successfully"))
        
    except Exception as e:
        logger.error(f"Failed to start Flash Sale: {e}")
        return jsonify(format_error_response(str(e), "START_FLASH_SALE_ERROR")), 500

# ===========================================
# SIMPLIFIED ROUTES - ONLY 2 MAIN ENDPOINTS
# ===========================================

# Error handlers
@api_bp.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit error handler"""
    return jsonify(format_error_response("Rate limit exceeded", "RATE_LIMIT_EXCEEDED")), 429

@api_bp.errorhandler(404)
def not_found_handler(e):
    """404 error handler"""
    return jsonify(format_error_response("Endpoint not found", "NOT_FOUND")), 404

@api_bp.errorhandler(500)
def internal_error_handler(e):
    """500 error handler"""
    logger.error(f"Internal server error: {e}")
    return jsonify(format_error_response("Internal server error", "INTERNAL_ERROR")), 500
