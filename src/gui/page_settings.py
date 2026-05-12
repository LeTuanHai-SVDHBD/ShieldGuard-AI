import json

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSlider,
    QGroupBox,
    QHBoxLayout,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QToolButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.utils.paths import APP_NAME, get_assets_dir, get_config_path, get_default_config_path
from src.utils.windows_startup import set_startup

class PageSettings(QWidget):
    settings_saved = pyqtSignal()
    def __init__(self, core_app):
        super().__init__()
        self.core = core_app  # Kết nối trực tiếp với core_app để cập nhật thông số
        self.config_path = get_config_path()
        self.load_config()
        self.last_timer_interval = self.core.timer_interval

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(15)

        # --- TIÊU ĐỀ ---
        lbl_title = QLabel("⚙️ CẤU HÌNH HỆ THỐNG")
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #89b4fa;")
        layout.addWidget(lbl_title)

        # --- NHÓM 1: HIỆU NĂNG (MẠNH/YẾU) ---
        gp_perf = QGroupBox("Hiệu năng & Tốc độ")
        gp_perf.setStyleSheet("QGroupBox { color: #f5e0dc; font-weight: bold; }")
        perf_layout = QVBoxLayout()

        self.cb_perf = QCheckBox("Bật chỉnh hiệu năng")
        self.cb_perf.setChecked(False)
        self.cb_perf.toggled.connect(self.toggle_perf_controls)
        perf_layout.addWidget(self.cb_perf)

        # Tốc độ quét
        self.lbl_timer = QLabel(f"Tốc độ quét: {self.core.timer_interval} ms (Thấp = Nhanh/Nặng máy)")
        self.sd_timer = self.create_slider(200, 2000, self.core.timer_interval)
        self.sd_timer.valueChanged.connect(self.change_timer)
        self.sd_timer.setEnabled(False)
        perf_layout.addWidget(self.lbl_status_label(self.lbl_timer, self.sd_timer))

        # Thời gian giữ khung
        self.lbl_hold = QLabel(f"Thời gian giữ khung che: {self.core.thoi_gian_giu} nhịp")
        self.sd_hold = self.create_slider(5, 50, self.core.thoi_gian_giu)
        self.sd_hold.valueChanged.connect(self.change_hold)
        self.sd_hold.setEnabled(False)
        perf_layout.addWidget(self.lbl_status_label(self.lbl_hold, self.sd_hold))

        gp_perf.setLayout(perf_layout)

        # --- NHÓM 2: CẤU HÌNH QUÉT CHI TIẾT (TẦM NHÌN) ---
        gp_vision = QGroupBox("Cấu hình Tầm nhìn AI (Vùng trung tâm)")
        gp_vision.setStyleSheet("QGroupBox { color: #a6e3a1; font-weight: bold; }")
        vision_layout = QVBoxLayout()

        self.cb_vision = QCheckBox("Bật chỉnh tầm nhìn AI")
        self.cb_vision.setChecked(False)
        self.cb_vision.toggled.connect(self.toggle_vision_controls)
        vision_layout.addWidget(self.cb_vision)

        # Giải thích phần này
        lbl_info_vision = QLabel("ℹ️ Điều chỉnh vùng AI tập trung quan sát ở giữa màn hình.")
        lbl_info_vision.setStyleSheet("color: #9399b2; font-style: italic;")
        vision_layout.addWidget(lbl_info_vision)

        # Vùng quét (Diện tích)
        self.lbl_area = QLabel(f"Độ rộng vùng quét: {int(self.core.vision.vung_quet_ratio * 100)}%")
        self.sd_area = self.create_slider(10, 90, int(self.core.vision.vung_quet_ratio * 100))
        self.sd_area.valueChanged.connect(self.change_area)
        self.sd_area.setEnabled(False)
        vision_layout.addWidget(self.lbl_status_label(self.lbl_area, self.sd_area))

        # Độ phóng đại (Zoom)
        self.lbl_zoom = QLabel(f"Độ phóng đại: {self.core.vision.zoom_factor:.1f}x")
        self.sd_zoom = self.create_slider(10, 40, int(self.core.vision.zoom_factor * 10))
        self.sd_zoom.valueChanged.connect(self.change_zoom)
        self.sd_zoom.setEnabled(False)
        vision_layout.addWidget(self.lbl_status_label(self.lbl_zoom, self.sd_zoom))

        gp_vision.setLayout(vision_layout)

        # --- NHÓM 3: ĐỘ CHÍNH XÁC ---
        gp_acc = QGroupBox("Độ tin cậy AI")
        gp_acc.setStyleSheet("QGroupBox { color: #fab387; font-weight: bold; }")
        acc_layout = QVBoxLayout()

        self.cb_acc = QCheckBox("Bật chỉnh độ tin cậy")
        self.cb_acc.setChecked(False)
        self.cb_acc.toggled.connect(self.toggle_acc_controls)
        acc_layout.addWidget(self.cb_acc)

        self.lbl_score = QLabel(f"Ngưỡng chặn: {int(self.core.vision.score_threshold * 100)}%")
        self.sd_score = self.create_slider(40, 60, int(self.core.vision.score_threshold * 100))
        self.sd_score.valueChanged.connect(self.change_score)
        self.sd_score.setEnabled(False)
        acc_layout.addWidget(self.lbl_status_label(self.lbl_score, self.sd_score))

        gp_acc.setLayout(acc_layout)

        # --- NHÓM 4: HỆ THỐNG & BẢO MẬT ---
        gp_pro = QGroupBox("Cài đặt Nâng cao")
        gp_pro.setStyleSheet("QGroupBox { color: #f2cdcd; font-weight: bold; }")
        pro_layout = QVBoxLayout()

        self.cb_startup = QCheckBox("Khởi động cùng Windows")
        self.cb_startup.setChecked(self.core.start_with_windows)
        pro_layout.addWidget(self.cb_startup)

        self.cb_tray = QCheckBox("Thu nhỏ xuống khay hệ thống khi đóng")
        self.cb_tray.setChecked(self.core.minimize_to_tray)
        pro_layout.addWidget(self.cb_tray)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Mật khẩu bảo vệ Setting:"))
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setPlaceholderText("Để trống nếu không dùng")
        self.txt_pass.setFixedWidth(160)
        self.txt_pass.setText(self.core.settings_password)
        pass_layout.addWidget(self.txt_pass)
        pass_layout.addStretch()
        pro_layout.addLayout(pass_layout)

        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("Phím tắt khẩn cấp:"))
        self.txt_hotkey = QLineEdit()
        self.txt_hotkey.setPlaceholderText("S+O+S")
        self.txt_hotkey.setFixedWidth(160)
        self.txt_hotkey.setText(self.core.emergency_hotkey)
        hotkey_layout.addWidget(self.txt_hotkey)
        hotkey_layout.addStretch()
        pro_layout.addLayout(hotkey_layout)

        gp_pro.setLayout(pro_layout)

        layout.addWidget(gp_perf)
        layout.addWidget(gp_vision)
        layout.addWidget(gp_acc)
        layout.addWidget(gp_pro)

        # --- NÚT LƯU CẤU HÌNH ---
        self.btn_save = QPushButton("💾 LƯU THAY ĐỔI")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setStyleSheet(
            "QPushButton { background-color: #fab387; color: #11111b; border-radius: 6px; }"
            "QPushButton:hover { background-color: #f9e2af; }"
        )
        self.btn_save.clicked.connect(self.save_config)
        layout.addWidget(self.btn_save)

        layout.addStretch()

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

        self.setStyleSheet(
            "QCheckBox { color: #e8eef7; }"
            "QCheckBox::indicator { width: 16px; height: 16px; }"
            "QLineEdit { color: #e8eef7; background-color: #0f1419; border: 1px solid #2b3340; border-radius: 6px; padding: 6px 8px; }"
            "QLineEdit:focus { border: 1px solid #3b82f6; }"
            "QComboBox { color: #e8eef7; background-color: #0f1419; border: 1px solid #2b3340; border-radius: 6px; padding: 6px 8px; }"
            "QComboBox QAbstractItemView { color: #e8eef7; background-color: #0f1419; selection-background-color: #1e293b; }"
            "QLabel { color: #e8eef7; }"
        )

        self._build_accordion(layout, gp_perf, gp_vision, gp_acc, gp_pro)

    def _build_accordion(self, parent_layout, *groups):
        self.section_buttons = []
        self.section_widgets = []

        parent_layout.insertSpacing(1, 8)
        for group in groups:
            title = group.title()
            group.setTitle("")

            btn = QToolButton()
            btn.setText(title)
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.setArrowType(Qt.ArrowType.RightArrow)
            btn.setStyleSheet(
                "QToolButton { color: #e8eef7; font-size: 13px; font-weight: 600; padding: 8px 6px; text-align: left; }"
                "QToolButton:hover { color: #cbd5e1; }"
            )

            index = parent_layout.indexOf(group)
            parent_layout.insertWidget(index, btn)

            self.section_buttons.append(btn)
            self.section_widgets.append(group)

            btn.clicked.connect(lambda checked, b=btn, g=group: self._toggle_section(b, g))
            group.setVisible(False)

        if self.section_buttons:
            self.section_buttons[0].setChecked(True)
            self.section_buttons[0].setArrowType(Qt.ArrowType.DownArrow)
            self.section_widgets[0].setVisible(True)

    def _toggle_section(self, active_button, active_group):
        for btn, group in zip(self.section_buttons, self.section_widgets):
            is_active = btn is active_button and active_button.isChecked()
            btn.setChecked(is_active)
            btn.setArrowType(Qt.ArrowType.DownArrow if is_active else Qt.ArrowType.RightArrow)
            group.setVisible(is_active)

    # --- HÀM HỖ TRỢ TẠO GIAO DIỆN NHANH ---
    def create_slider(self, min_v, max_v, cur_v):
        s = QSlider(Qt.Orientation.Horizontal)
        s.setRange(min_v, max_v)
        s.setValue(cur_v)
        return s

    def lbl_status_label(self, lbl, sd):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(lbl)
        l.addWidget(sd)
        return w

    # --- HÀM XỬ LÝ KHI NGƯỜI DÙNG KÉO SLIDER ---
    def change_timer(self, v):
        self.core.timer_interval = v
        if self.core.timer.isActive():
            self.core.timer.start(v)
        self.lbl_timer.setText(f"Tốc độ quét: {v} ms")
        if not self.cb_battery.isChecked():
            self.last_timer_interval = v

    def change_hold(self, v):
        self.core.thoi_gian_giu = v
        self.lbl_hold.setText(f"Thời gian giữ khung che: {v} nhịp")

    def change_area(self, v):
        self.core.vision.vung_quet_ratio = v / 100
        self.lbl_area.setText(f"Độ rộng vùng quét: {v}%")

    def change_zoom(self, v):
        self.core.vision.zoom_factor = v / 10
        self.lbl_zoom.setText(f"Độ phóng đại: {v / 10:.1f}x")

    def change_score(self, v):
        self.core.vision.score_threshold = v / 100
        self.lbl_score.setText(f"Ngưỡng chặn: {v}%")

    def toggle_perf_controls(self, enabled):
        self.sd_timer.setEnabled(enabled)
        self.sd_hold.setEnabled(enabled)

    def toggle_vision_controls(self, enabled):
        self.sd_area.setEnabled(enabled)
        self.sd_zoom.setEnabled(enabled)

    def toggle_acc_controls(self, enabled):
        self.sd_score.setEnabled(enabled)

    def _apply_timer_interval(self, value):
        self.sd_timer.blockSignals(True)
        self.sd_timer.setValue(value)
        self.sd_timer.blockSignals(False)
        self.change_timer(value)

    def _default_config(self):
        return {
            "timer_interval": 500,
            "thoi_gian_giu": 10,
            "vung_quet_ratio": 0.5,
            "zoom_factor": 2.5,
            "score_threshold": 0.5,
            "start_with_windows": False,
            "minimize_to_tray": True,
            "settings_password": "",
            "emergency_hotkey": "Ctrl+Alt+S",
            "sound_alert": False,
            "battery_saver": False,
            "monitor_index": 1,
        }

    def load_config(self):
        config = self._default_config()
        if self.config_path.exists():
            try:
                config.update(json.loads(self.config_path.read_text(encoding="utf-8")))
            except Exception:
                pass
        else:
            default_path = get_default_config_path()
            if default_path.exists():
                try:
                    config.update(json.loads(default_path.read_text(encoding="utf-8")))
                except Exception:
                    pass

        self.core.timer_interval = int(config["timer_interval"])
        self.core.thoi_gian_giu = int(config["thoi_gian_giu"])
        self.core.vision.vung_quet_ratio = float(config["vung_quet_ratio"])
        self.core.vision.zoom_factor = float(config["zoom_factor"])
        self.core.vision.score_threshold = float(config["score_threshold"])
        self.core.start_with_windows = bool(config["start_with_windows"])
        self.core.minimize_to_tray = bool(config["minimize_to_tray"])
        self.core.settings_password = str(config["settings_password"])
        self.core.emergency_hotkey = str(config["emergency_hotkey"])
        self.core.sound_alert = bool(config.get("sound_alert", False))
        self.core.battery_saver = bool(config.get("battery_saver", False))
        self.core.monitor_index = int(config.get("monitor_index", 1))

        if hasattr(self.core.vision, "set_monitor_index"):
            self.core.vision.set_monitor_index(self.core.monitor_index)

    def save_config(self):
        config = {
            "timer_interval": self.core.timer_interval,
            "thoi_gian_giu": self.core.thoi_gian_giu,
            "vung_quet_ratio": self.core.vision.vung_quet_ratio,
            "zoom_factor": self.core.vision.zoom_factor,
            "score_threshold": self.core.vision.score_threshold,
            "start_with_windows": self.cb_startup.isChecked(),
            "minimize_to_tray": self.cb_tray.isChecked(),
            "settings_password": self.txt_pass.text().strip(),
            "emergency_hotkey": self.txt_hotkey.text().strip(),
            "sound_alert": self.core.sound_alert,
            "battery_saver": self.core.battery_saver,
            "monitor_index": self.core.monitor_index,
        }

        self.core.start_with_windows = config["start_with_windows"]
        self.core.minimize_to_tray = config["minimize_to_tray"]
        self.core.settings_password = config["settings_password"]
        self.core.emergency_hotkey = config["emergency_hotkey"]
        self.core.sound_alert = config["sound_alert"]
        self.core.battery_saver = config["battery_saver"]
        self.core.monitor_index = config["monitor_index"]

        if hasattr(self.core.vision, "set_monitor_index"):
            self.core.vision.set_monitor_index(self.core.monitor_index)

        try:
            self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except Exception as exc:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu cấu hình: {exc}")
            return

        entry_point = (get_assets_dir().parent / "main.py").resolve()
        if not set_startup(config["start_with_windows"], APP_NAME, entry_point):
            QMessageBox.warning(self, "Cảnh báo", "Không thể cập nhật cấu hình khởi động cùng Windows.")

        QMessageBox.information(self, "Lưu cấu hình", "Đã lưu cấu hình người dùng!")
        self.settings_saved.emit()