import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import qInstallMessageHandler

# Gọi Giao diện chính mà bạn vừa tạo
from src.gui.main_sidebar import ChuyenNghiepGUI
from src.gui.page_settings import PageSettings
from src.gui.page_privacy import PagePrivacy
from src.utils.updater import check_for_updates # Thêm dòng này

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.page_settings = PageSettings(self.main_frame)
        self.page_privacy = PagePrivacy(self.main_frame)

        self.show_page("dashboard")
        
        # Kiểm tra cập nhật khi ứng dụng khởi động
        self.after(2000, self.check_updates_on_startup)

    def check_updates_on_startup(self):
        """Chạy kiểm tra cập nhật trong một luồng riêng để không làm treo GUI."""
        import threading
        update_thread = threading.Thread(target=check_for_updates, daemon=True)
        update_thread.start()

    def show_page(self, page_name):
        self.page_settings.show_page(page_name)
        self.page_privacy.show_page(page_name)

if __name__ == '__main__':
    def _qt_message_handler(mode, context, message):
        if "QFont::setPointSize" in message:
            return
        sys.stderr.write(message + "\n")

    qInstallMessageHandler(_qt_message_handler)
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = ChuyenNghiepGUI()

    # Căn giữa cửa sổ
    qt_rect = window.frameGeometry()
    center_point = app.primaryScreen().availableGeometry().center()
    qt_rect.moveCenter(center_point)
    window.move(qt_rect.topLeft())

    window.show()
    sys.exit(app.exec())