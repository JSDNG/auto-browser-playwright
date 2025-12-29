"""
GUI Main Window cho Etsy Crawler App.
Sử dụng PyQt6 để tạo desktop app với tray icon và form config.
"""
import sys
import asyncio
import json
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton, QTextEdit, QSystemTrayIcon,
    QMenu, QMessageBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction

from src.utils.chrome_launcher import check_cdp_running, launch_chrome_with_cdp


class SpyThread(QThread):
    """Thread để chạy spy Etsy trong background."""
    finished = pyqtSignal(dict)
    log = pyqtSignal(str)
    
    def __init__(self, keyword: str, pages: int, created_date_months: int):
        super().__init__()
        self.keyword = keyword
        self.pages = pages
        self.created_date_months = created_date_months
    
    def run(self):
        """Chạy spy Etsy trong thread riêng."""
        try:
            # Import trong thread để tránh conflict
            from src.app.cdp_connection import spy_etsy_via_cdp
            
            # Chạy async function trong thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.log.emit(f"Bắt đầu spy Etsy: keyword='{self.keyword}', pages={self.pages}")
            result = loop.run_until_complete(
                spy_etsy_via_cdp(
                    keyword=self.keyword,
                    pages=self.pages,
                    created_date_months=self.created_date_months
                )
            )
            
            loop.close()
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"success": False, "error": str(e)})


