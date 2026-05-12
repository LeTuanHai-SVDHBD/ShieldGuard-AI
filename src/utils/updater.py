import requests
import json
from tkinter import messagebox

# URL đến file version.json trên server của bạn
# Thay thế bằng URL thật khi bạn có
VERSION_URL = "https://raw.githubusercontent.com/your_username/your_repo/main/version.json"

def get_current_version():
    """Đọc phiên bản hiện tại từ file config.json."""
    try:
        with open("data/config.json", "r") as f:
            config = json.load(f)
            return config.get("version", "0.0.0")
    except FileNotFoundError:
        return "0.0.0"

def check_for_updates():
    """
    Kiểm tra phiên bản mới từ server và thông báo cho người dùng.
    """
    try:
        response = requests.get(VERSION_URL, timeout=5)
        response.raise_for_status()  # Báo lỗi nếu request không thành công (4xx, 5xx)

        server_info = response.json()
        latest_version = server_info.get("latest_version")
        download_url = server_info.get("download_url")
        changelog = server_info.get("changelog", "Không có thông tin thay đổi.")

        current_version = get_current_version()

        # So sánh phiên bản (đơn giản, có thể cần thư viện phức tạp hơn như packaging)
        if latest_version and latest_version > current_version:
            show_update_notification(latest_version, changelog, download_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi kiểm tra cập nhật: {e}")
    except json.JSONDecodeError:
        print("Lỗi: Không thể phân tích file version.json từ server.")

def show_update_notification(version, changelog, url):
    """
    Hiển thị cửa sổ thông báo có bản cập nhật mới.
    """
    title = f"Có bản cập nhật mới: {version}"
    message = f"Đã có phiên bản {version}!\n\n"
    message += f"Thay đổi:\n{changelog}\n\n"
    message += "Bạn có muốn tải về ngay bây giờ không?"

    # Sử dụng messagebox của tkinter để hiển thị thông báo
    # (Trong ứng dụng customtkinter, bạn có thể tạo một dialog tùy chỉnh đẹp hơn)
    should_update = messagebox.askyesno(title, message)

    if should_update:
        # Mở trình duyệt để người dùng tải file
        import webbrowser
        webbrowser.open(url)

if __name__ == '__main__':
    # Đây là phần để bạn chạy thử nghiệm độc lập
    # Tạo một file version.json giả trên máy để test
    mock_server_info = {
        "latest_version": "1.1.0",
        "download_url": "https://example.com/download/new_version.exe",
        "changelog": "- Sửa lỗi crash khi mở camera.\n- Tăng tốc độ nhận diện."
    }
    # Ghi file version.json giả
    with open("version.json", "w", encoding="utf-8") as f:
        json.dump(mock_server_info, f, ensure_ascii=False, indent=2)
    
    # Thay đổi URL để trỏ đến file giả trên máy
    import pathlib
    VERSION_URL = pathlib.Path("version.json").as_uri()

    print("Đang kiểm tra cập nhật (dùng file giả lập)...")
    check_for_updates()
    print("Kiểm tra hoàn tất.")
