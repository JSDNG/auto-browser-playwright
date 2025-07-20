import sys
import os
from pathlib import Path
import uvicorn
# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright, Browser, Playwright, Page, BrowserContext
import asyncio  
import logging  
import platform
from typing import Optional, Dict, List, Any, Union
import uuid
from contextlib import asynccontextmanager
from src.models.input import AutomationInput
from src.core.automation import PlaywrightAutomation
from src.app.main import run_automation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class NavigateRequest(BaseModel):
    session_id: str
    url: str
    wait_until: str = "domcontentloaded"

class ExecuteJSRequest(BaseModel):
    session_id: str
    script: str

# ===== AUTOMATION CLASSES IMPORTED FROM OTHER FILES =====
# PlaywrightAutomation, ActionExecutor, DataExtractor are now imported from their respective files
# get_default_config and run_automation are now imported from main.py

# ===== BROWSER SESSION MANAGEMENT =====
class BrowserSession:
    def __init__(self, session_id: str, browser: Browser, context: BrowserContext, page: Page, automation: PlaywrightAutomation = None):
        self.session_id = session_id
        self.browser = browser
        self.context = context
        self.page = page
        self.automation = automation
        self.created_at = asyncio.get_event_loop().time()
        self.automation_data = {}

class BrowserManager:
    def __init__(self):
        self.playwright: Playwright = None
        self.sessions: Dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        
    async def start_playwright(self):
        """Initialize Playwright"""
        if self.playwright is None:
            logger.info("Starting Playwright...")
            self.playwright = await async_playwright().start()
            logger.info("Playwright started successfully")
    
    async def create_browser_session(self, request: AutomationInput) -> tuple[str, Dict[str, Any]]:
        """Create a new browser session with optional automation"""
        await self.start_playwright()
        
        session_id = str(uuid.uuid4())
        automation_result = {}
        
        try:                            
            # Run automation
            automation_result, automation_instance = await run_automation(request)
                
            if automation_result["success"] and automation_instance:
                # Store the automation session
                session = BrowserSession(
                    session_id=session_id,
                    browser=automation_instance.browser,
                    context=automation_instance.context,
                    page=automation_instance.page,
                    automation=automation_instance
                )
                session.automation_data = automation_result["data"]
                self.sessions[session_id] = session
                    
                logger.info(f"Created automation session {session_id}")
                return session_id, automation_result
            else:
                # Automation failed
                return session_id, automation_result
                
        except Exception as e:
            logger.error(f"Failed to create browser session: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create browser session: {str(e)}")
    
    async def get_session(self, session_id: str) -> BrowserSession:
        """Get browser session by ID"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return self.sessions[session_id]
    
    async def close_session(self, session_id: str):
        """Close a specific browser session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            try:
                if session.automation:
                    await session.automation.close()
                else:
                    await session.page.close()
                    await session.context.close()
                    await session.browser.close()
                del self.sessions[session_id]
                logger.info(f"Closed session {session_id}")
            except Exception as e:
                logger.error(f"Error closing session {session_id}: {e}")
    
    async def close_all_sessions(self):
        """Close all browser sessions"""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
    
    async def stop(self):
        """Stop all sessions and playwright"""
        await self.close_all_sessions()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            logger.info("Playwright stopped")

# Global browser manager
browser_manager = BrowserManager()

# ===== FASTAPI ROUTES =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup playwright"""
    await browser_manager.start_playwright()
    yield
    await browser_manager.stop()

# Remove the old app definition and recreate with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "FastAPI Playwright Browser Controller with Automation", "sessions": len(browser_manager.sessions)}

@app.post("/automation")
async def open_browser(request: AutomationInput):
    """Open a new browser window with optional automation"""
    session_id, automation_result = await browser_manager.create_browser_session(request)
    
    return {
        "success": automation_result.get("success", True),
        "session_id": session_id,
        "automation_result": automation_result,
        "headless": request.headless,
        "message": f"Browser session created: {session_id}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5765)