import re
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QToolButton,
    QFrame,
    QHBoxLayout,
    QComboBox,
    QMessageBox,
    QStyle,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.utils.paths import get_log_path

class PageLogs(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #0f1419;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # --- HEADER ---
        lbl_title = QLabel("📊 Nhật Ký Vi Phạm")
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #e8eef7; margin-bottom: 10px;")
        layout.addWidget(lbl_title)

        # --- LOG VIEWER ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setStyleSheet(""
            "QScrollArea { background-color: transparent; }"
            "QScrollBar:vertical { background-color: #0f1419; width: 10px; border: none; }"
            "QScrollBar::handle:vertical { background-color: #475569; border-radius: 5px; }"
            "QScrollBar::handle:vertical:hover { background-color: #64748b; }"
        )

        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_layout.setSpacing(12)

        self.scroll.setWidget(self.log_container)
        layout.addWidget(self.scroll)

        # --- ACTIONS ---
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(10)

        self.cb_delete = QComboBox()
        self.cb_delete.addItems([
            "Xóa dữ liệu 30 phút",
            "Xóa dữ liệu 1 giờ",
            "Xóa dữ liệu 3 giờ",
            "Xóa dữ liệu 24 giờ",
        ])
        self.cb_delete.setMinimumWidth(180)
        self.cb_delete.setStyleSheet(
            "QComboBox { color: #e8eef7; background-color: #0f1419; border: 1px solid #2b3340; border-radius: 6px; padding: 6px 8px; }"
            "QComboBox QAbstractItemView { color: #e8eef7; background-color: #0f1419; selection-background-color: #1e293b; }"
        )
        action_row.addWidget(self.cb_delete)

        self.btn_delete = QPushButton("🗑️ Xóa dữ liệu")
        self.btn_delete.setMinimumHeight(40)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(
            "QPushButton { background-color: #f97316; color: white; border: none; border-radius: 8px; font-weight: bold; padding: 6px 14px; }"
            "QPushButton:hover { background-color: #ea580c; }"
            "QPushButton:pressed { background-color: #c2410c; }"
        )
        self.btn_delete.clicked.connect(self._delete_by_range)
        action_row.addWidget(self.btn_delete)

        btn_refresh = QPushButton("🔄 Làm mới dữ liệu")
        btn_refresh.setMinimumHeight(40)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(
            "QPushButton { background-color: #3b82f6; color: white; border: none; border-radius: 8px; font-weight: bold; padding: 6px 14px; }"
            "QPushButton:hover { background-color: #2563eb; }"
            "QPushButton:pressed { background-color: #1d4ed8; }"
        )
        btn_refresh.clicked.connect(self.load_logs)
        action_row.addWidget(btn_refresh)

        action_row.addStretch()
        layout.addLayout(action_row)

        self.load_logs()

    def load_logs(self):
        for i in reversed(range(self.log_layout.count())):
            item = self.log_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        log_path = get_log_path()
        if not log_path.exists():
            self._show_empty()
            return

        lines = log_path.read_text(encoding="utf-8").splitlines()
        entries = [self._parse_line(line) for line in lines]
        entries = [entry for entry in entries if entry is not None]

        groups = self._group_entries(entries)
        if not groups:
            self._show_empty()
            return

        for entry in groups:
            card = LogCard(entry, self._delete_entry)
            self.log_layout.addWidget(card)

        self.log_layout.addStretch()

    def _show_empty(self):
        empty = QLabel("✓ Hệ thống sạch - Chưa ghi nhận vi phạm nào!")
        empty.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        empty.setStyleSheet("color: #94a3b8; padding: 10px;")
        self.log_layout.addWidget(empty)
        self.log_layout.addStretch()

    def _parse_line(self, line):
        if not line or line.startswith("---"):
            return None

        action_match = re.match(
            r"\[(?P<time>[^\]]+)\]\s*\|\s*Cấp độ:\s*(?P<level>\d+)\s*\|\s*Hành động:\s*(?P<action>[^|]+)\|\s*Cửa sổ:\s*(?P<window>.+)",
            line,
        )
        if action_match:
            return {
                "type": "action",
                "time": action_match.group("time").strip(),
                "time_dt": self._parse_time(action_match.group("time").strip()),
                "level": action_match.group("level").strip(),
                "action": action_match.group("action").strip(),
                "window": action_match.group("window").strip(),
                "raw": line,
            }

        detect_match = re.match(
            r"\[(?P<time>[^\]]+)\]\s*\|\s*Khung hình:\s*(?P<frame>\d+)\s*\|\s*Tọa độ:\s*(?P<box>\[[^\]]+\])\s*\|\s*Độ chính xác:\s*(?P<score>[\d.]+)%",
            line,
        )
        if detect_match:
            return {
                "type": "detect",
                "time": detect_match.group("time").strip(),
                "time_dt": self._parse_time(detect_match.group("time").strip()),
                "frame": detect_match.group("frame").strip(),
                "box": detect_match.group("box").strip(),
                "score": detect_match.group("score").strip(),
                "raw": line,
            }

        return None

    def _group_entries(self, entries):
        groups = []
        pending_detections = []

        for entry in entries:
            if entry["type"] == "detect":
                pending_detections.append(entry)
                continue

            if entry["type"] == "action":
                groups.append({
                    "type": "action_group",
                    "time": entry["time"],
                    "time_dt": entry["time_dt"],
                    "level": entry["level"],
                    "action": entry["action"],
                    "window": entry["window"],
                    "detections": pending_detections[:],
                    "action_raw": entry["raw"],
                    "detection_raw": [det["raw"] for det in pending_detections],
                })
                pending_detections.clear()

        if pending_detections:
            groups.append({
                "type": "detect_group",
                "time": pending_detections[-1]["time"],
                "time_dt": pending_detections[-1]["time_dt"],
                "detections": pending_detections[:],
                "detection_raw": [det["raw"] for det in pending_detections],
            })

        return groups

    def _parse_time(self, text):
        try:
            return datetime.strptime(text, "%d/%m/%Y %H:%M:%S")
        except Exception:
            return None

    def _delete_by_range(self):
        minutes = 30
        selection = self.cb_delete.currentText()
        if "1 giờ" in selection:
            minutes = 60
        elif "3 giờ" in selection:
            minutes = 180
        elif "24 giờ" in selection:
            minutes = 24 * 60

        if not QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn muốn xóa dữ liệu trong {minutes} phút gần nhất?",
        ) == QMessageBox.StandardButton.Yes:
            return

        cutoff = datetime.now() - timedelta(minutes=minutes)
        self._delete_lines_after(cutoff)

    def _delete_entry(self, entry):
        if not QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn muốn xóa mục này không?",
        ) == QMessageBox.StandardButton.Yes:
            return

        raw_lines = []
        raw_lines.extend(entry.get("detection_raw", []))
        action_raw = entry.get("action_raw")
        if action_raw:
            raw_lines.append(action_raw)

        if raw_lines:
            self._delete_specific_lines(raw_lines)

    def _delete_specific_lines(self, raw_lines):
        log_path = get_log_path()
        if not log_path.exists():
            return

        existing = log_path.read_text(encoding="utf-8").splitlines()
        raw_set = set(raw_lines)
        kept = [line for line in existing if line not in raw_set]
        log_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
        self.load_logs()

    def _delete_lines_after(self, cutoff):
        log_path = get_log_path()
        if not log_path.exists():
            return

        kept = []
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("---") or not line.strip():
                kept.append(line)
                continue

            entry = self._parse_line(line)
            if entry and entry.get("time_dt") and entry["time_dt"] >= cutoff:
                continue
            kept.append(line)

        log_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
        self.load_logs()