class MainWindow(QMainWindow):
    """Main window của app."""
    
    def __init__(self):
        super().__init__()
        self.config_path = self._get_config_path()
        self.spy_thread = None
        self.init_ui()
        self.init_tray()
        self.load_config()
    
    def _get_config_path(self) -> Path:
        """Tìm đường dẫn đến config.ini."""
        if getattr(sys, 'frozen', False):
            # Chạy từ PyInstaller executable
            return Path(sys.executable).parent / "config.ini"
        else:
            # Chạy từ source code
            return Path(__file__).parent.parent.parent / "config.ini"
    
    def init_ui(self):
        """Khởi tạo UI."""
        self.setWindowTitle("Etsy Crawler")
        self.setGeometry(100, 100, 600, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Config group
        config_group = QGroupBox("Cấu hình")
        config_layout = QFormLayout()
        
        # Keyword
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("handmade bag")
        config_layout.addRow("Từ khóa:", self.keyword_input)
        
        # Pages
        self.pages_input = QSpinBox()
        self.pages_input.setMinimum(1)
        self.pages_input.setMaximum(20)
        self.pages_input.setValue(5)
        config_layout.addRow("Số trang:", self.pages_input)
        
        # Created date months
        self.months_input = QSpinBox()
        self.months_input.setMinimum(1)
        self.months_input.setMaximum(12)
        self.months_input.setValue(2)
        config_layout.addRow("Lọc theo tháng:", self.months_input)
        
        # Webhook URL - Ẩn khỏi GUI, chỉ đọc từ config.ini
        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("https://spyetsy.supover.com/webhook")
        self.webhook_input.setVisible(False)  # Ẩn field webhook
        
        # CDP Port
        self.cdp_port_input = QSpinBox()
        self.cdp_port_input.setMinimum(1024)
        self.cdp_port_input.setMaximum(65535)
        self.cdp_port_input.setValue(9223)
        config_layout.addRow("CDP Port:", self.cdp_port_input)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_config_btn = QPushButton("Lưu cấu hình")
        self.save_config_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_config_btn)
        
        self.spy_btn = QPushButton("Spy Etsy")
        self.spy_btn.clicked.connect(self.start_spy)
        self.spy_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        button_layout.addWidget(self.spy_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Log output
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Chrome status
        self.chrome_status_label = QLabel("Chrome: Chưa kiểm tra")
        layout.addWidget(self.chrome_status_label)
        
        # Check Chrome status định kỳ
        self.chrome_check_timer = QTimer()
        self.chrome_check_timer.timeout.connect(self.check_chrome_status)
        self.chrome_check_timer.start(5000)  # Check mỗi 5 giây
        self.check_chrome_status()
    
    def init_tray(self):
        """Khởi tạo system tray icon."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", "System tray không khả dụng trên hệ thống này.")
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        # TODO: Thêm icon file
        # self.tray_icon.setIcon(QIcon("icon.png"))
        
        tray_menu = QMenu()
        
        show_action = QAction("Hiển thị", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Thoát", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Xử lý khi click vào tray icon."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def load_config(self):
        """Đọc config từ config.ini."""
        try:
            from src.utils.config_loader import load_config_ini
            config = load_config_ini(str(self.config_path))
            if config:
                self.keyword_input.setText(config["search"]["keyword"])
                self.pages_input.setValue(config["search"]["pages"])
                self.months_input.setValue(config["filter"]["created_date_months"])
                # Webhook vẫn đọc từ config nhưng không hiển thị trong GUI
                if "webhook" in config:
                    self.webhook_input.setText(config["webhook"]["url"])
                self.cdp_port_input.setValue(config["cdp"]["port"])
                self.log("✓ Đã tải config")
            else:
                self.log("⚠️ Không tìm thấy config, dùng giá trị mặc định")
        except Exception as e:
            self.log(f"❌ Lỗi khi đọc config: {e}")
    
    def save_config(self):
        """Lưu config vào config.ini."""
        try:
            import configparser
            config = configparser.ConfigParser()
            
            config["search"] = {
                "keyword": self.keyword_input.text() or "t-shirt",
                "pages": str(self.pages_input.value()),
            }
            config["filter"] = {
                "created_date_months": str(self.months_input.value()),
            }
            config["webhook"] = {
                "url": self.webhook_input.text() or "https://spyetsy.supover.com/webhook",
            }
            config["api"] = {
                "host": "0.0.0.0",
                "port": "5674",
            }
            config["cdp"] = {
                "port": str(self.cdp_port_input.value()),
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.log("✓ Đã lưu config")
            self.status_label.setText("Đã lưu cấu hình")
        except Exception as e:
            self.log(f"❌ Lỗi khi lưu config: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu config: {e}")
    
    def check_chrome_status(self):
        """Kiểm tra Chrome CDP có đang chạy không."""
        port = self.cdp_port_input.value()
        is_running = check_cdp_running(port)
        
        if is_running:
            self.chrome_status_label.setText(f"Chrome: ✓ Đang chạy tại port {port}")
            self.chrome_status_label.setStyleSheet("color: green;")
        else:
            self.chrome_status_label.setText(f"Chrome: ✗ Chưa chạy tại port {port}")
            self.chrome_status_label.setStyleSheet("color: red;")
    
    def start_spy(self):
        """Bắt đầu spy Etsy."""
        # Lưu config trước
        self.save_config()
        
        # Kiểm tra Chrome CDP
        port = self.cdp_port_input.value()
        if not check_cdp_running(port):
            # Tự động khởi động Chrome không cần xác nhận
            self.log(f"Chrome chưa chạy với CDP tại port {port}. Đang tự động khởi động Chrome...")
            try:
                launch_chrome_with_cdp(port)
                self.log("✓ Đã khởi động Chrome")
                # Đợi một chút để Chrome khởi động
                QTimer.singleShot(2000, self._do_spy)
            except Exception as e:
                self.log(f"❌ Lỗi khi khởi động Chrome: {e}")
                QMessageBox.critical(self, "Lỗi", f"Không thể khởi động Chrome: {e}")
                return
        else:
            self._do_spy()
    
    def _do_spy(self):
        """Thực hiện spy sau khi đảm bảo Chrome đã chạy."""
        keyword = self.keyword_input.text() or "t-shirt"
        pages = self.pages_input.value()
        months = self.months_input.value()
        
        self.spy_btn.setEnabled(False)
        self.status_label.setText("Đang spy Etsy...")
        self.log_output.clear()
        self.log(f"Bắt đầu spy: keyword='{keyword}', pages={pages}, months={months}")
        
        # Chạy spy trong thread riêng
        self.spy_thread = SpyThread(keyword, pages, months)
        self.spy_thread.finished.connect(self.on_spy_finished)
        self.spy_thread.log.connect(self.log)
        self.spy_thread.start()
    
    def on_spy_finished(self, result: dict):
        """Xử lý khi spy hoàn thành."""
        self.spy_btn.setEnabled(True)
        
        if result.get("success"):
            count = result.get("count", 0)
            self.status_label.setText(f"✓ Hoàn thành: {count} sản phẩm")
            self.log(f"✓ Spy thành công: {count} sản phẩm")
            self.tray_icon.showMessage(
                "Etsy Crawler",
                f"Spy thành công: {count} sản phẩm",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
        else:
            error = result.get("error", "Unknown error")
            self.status_label.setText(f"❌ Thất bại: {error}")
            self.log(f"❌ Spy thất bại: {error}")
            QMessageBox.critical(self, "Lỗi", f"Spy thất bại: {error}")
    
    def log(self, message: str):
        """Thêm log vào output."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """Xử lý khi đóng window."""
        if self.tray_icon.isVisible():
            QMessageBox.information(
                self,
                "Etsy Crawler",
                "App sẽ chạy trong system tray. Click vào icon để mở lại."
            )
            self.hide()
            event.ignore()
        else:
            event.accept()


def main():
    """Main entry point cho GUI app."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Không thoát khi đóng window
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

