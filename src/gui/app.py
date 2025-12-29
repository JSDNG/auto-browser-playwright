"""
Main entry point cho GUI app.
Kết hợp FastAPI server và GUI window.
"""
import sys
import asyncio
import threading
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow
from src.app.api_server import app
import uvicorn


def run_fastapi():
    """Chạy FastAPI server trong thread riêng."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5674,
        log_level="info"
    )


def main():
    """Main entry point: Chạy cả GUI và FastAPI."""
    # Start FastAPI server trong background thread
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    
    # Start GUI
    app_qt = QApplication(sys.argv)
    app_qt.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()

