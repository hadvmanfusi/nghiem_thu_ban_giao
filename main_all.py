import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# Import các hàm từ 2 thư mục con
from workflow_nghiem_thu.step1_login import login_and_get_page as login_nghiem_thu
from workflow_nghiem_thu.step2_scrape import scrape_nghiem_thu_ban_giao
from workflow_nghiem_thu.step3_push_db import push_to_supabase as push_nghiem_thu

from workflow_su_co.step1_login import login_and_get_page as login_su_co
from workflow_su_co.step2_scrape import scrape_nghiem_thu_ban_giao as scrape_su_co
from workflow_su_co.step3_push_db import push_jobs_to_supabase as push_su_co

START_HOUR = 7   # 7h sáng
END_HOUR = 21    # 21h tối

def is_working_hours():
    now = datetime.now()
    return START_HOUR <= now.hour < END_HOUR

def run_pipeline(page_nt, page_sc):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n==================================================")
    print(f"🚀 [{current_time}] BẮT ĐẦU CHẠY ĐỒNG BỘ CẢ 2 BẢNG WORKFLOW")
    print(f"==================================================")

    # 1. Chạy Luồng Nghiệm Thu Bàn Giao
    try:
        print("\n🔄 [1/2] Đang làm mới & cào Bảng Nghiệm Thu...")
        page_nt.reload(wait_until="domcontentloaded")
        page_nt.wait_for_timeout(2000)
        jobs_nt = scrape_nghiem_thu_ban_giao(page_nt)
        push_nghiem_thu(jobs_nt)
    except Exception as e:
        print(f"❌ Lỗi luồng Nghiệm Thu: {e}")

    # 2. Chạy Luồng Xử Lý Sự Cố
    try:
        print("\n🔄 [2/2] Đang làm mới & cào Bảng Sự Cố...")
        page_sc.reload(wait_until="domcontentloaded")
        page_sc.wait_for_timeout(2000)
        jobs_sc = scrape_su_co(page_sc)
        push_su_co(jobs_sc)
    except Exception as e:
        print(f"❌ Lỗi luồng Sự Cố: {e}")

    print("\n🏁 Hoàn thành 1 chu kỳ đồng bộ cho cả 2 bảng!")

def main():
    print(f"🤖 Bot Auto-Sync Supabase (All-in-One) đã khởi động!")
    print(f"⏰ Khung giờ hoạt động: {START_HOUR}:00 - {END_HOUR}:00 hàng ngày.\n")

    with sync_playwright() as p:
        print("🔐 Đang đăng nhập luồng Nghiệm Thu...")
        browser_nt, page_nt = login_nghiem_thu(p)
        
        print("🔐 Đang đăng nhập luồng Sự Cố...")
        browser_sc, page_sc = login_su_co(p)

        try:
            while True:
                if is_working_hours():
                    run_pipeline(page_nt, page_sc)

                    sleep_seconds = random.randint(110, 130)
                    next_run = datetime.now() + timedelta(seconds=sleep_seconds)
                    print(f"⏰ Lần cập nhật tiếp theo: {next_run.strftime('%H:%M:%S')}")
                    print(f"💤 Tạm dừng {sleep_seconds} giây...\n")
                    time.sleep(sleep_seconds)
                else:
                    now_str = datetime.now().strftime("%H:%M:%S")
                    print(f"🌙 [{now_str}] Đã ngoài giờ làm việc (sau {END_HOUR}h). Tạm nghỉ 10 phút...")
                    time.sleep(600)

        finally:
            browser_nt.close()
            browser_sc.close()
            print("🔒 Đã đóng toàn bộ trình duyệt an toàn.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng chương trình thủ công!")
