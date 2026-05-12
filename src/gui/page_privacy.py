from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.utils.paths import get_default_privacy_path, get_privacy_path

class PagePrivacy(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #0f1419;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)

        lbl_title = QLabel("🛡️ Quyền Riêng Tư & Bảo Mật")
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #f97316; margin-bottom: 10px;")
        layout.addWidget(lbl_title)

        self.txt_privacy = QTextEdit()
        self.txt_privacy.setReadOnly(True)
        self.txt_privacy.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                color: #cbd5e1;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                border: 2px solid #334155;
                border-radius: 10px;
                padding: 16px;
                line-height: 1.5;
            }
            QScrollBar:vertical {
                background-color: #0f1419;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }
        """)
        layout.addWidget(self.txt_privacy)

        self.load_privacy()

    def load_privacy(self):
        privacy_path = get_privacy_path()
        default_path = get_default_privacy_path()

        content = ""
        if privacy_path.exists():
            content = privacy_path.read_text(encoding="utf-8")
        elif default_path.exists():
            content = default_path.read_text(encoding="utf-8")
        else:
            content = (
                "QUYEN RIENG TU & BAO MAT\n\n"
                "- OFFLINE 100%: Ung dung hoat dong hoan toan tren may tinh cua ban.\n"
                "- KHONG LUU ANH: AI chi quet man hinh qua RAM va xoa ngay lap tuc.\n"
                "- KHONG GUI DU LIEU: Khong gui thong tin nao len Internet.\n"
                "- MINH BACH: Log chi ghi lai thoi gian va toa do.\n"
            )

        self.txt_privacy.setText(content)