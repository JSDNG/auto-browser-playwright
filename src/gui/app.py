"""
Main entry point cho GUI app.
Kết hợp FastAPI server và GUI window.
"""
import sys
import os
import asyncio
import threading
from pathlib import Path

# Fix PyInstaller temp directory issue on macOS
# Set TMPDIR to user's home BEFORE PyInstaller tries to extract
# This must be done very early, before any imports that might trigger PyInstaller extraction
if sys.platform == 'darwin':
    home_dir = Path.home()
    custom_tmp = home_dir / '.etsycrawlerdragonmedia_temp'
    # Create directory immediately
    try:
        custom_tmp.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass  # If can't create, try to use it anyway
    # Set TMPDIR immediately, before PyInstaller extraction
    os.environ['TMPDIR'] = str(custom_tmp)
    os.environ['_MEIPASS2'] = str(custom_tmp)  # Also set PyInstaller's internal variable

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt

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
    try:
        # Start FastAPI server trong background thread
        # Wrap trong try-except để không crash app nếu FastAPI lỗi
        def safe_run_fastapi():
            try:
                run_fastapi()
            except Exception as e:
                print(f"FastAPI server error (non-critical): {e}", file=sys.stderr)
        
        api_thread = threading.Thread(target=safe_run_fastapi, daemon=True)
        api_thread.start()
        
        # Start GUI
        app_qt = QApplication(sys.argv)
        app_qt.setQuitOnLastWindowClosed(False)
        
        # Đảm bảo app được activate trên macOS
        if sys.platform == 'darwin':
            app_qt.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
        
        window = MainWindow()
        window.show()
        
        # Đảm bảo window hiển thị trên top và được focus trên macOS
        if sys.platform == 'darwin':
            # Process events để đảm bảo window được render
            app_qt.processEvents()
            window.raise_()
            window.activateWindow()
            # Đảm bảo window không bị ẩn
            window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        
        sys.exit(app_qt.exec())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

