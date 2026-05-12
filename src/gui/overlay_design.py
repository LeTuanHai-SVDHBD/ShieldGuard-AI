from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCore import Qt

def ve_giao_dien_che(painter, w, h, margin_h, cap_do):
    rect_x = 0
    rect_y = margin_h
    rect_w = w
    rect_h = h - (2 * margin_h)
    
    # --- THIẾT LẬP THÔNG SỐ THEO CẤP ĐỘ ---
    if cap_do == 1:
        bg_color = QColor(10, 10, 10, 255) # Đen tuyền
        border_color = QColor(255, 140, 0, 200) # Viền cam
        border_w = 8
        font_tieu_de = QFont("Impact", 45)
        font_phu = QFont("Consolas", 20)
        tieu_de = "⚠️ CẢNH BÁO VI PHẠM LẦN 1 ⚠️"
        phu = "PHÁT HIỆN NỘI DUNG 18+ VUI LÒNG ĐÓNG TAB NGAY LẬP TỨC!\nHỆ THỐNG ĐANG THEO DÕI!"
        color_tieu_de = QColor(255, 140, 0, 255)
        color_phu = QColor(200, 200, 200, 255)
        
    elif cap_do == 2:
        bg_color = QColor(25, 5, 5, 255) # Nền đen pha chút đỏ tối (ngột ngạt)
        border_color = QColor(255, 50, 50, 255) # Viền đỏ gắt
        border_w = 15
        font_tieu_de = QFont("Impact", 60)
        font_phu = QFont("Consolas", 25, QFont.Weight.Bold)
        tieu_de = "🚫 CẢNH BÁO VI PHẠM LẦN 2 🚫"
        phu = "HỆ THỐNG ĐANG GHI NHẬN HÀNH VI!\nHÃY DỪNG LẠI TRƯỚC KHI QUÁ MUỘN!\nCẤP ĐỘ NGUY HIỂM ĐANG TĂNG CAO!"
        color_tieu_de = QColor(255, 50, 50, 255)
        color_phu = QColor(255, 150, 150, 255)
        
    else: # cap_do >= 3 (Cấp độ cao nhất, áp đảo hoàn toàn)
        bg_color = QColor(60, 0, 0, 255) # Nền đỏ máu tối
        border_color = QColor(255, 0, 0, 255) # Viền đỏ tươi cực gắt
        border_w = 30 # Viền cực dày
        font_tieu_de = QFont("Impact", 85)
        font_phu = QFont("Consolas", 35, QFont.Weight.Bold)
        tieu_de = "🛑 CẢNH BÁO VI PHẠM LẦN 3 🛑"
        phu = "BẠN ĐÃ CỐ TÌNH VI PHẠM NHIỀU LẦN!\nTẤT CẢ DỮ LIỆU SẼ BỊ LƯU VẾT BÁO CÁO!"
        color_tieu_de = QColor(255, 255, 255, 255) # Chữ trắng toát trên nền đỏ
        color_phu = QColor(255, 180, 180, 255)

    # 1. Vẽ nền (Đen -> Đỏ tối -> Đỏ máu)
    painter.fillRect(rect_x, rect_y, rect_w, rect_h, bg_color)
    
    # 2. Vẽ viền cảnh báo (Dày dần lên)
    pen = QPen(border_color)
    pen.setWidth(border_w)
    painter.setPen(pen)
    # Thụt vào một chút để viền không bị cắt lẹm
    offset = border_w // 2
    painter.drawRect(rect_x + offset, rect_y + offset, rect_w - border_w, rect_h - border_w)
    
    # 3. Thêm Text Tiêu đề chính
    painter.setPen(color_tieu_de)
    painter.setFont(font_tieu_de)
    painter.drawText(
        rect_x, rect_y, rect_w, rect_h // 2, 
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, 
        tieu_de
    )
                     
    # 4. Thêm Text Phụ 
    painter.setPen(color_phu)
    painter.setFont(font_phu)
    painter.drawText(
        rect_x, rect_y + (rect_h // 2) + 20, rect_w, rect_h // 2, 
        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, 
        phu
    )