import ctypes
import time
import winsound
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter
import pyautogui
import pygetwindow as gw

# Gọi module AI và Design từ trong thư mục src
from src.core.vision import VisionProcessor
from src.gui.overlay_design import ve_giao_dien_che
from src.core.stats_logger import StatsLogger

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

class KhungCheThongMinh(QWidget):
    def __init__(self):
        super().__init__()
        
        print("=====================================================")
        print("     HỆ THỐNG NHẬN DIỆN & BẢO VỆ NỘI DUNG 18+        ")
        print("         Phiên bản: 5.0 (Bộ Não 640m Xịn)           ")
        print("=====================================================")
        
        self.vision = VisionProcessor()
        self.timer_interval = 500 # Mặc định quét mỗi 500ms (2 lần mỗi giây)
        self.sound_alert = False
        self.dang_che = False
        self.bo_dem_giu_khung = 0
        self.thoi_gian_giu = 10 # Giữ 10 nhịp (~5 giây với timer 500ms)
        self.cap_do_vi_pham = 0
        self.stats_logger = StatsLogger()
        self.current_fps = 0
        self.grab_fail_count = 0
        self.max_grab_fail = 5

        self.thiet_lap_giao_dien()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.quet_va_xu_ly)
        print("[*] Hoàn tất! Đang giám sát màn hình ngầm.\n")

    def bat_dau(self):
        """Hàm này được gọi khi người dùng bấm Bắt Đầu trên Menu"""
        self.timer.start(self.timer_interval)
        self.show() # Hiện khung che trong suốt lên để chuẩn bị vẽ
        print(">>> HỆ THỐNG ĐÃ KÍCH HOẠT <<<")

    def dung_lai(self):
        """Hàm này được gọi khi người dùng bấm Dừng trên Menu"""
        self.timer.stop() # Dừng quét màn hình
        self.dang_che = False
        self.cap_do_vi_pham = 0
        self.update() # Xóa khung che trên màn hình (nếu đang có)
        self.hide() # Ẩn luôn cửa sổ ngầm đi
        print(">>> HỆ THỐNG ĐÃ TẠM DỪNG <<<")

    def thiet_lap_giao_dien(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.show()

    def quet_va_xu_ly(self):

        self.current_fps = self.stats_logger.tinh_fps()
        try:
            co_nguy_hiem, results = self.vision.quet_man_hinh_chi_tiet()
            # reset consecutive failure counter on success
            self.grab_fail_count = 0
        except RuntimeError as exc:
            if str(exc) == "screen_grab_failed":
                self.grab_fail_count += 1
                print(f"[!] Lỗi chụp màn hình ({self.grab_fail_count}/{self.max_grab_fail})")
                if self.grab_fail_count >= self.max_grab_fail:
                    self.dung_lai()
                    QMessageBox.warning(
                        self,
                        "Tạm dừng giám sát",
                        "Không thể chụp màn hình liên tục. Hệ thống đã tạm dừng để an toàn. Vui lòng kiểm tra và thử lại."
                    )
                return
            else:
                raise
        if co_nguy_hiem:
            self.stats_logger.ghi_log(results)
            if not self.dang_che:
                self.cap_do_vi_pham += 1
                if self.cap_do_vi_pham > 3: self.cap_do_vi_pham = 3

                if self.sound_alert:
                    self.phat_am_thanh_canh_bao(self.cap_do_vi_pham)
                
                # --- QUAN TRỌNG: GỌI HÀM THỰC THI Ở ĐÂY ---
                self.thuc_thi_ky_luat()
                print(f"[!] CẢNH BÁO CẤP {self.cap_do_vi_pham}: Thực thi kỷ luật!")
                
            self.dang_che = True
            self.bo_dem_giu_khung = 0 
        else:
            if self.dang_che:
                self.bo_dem_giu_khung += 1
                if self.bo_dem_giu_khung > self.thoi_gian_giu:
                    self.dang_che = False
                    self.bo_dem_giu_khung = 0
                    print(f"[✓] Đã an toàn.")
                    
        self.update()

    def phat_am_thanh_canh_bao(self, cap_do):
        try:
            if cap_do == 1:
                winsound.Beep(900, 160)
            elif cap_do == 2:
                winsound.Beep(1100, 220)
            else:
                winsound.Beep(1400, 300)
        except Exception as e:
            print(f"[-] Lỗi âm thanh: {e}")

    def thuc_thi_ky_luat(self):
        """Hàm can thiệp trực tiếp vào cửa sổ vi phạm"""
        try:
            # 1. Tạm ẩn khung che để không bị lấy nhầm Focus
            self.hide()
            time.sleep(0.1) 
            
            # 2. Lấy cửa sổ đang nằm trên cùng (thường là trình duyệt)
            cua_so_hien_tai = gw.getActiveWindow()
            
            # 3. Hiện lại khung che ngay lập tức
            self.show()

            if not cua_so_hien_tai:
                return

            ten_cua_so = cua_so_hien_tai.title or "(Khong ro tieu de)"

            if self.cap_do_vi_pham == 1:
                self.stats_logger.ghi_hanh_dong(1, "Canh bao", ten_cua_so)

            # CẤP ĐỘ 2: Thu nhỏ cửa sổ
            if self.cap_do_vi_pham == 2:
                self.stats_logger.ghi_hanh_dong(2, "Thu nho cua so", ten_cua_so)
                print(f"[ACTION] Cấp 2: Thu nhỏ cửa sổ '{cua_so_hien_tai.title}'")
                cua_so_hien_tai.minimize()

            # CẤP ĐỘ 3: Đóng tab / Đóng cửa sổ
            elif self.cap_do_vi_pham >= 3:
                print(f"[DANGER] Cấp 3: Đóng tab trên '{cua_so_hien_tai.title}'")
                ten_app = cua_so_hien_tai.title.lower()
                trinh_duyet = ["chrome", "edge", "firefox", "coccoc", "opera", "brave"]
                
                if any(web in ten_app for web in trinh_duyet):
                    self.stats_logger.ghi_hanh_dong(3, "Dong tab", ten_cua_so)
                    cua_so_hien_tai.activate() # Đảm bảo trình duyệt được chọn
                    pyautogui.hotkey('ctrl', 'w')
                else:
                    self.stats_logger.ghi_hanh_dong(3, "Dong cua so", ten_cua_so)
                    cua_so_hien_tai.close()
        except Exception as e:
            print(f"[-] Lỗi thực thi: {e}")
            self.show()

    def paintEvent(self, event):
        if not self.dang_che:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        
        w = self.width()
        h = self.height()
        # Chỉnh margin_h = 0 nếu muốn che kín hoàn toàn ở cấp độ 3
        margin_h = int(h * 0.05) if self.cap_do_vi_pham < 3 else 0
        
        ve_giao_dien_che(painter, w, h, margin_h, self.cap_do_vi_pham)