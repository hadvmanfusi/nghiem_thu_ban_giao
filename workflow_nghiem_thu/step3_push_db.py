import os
from supabase import create_client, Client

# Cấu hình Supabase (đảm bảo bro đã set biến môi trường hoặc điền đúng URL/Key)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ffdywmzxkeoxrbaouxdg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_6gme6H2qh4oZ8VbG8y2hlQ_OH7UAKix")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def push_to_supabase(jobs):
    if not jobs:
        print("ℹ️ Không có dữ liệu để đẩy lên Supabase.")
        return

    print(f"💾 Đang đẩy {len(jobs)} bản ghi lên Supabase...")

    # Chuẩn hóa dữ liệu trước khi đẩy, dùng .get() để tránh KeyError 'details' hay bất kỳ key nào khác
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append(
            {
                "job_id": job.get("job_id"),
                "job_title": job.get("job_title"),
                "assignee": job.get("assignee"),
                "phone": job.get("phone"),
                "status_time": job.get("status_time"),
                "tagline_info": job.get("tagline_info"),
                "stage_name": job.get("stage_name", "Nghiệm thu và bàn giao"),
                # Thêm các trường khác nếu table của bro cần:
                # "details": job.get("details", "") # dùng .get() safe-guard không lo cào thiếu
            }
        )

    try:
        # Thực hiện Upsert dựa trên job_id
        response = (
            supabase.table("jobs")
            .upsert(formatted_jobs, on_conflict="job_id")
            .execute()
        )

        print(
            f"✅ Đẩy dữ liệu lên Supabase Cloud thành công! ({len(response.data)} bản ghi)"
        )

    except Exception as e:
        # Bắt exception an toàn, in ra thông báo lỗi gốc mà không bị dính KeyError 'details'
        print(f"❌ Lỗi khi làm việc với Supabase: {str(e)}")