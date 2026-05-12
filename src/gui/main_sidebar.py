from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QFrame,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
    QInputDialog,
    QLineEdit,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon, QKeySequence, QShortcut
from time import monotonic

from src.utils.paths import APP_NAME, get_assets_dir
from src.utils.windows_startup import set_startup

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None

# Import 4 trang bạn vừa tạo
from src.gui.page_dashboard import PageDashboard
from src.gui.page_settings import PageSettings
from src.gui.page_logs import PageLogs
from src.gui.page_privacy import PagePrivacy

class ChuyenNghiepGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShieldGuard - Hệ Thống Nhận Diện Ảnh 18+")
        self.setFixedSize(1000, 650)
        self.setWindowIcon(self._app_icon())
        
        # Áp dụng Dark Mode chuyên nghiệp
        self.setStyleSheet("""
            QMainWindow { background-color: #0f1419; }
            QLabel { color: #e8eef7; }
            QPushButton {
                background-color: #1e293b; color: #e8eef7;
                border: 2px solid transparent; padding: 14px 16px; text-align: left;
                border-radius: 8px; font-weight: 600; font-size: 13px;
            }
            QPushButton:hover { 
                background-color: #334155; border: 2px solid #3b82f6;
                padding: 14px 16px;
            }
            QPushButton:pressed { background-color: #0f172a; }
            QPushButton:checked { 
                background-color: #3b82f6; color: #ffffff; 
                border: 2px solid #1e40af;
            }
        """)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # --- SIDEBAR BÊN TRÁI ---
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QWidget { background-color: #1a202c; }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        sidebar_layout.setSpacing(15)

        # Header sidebar
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(get_assets_dir() / "MyLogo.jpg"))
        logo_pixmap = logo_pixmap.scaledToHeight(55, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label)

        # Text bên phải logo
        text_container = QVBoxLayout()
        text_container.setContentsMargins(0, 0, 0, 0)
        text_container.setSpacing(0)

        title_text = QLabel("SHIELD GUARD")
        title_text.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_text.setStyleSheet("color: #ff4b6e;")
        text_container.addWidget(title_text)

        subtitle_text = QLabel("REAL-TIME PROTECTION")
        subtitle_text.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        subtitle_text.setStyleSheet("color: #ffffff;")
        text_container.addWidget(subtitle_text)

        header_layout.addLayout(text_container)
        header_layout.addStretch()
        sidebar_layout.addWidget(header_container)
        
        sidebar_layout.addSpacing(20)

        self.btn_dash = QPushButton("🏠 Bảng Điều Khiển")
        self.btn_logs = QPushButton("📊 Nhật Ký (Logs)")
        self.btn_settings = QPushButton("⚙️ Cài Đặt AI")
        self.btn_privacy = QPushButton("🔒 Quyền Riêng Tư")

        self.nav_buttons = [self.btn_dash, self.btn_logs, self.btn_settings, self.btn_privacy]
        for btn in self.nav_buttons:
            btn.setCheckable(True)
            btn.setMinimumHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()

        # --- NỘI DUNG BÊN PHẢI ---
        self.pages = QStackedWidget()
        self.pages.setContentsMargins(30, 30, 30, 30)
        self.pages.setStyleSheet("background-color: #0f1419;")
        
        # Nhúng 4 trang vào
        self.dash_page = PageDashboard()
        self.settings_page = PageSettings(self.dash_page.he_thong_ngam)
        self.core = self.dash_page.he_thong_ngam
        self.pages.addWidget(self.dash_page)
        self.pages.addWidget(PageLogs())
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(PagePrivacy())

        self.settings_page.settings_saved.connect(self._on_settings_saved)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

        # Bắt sự kiện chuyển trang
        self.btn_dash.clicked.connect(lambda: self.chuyen_trang(0, self.btn_dash))
        self.btn_logs.clicked.connect(lambda: self.chuyen_trang(1, self.btn_logs))
        self.btn_settings.clicked.connect(lambda: self._try_open_settings())
        self.btn_privacy.clicked.connect(lambda: self.chuyen_trang(3, self.btn_privacy))

        self._init_tray()
        self._apply_startup()
        self._setup_hotkey()
        self._setup_global_hotkey()
        self._auto_start_protection()

        self.chuyen_trang(0, self.btn_dash) # Mặc định mở Trang chủ

    def _app_icon(self):
        icon_path = get_assets_dir() / "icons" / "app_icon.ico"
        if icon_path.exists():
            return QIcon(str(icon_path))
        logo_path = get_assets_dir() / "MyLogo.jpg"
        if logo_path.exists():
            return QIcon(str(logo_path))
        return QIcon()

    def _init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return

        tray_menu = QMenu(self)
        action_show = tray_menu.addAction("Mở ứng dụng")
        action_exit = tray_menu.addAction("Thoát")

        action_show.triggered.connect(self._restore_from_tray)
        action_exit.triggered.connect(self._exit_app)

        self.tray_icon = QSystemTrayIcon(self._app_icon(), self)
        self.tray_icon.setToolTip(APP_NAME)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _apply_startup(self):
        entry_point = (get_assets_dir().parent / "main.py").resolve()
        set_startup(self.core.start_with_windows, APP_NAME, entry_point)

    def _normalize_hotkey(self, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return ""
        has_modifier = any(mod in cleaned for mod in ("Ctrl", "Alt", "Shift", "Meta"))
        if "+" in cleaned and not has_modifier:
            return ", ".join(part.strip() for part in cleaned.split("+") if part.strip())
        return cleaned

    def _setup_hotkey(self):
        seq_text = self._normalize_hotkey(self.core.emergency_hotkey)
        if not seq_text:
            self.hotkey_shortcut = None
            return
        self.hotkey_shortcut = QShortcut(QKeySequence(seq_text), self)
        self.hotkey_shortcut.activated.connect(self._emergency_stop)

    def _setup_global_hotkey(self):
        self._stop_global_hotkey()
        if pynput_keyboard is None:
            return

        hotkey_type, tokens = self._parse_hotkey(self.core.emergency_hotkey)
        if hotkey_type == "combo":
            combo = "+".join(tokens)
            self.global_hotkey = pynput_keyboard.GlobalHotKeys({combo: self._emergency_stop})
            self.global_hotkey.start()
        elif hotkey_type == "sequence":
            self._seq_tokens = tokens
            self._seq_index = 0
            self._seq_deadline = 0.0
            self.sequence_listener = pynput_keyboard.Listener(on_press=self._on_sequence_press)
            self.sequence_listener.start()

    def _stop_global_hotkey(self):
        if getattr(self, "global_hotkey", None):
            try:
                self.global_hotkey.stop()
            except Exception:
                pass
            self.global_hotkey = None

        if getattr(self, "sequence_listener", None):
            try:
                self.sequence_listener.stop()
            except Exception:
                pass
            self.sequence_listener = None

    def _parse_hotkey(self, text: str):
        cleaned = self._normalize_hotkey(text)
        if not cleaned:
            return "none", []

        raw_tokens = [t.strip().lower() for t in cleaned.replace(",", "+").split("+") if t.strip()]
        if not raw_tokens:
            return "none", []

        modifiers = {"ctrl", "alt", "shift", "win", "windows", "meta"}
        has_modifier = any(token in modifiers for token in raw_tokens)

        if has_modifier:
            mapped = []
            for token in raw_tokens:
                if token in ("win", "windows"):
                    mapped.append("<cmd>")
                elif token == "ctrl":
                    mapped.append("<ctrl>")
                elif token == "alt":
                    mapped.append("<alt>")
                elif token == "shift":
                    mapped.append("<shift>")
                elif token == "meta":
                    mapped.append("<cmd>")
                else:
                    mapped.append(token)
            return "combo", mapped

        return "sequence", raw_tokens

    def _key_to_token(self, key):
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        if hasattr(key, "name") and key.name:
            return key.name.lower()
        return ""

    def _on_sequence_press(self, key):
        if not getattr(self, "_seq_tokens", None):
            return
        token = self._key_to_token(key)
        if not token:
            return

        now = monotonic()
        if now > getattr(self, "_seq_deadline", 0.0):
            self._seq_index = 0

        expected = self._seq_tokens[self._seq_index] if self._seq_index < len(self._seq_tokens) else ""
        if token == expected:
            self._seq_index += 1
            self._seq_deadline = now + 1.5
            if self._seq_index >= len(self._seq_tokens):
                self._seq_index = 0
                self._seq_deadline = 0.0
                self._emergency_stop()
        else:
            self._seq_index = 1 if token == self._seq_tokens[0] else 0
            self._seq_deadline = now + 1.5 if self._seq_index == 1 else 0.0

    def _auto_start_protection(self):
        if self.core.start_with_windows and not self.dash_page.dang_hoat_dong:
            self.dash_page.toggle_system()

    def _on_settings_saved(self):
        self._apply_startup()
        self._setup_hotkey()
        self._setup_global_hotkey()

    def _emergency_stop(self):
        # Ensure GUI/timer operations run on the main thread.
        QTimer.singleShot(0, self.dash_page.emergency_stop)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._restore_from_tray()

    def _restore_from_tray(self):
        self.showNormal()
        self.activateWindow()

    def _exit_app(self):
        if self.tray_icon:
            self.tray_icon.hide()
        self.close()

    def _try_open_settings(self):
        if not self.core.settings_password:
            self.chuyen_trang(2, self.btn_settings)
            return

        text, ok = QInputDialog.getText(
            self,
            "Xác thực",
            "Nhập mật khẩu để mở Cài đặt:",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return
        if text == self.core.settings_password:
            self.chuyen_trang(2, self.btn_settings)
        else:
            QMessageBox.warning(self, "Sai mật khẩu", "Mật khẩu không đúng.")

    def chuyen_trang(self, index, active_btn):
        self.pages.setCurrentIndex(index)
        for btn in self.nav_buttons:
            btn.setChecked(False)
        active_btn.setChecked(True)

    def closeEvent(self, event):
        if self.core.minimize_to_tray and self.tray_icon:
            self.hide()
            self.tray_icon.showMessage(
                APP_NAME,
                "Ứng dụng vẫn đang chạy trong khay hệ thống.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
            event.ignore()
            return
        self._stop_global_hotkey()
        event.accept()