from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import lõi quét ngầm
from src.core.core_app import KhungCheThongMinh

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.he_thong_ngam = KhungCheThongMinh()
        self.dang_hoat_dong = False
        self.setStyleSheet("background-color: #0f1419;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)

        # --- TIÊU ĐỀ ---
        title = QLabel("Bảng Điều Khiển Hệ Thống")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #e8eef7; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- THẺ THÔNG TIN TRẠNG THÁI ---
        status_card = QFrame()
        status_card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(25, 25, 25, 25)
        status_layout.setSpacing(15)

        status_title = QLabel("Trạng Thái Bảo Vệ")
        status_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        status_title.setStyleSheet("color: #94a3b8;")
        status_layout.addWidget(status_title)

        self.lbl_status = QLabel("🔴 ĐANG TẮT")
        self.lbl_status.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.lbl_status.setStyleSheet("color: #ef4444;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.lbl_status)

        layout.addWidget(status_card)

        # --- KHÔNG GIAN TRỐNG ---
        layout.addStretch()

        # --- NÚT ĐIỀU KHIỂN ---
        self.btn_toggle = QPushButton("▶  BẮT ĐẦU BẢO VỆ")
        self.btn_toggle.setMinimumHeight(70)
        self.btn_toggle.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.btn_toggle.clicked.connect(self.toggle_system)
        layout.addWidget(self.btn_toggle)

    def toggle_system(self):
        if not self.dang_hoat_dong:
            self.he_thong_ngam.bat_dau()
            self.lbl_status.setText("🟢 ĐANG GIÁM SÁT")
            self.lbl_status.setStyleSheet("color: #10b981;")
            self.btn_toggle.setText("⏹  DỪNG BẢO VỆ")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
                QPushButton:pressed {
                    background-color: #b91c1c;
                }
            """)
            self.dang_hoat_dong = True
        else:
            self.he_thong_ngam.dung_lai()
            self.lbl_status.setText("🔴 ĐANG TẮT")
            self.lbl_status.setStyleSheet("color: #ef4444;")
            self.btn_toggle.setText("▶  BẮT ĐẦU BẢO VỆ")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
                QPushButton:pressed {
                    background-color: #047857;
                }
            """)
            self.dang_hoat_dong = False

    def emergency_stop(self):
        if not self.dang_hoat_dong:
            return
        self.he_thong_ngam.dung_lai()
        self.lbl_status.setText("🔴 ĐANG TẮT")
        self.lbl_status.setStyleSheet("color: #ef4444;")
        self.btn_toggle.setText("▶  BẮT ĐẦU BẢO VỆ")
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.dang_hoat_dong = False