import datetime
import time
from pathlib import Path

from src.utils.paths import get_log_path

class StatsLogger:
    def __init__(self, log_file=None):
        if log_file is None:
            log_file = get_log_path()
        self.log_file = Path(log_file)
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0

    def tinh_fps(self):
        """Tính toán số khung hình trên giây (FPS)"""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1.0: # Cập nhật FPS mỗi giây
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
        return round(self.fps, 2)

    def ghi_log(self, detections):
        """Ghi dữ liệu vi phạm vào file txt"""
        # detections là danh sách các kết quả từ AI: [{'box':..., 'score':...}]
        bay_gio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("--- NHẬT KÝ HỆ THỐNG BẢO VỆ ---\n")

        with open(self.log_file, "a", encoding="utf-8") as f:
            for det in detections:
                box = det['box'] # [x, y, w, h]
                accuracy = round(det['score'] * 100, 2)
                
                # Chỉ ghi log nếu độ chính xác trên 40% như bạn yêu cầu
                if accuracy >= 40:
                    log_msg = (f"[{bay_gio}] | Khung hình: {self.frame_count} "
                               f"| Tọa độ: {box} | Độ chính xác: {accuracy}%\n")
                    f.write(log_msg)

    def ghi_hanh_dong(self, cap_do, hanh_dong, ten_cua_so):
        bay_gio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("--- NHẬT KÝ HỆ THỐNG BẢO VỆ ---\n")

        with open(self.log_file, "a", encoding="utf-8") as f:
            log_msg = (
                f"[{bay_gio}] | Cấp độ: {cap_do} | Hành động: {hanh_dong} "
                f"| Cửa sổ: {ten_cua_so}\n"
            )
            f.write(log_msg)