import mss
from mss.exception import ScreenShotError
import numpy as np
import cv2
from nudenet import NudeDetector

from src.utils.paths import get_model_path

class VisionProcessor:
    def __init__(self):
        print("[*] Đang khởi động lõi AI Neural Network (Vision)...")
        self.vung_quet_ratio = 0.5
        self.zoom_factor = 2.5
        self.score_threshold = 0.5
        self.monitor_index = 1
        model_path = get_model_path()
        if model_path.exists():
            self.detector = NudeDetector(str(model_path))
        else:
            print("[!] Khong tim thay model tai assets/models, dung model mac dinh.")
            self.detector = NudeDetector()
        
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[self.monitor_index]
        
        self.danh_sach_den = [
            "FEMALE_GENITALIA_COVERED", "FACE_FEMALE", "BUTTOCKS_EXPOSED",
            "FEMALE_BREAST_EXPOSED", "FEMALE_GENITALIA_EXPOSED", "MALE_BREAST_EXPOSED",
            "ANUS_EXPOSED", "FEET_EXPOSED", "BELLY_COVERED", "FEET_COVERED",
            "ARMPITS_COVERED", "ARMPITS_EXPOSED", "FACE_MALE", "BELLY_EXPOSED",
            "MALE_GENITALIA_EXPOSED", "ANUS_COVERED", "FEMALE_BREAST_COVERED",
            "BUTTOCKS_COVERED",
        ]

    def set_monitor_index(self, monitor_index):
        try:
            index = int(monitor_index)
        except Exception:
            index = 1

        if index < 0:
            index = 1
        if index >= len(self.sct.monitors):
            index = 1

        self.monitor_index = index
        self.monitor = self.sct.monitors[self.monitor_index]

    def quet_man_hinh_chi_tiet(self):
        """Chụp màn hình, xử lý siêu nét và trả về (co_nguy_hiem, ket_qua)."""
        self.vung_quet_ratio = min(0.9, max(0.1, float(self.vung_quet_ratio)))
        self.zoom_factor = min(4.0, max(1.0, float(self.zoom_factor)))
        try:
            sct_img = self.sct.grab(self.monitor)
        except ScreenShotError as exc:
            raise RuntimeError("screen_grab_failed") from exc
        img_array = np.array(sct_img)[:, :, :3]

        h, w, _ = img_array.shape
        c_h, c_w = h // 2, w // 2

        vung_cao = max(10, int(h * self.vung_quet_ratio / 2))
        vung_rong = max(10, int(w * self.vung_quet_ratio * 0.8 / 2))

        top = max(0, c_h - vung_cao)
        bottom = min(h, c_h + vung_cao)
        left = max(0, c_w - vung_rong)
        right = min(w, c_w + vung_rong)

        anh_loi = img_array[top:bottom, left:right]

        anh_zoom = cv2.resize(
            anh_loi,
            None,
            fx=self.zoom_factor,
            fy=self.zoom_factor,
            interpolation=cv2.INTER_LANCZOS4,
        )

        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        anh_sac_net = cv2.filter2D(anh_zoom, -1, kernel)

        lab = cv2.cvtColor(anh_sac_net, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        anh_cuoi_cung = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        results = self.detector.detect(anh_cuoi_cung)
        vi_pham = [
            res
            for res in results
            if res['class'] in self.danh_sach_den and res['score'] > self.score_threshold
        ]

        co_nguy_hiem = len(vi_pham) > 0
        return co_nguy_hiem, vi_pham