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
        # Log để debug
        print("Starting Etsy Crawler app...", file=sys.stderr)
        print(f"Platform: {sys.platform}", file=sys.stderr)
        print(f"Python: {sys.version}", file=sys.stderr)
        
        # Start FastAPI server trong background thread
        # Wrap trong try-except để không crash app nếu FastAPI lỗi
        def safe_run_fastapi():
            try:
                print("Starting FastAPI server...", file=sys.stderr)
                run_fastapi()
            except Exception as e:
                print(f"FastAPI server error (non-critical): {e}", file=sys.stderr)
        
        api_thread = threading.Thread(target=safe_run_fastapi, daemon=True)
        api_thread.start()
        
        # Start GUI
        # Trên macOS, cần set environment variables trước khi tạo QApplication
        if sys.platform == 'darwin':
            # Đảm bảo app có thể truy cập display
            os.environ['QT_MAC_WANTS_LAYER'] = '1'
            # Disable macOS dark mode nếu cần
            os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
            print("macOS detected, setting Qt environment variables...", file=sys.stderr)
        
        print("Creating QApplication...", file=sys.stderr)
        app_qt = QApplication(sys.argv)
        app_qt.setQuitOnLastWindowClosed(False)
        
        # Đảm bảo app được activate trên macOS
        if sys.platform == 'darwin':
            app_qt.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
            # Đảm bảo app có thể hiển thị windows
            app_qt.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app_qt.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            print("macOS-specific Qt attributes set", file=sys.stderr)
        
        # Tạo window
        print("Creating MainWindow...", file=sys.stderr)
        window = MainWindow()
        print("MainWindow created successfully", file=sys.stderr)
        
        # Hiển thị window và đảm bảo nó được focus
        print("Showing window...", file=sys.stderr)
        window.show()
        window.raise_()
        window.activateWindow()
        
        # Đảm bảo window hiển thị trên top và được focus trên macOS
        if sys.platform == 'darwin':
            # Process events để đảm bảo window được render
            app_qt.processEvents()
            # Đảm bảo window không bị ẩn
            window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            # Force window lên foreground
            window.raise_()
            window.activateWindow()
            # Thêm delay nhỏ để đảm bảo window được render
            QTimer.singleShot(100, lambda: window.raise_() and window.activateWindow())
            print("Window activated for macOS", file=sys.stderr)
        
        print("Starting Qt event loop...", file=sys.stderr)
        sys.exit(app_qt.exec())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Trên macOS, hiển thị error dialog nếu có thể
        if sys.platform == 'darwin':
            try:
                from PyQt6.QtWidgets import QApplication, QMessageBox
                if QApplication.instance() is None:
                    app = QApplication(sys.argv)
                QMessageBox.critical(None, "Lỗi", f"Lỗi khi khởi động app:\n{e}\n\n{traceback.format_exc()}")
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()