class LogCard(QFrame):
    def __init__(self, entry, on_delete):
        super().__init__()
        self.entry = entry
        self.on_delete = on_delete
        self.setStyleSheet(
            "QFrame { background-color: #1e293b; border: 2px solid #334155; border-radius: 10px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = self._build_title(entry)
        subtitle = self._build_subtitle(entry)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)

        self.btn_toggle = QToolButton()
        self.btn_toggle.setText(title)
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setChecked(False)
        self.btn_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.btn_toggle.clicked.connect(self._toggle_details)
        self.btn_toggle.setStyleSheet(
            "QToolButton { color: #e2e8f0; font-weight: 600; font-size: 12px; text-align: left; }"
        )
        header.addWidget(self.btn_toggle)
        header.addStretch()

        self.btn_delete = QToolButton()
        self.btn_delete.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.btn_delete.setToolTip("Xóa mục này")
        self.btn_delete.clicked.connect(self._confirm_delete)
        self.btn_delete.setStyleSheet(
            "QToolButton { color: #f97316; padding: 2px; }"
            "QToolButton:hover { color: #fb923c; }"
        )
        header.addWidget(self.btn_delete)

        layout.addLayout(header)

        self.lbl_subtitle = QLabel(subtitle)
        self.lbl_subtitle.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.lbl_subtitle)

        self.lbl_details = QLabel(self._build_details(entry))
        self.lbl_details.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setVisible(False)
        layout.addWidget(self.lbl_details)

    def _toggle_details(self):
        expanded = self.btn_toggle.isChecked()
        self.btn_toggle.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.lbl_details.setVisible(expanded)

    def _confirm_delete(self):
        if self.on_delete:
            self.on_delete(self.entry)

    def _build_title(self, entry):
        if entry["type"] == "action_group":
            return f"Cấp độ {entry['level']} - {entry['action']}"
        count = len(entry.get("detections", []))
        return f"AI phát hiện - {count} khung hình"

    def _build_subtitle(self, entry):
        return f"[{entry['time']}]"

    def _build_details(self, entry):
        detections = entry.get("detections", [])
        detection_lines = []
        for det in detections:
            detection_lines.append(
                f"Khung hình: {det['frame']} | Tọa độ: {det['box']} | Độ chính xác: {det['score']}%"
            )

        if entry["type"] == "action_group":
            header = f"Cửa sổ: {entry['window']}"
            if detection_lines:
                return "\n".join([header, "---"] + detection_lines)
            return header

        return "\n".join(detection_lines) if detection_lines else "(Không có khung hình)"