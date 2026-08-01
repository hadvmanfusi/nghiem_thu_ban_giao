import os
import sys
import time
import random
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.sync_api import sync_playwright

# Đảm bảo Python nhận đúng các module trong cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from step1_login import login_and_get_page
from step2_scrape import scrape_nghiem_thu_ban_giao
from step3_push_db import push_to_supabase

# ==========================================
# 1. DUMMY SERVER CHO RENDER HEALTH CHECK
# (Sửa lỗi 'No open ports detected')
# ==========================================
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot Nghiem Thu is healthy and running!")
        def log_message(self, format, *args):
            return  # Tắt log HTTP thừa

    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Bật HTTP server ngầm
threading.Thread(target=run_dummy_server, daemon=True).start()

# ==========================================
# 2. CẤU HÌNH KHUNG GIỜ UTC (Tương đương 6h - 22h VN)
# ==========================================
# VN: 06:00 - 22:00  ===>  UTC: 23:00 (đêm trước) - 15:00 (chiều)
START_UTC_HOUR = 23
END_UTC_HOUR = 15

def is_working_hours():
    """Kiểm tra khung giờ làm việc theo giờ UTC máy chủ"""
    now_hour = datetime.now().hour
    return now_hour >= START_UTC_HOUR or now_hour < END_UTC_HOUR

def run_single_pipeline():
    """
    Chạy 1 chu kỳ độc lập: Khởi tạo -> Cào -> Push DB -> ĐÓNG BROWSER GIẢI PHÓNG RAM
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==================================================")
    print(f"🚀 [{current_time} UTC] BẮT ĐẦU CHẠY ĐỒNG BỘ DỰ ÁN")
    print(f"==================================================")

    browser = None
    try:
        with sync_playwright() as p:
            # Mở trình duyệt & đăng nhập
            browser, page = login_and_get_page(p)

            print("🔄 Đang làm mới trang...")
            page.reload(wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # 1. Cào dữ liệu
            jobs = scrape_nghiem_thu_ban_giao(page)

            # 2. Đẩy lên Supabase (hàm push_to_supabase của bro)
            push_to_supabase(jobs)

            print("🏁 Hoàn thành chu kỳ đồng bộ dữ liệu!")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra trong quá trình xử lý: {e}")

    finally:
        # BẮT BUỘC ĐÓNG BROWSER MỖI LẦN CHẠY XONG ĐỂ XẢ RAM VỀ 0MB
        if browser:
            try:
                browser.close()
                print("🧹 Đã đóng trình duyệt & giải phóng RAM hoàn toàn!")
            except Exception:
                pass

def main():
    print(f"🤖 Bot Auto-Sync Supabase (Nghiệm Thu Bàn Giao) đã khởi động!")
    print(f"⏰ Khung giờ hoạt động: 23:00 - 15:00 UTC (Tương đương 06:00 - 22:00 giờ VN).\n")

    while True:
        if is_working_hours():
            # Chạy pipeline đơn (tự mở và tự xả RAM)
            run_single_pipeline()

            # Giảm tần suất cào: Nghỉ 18 - 21 phút (1100s - 1300s) vừa an toàn vừa tiết kiệm tài nguyên
            sleep_seconds = random.randint(120, 150)
            next_run = datetime.now() + timedelta(seconds=sleep_seconds)
            
            print(f"⏰ Lần cập nhật tiếp theo (UTC): {next_run.strftime('%H:%M:%S')}")
            print(f"💤 Tạm dừng {sleep_seconds} giây (Trạng thái rảnh RAM)...")
            time.sleep(sleep_seconds)

        else:
            now_str = datetime.now().strftime("%H:%M:%S")
            print(f"🌙 [{now_str} UTC] Đã ngoài giờ làm việc (nghỉ đêm).")
            print("💤 Đang ngủ... Kiểm tra lại sau 10 phút.")
            time.sleep(600)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng chương trình thủ công (Ctrl+C)!")
