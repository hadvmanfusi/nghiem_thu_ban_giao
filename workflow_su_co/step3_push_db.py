import os
from supabase import create_client, Client

# Cấu hình Supabase (đảm bảo bro đã set biến môi trường hoặc điền đúng URL/Key)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ffdywmzxkeoxrbaouxdg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_6gme6H2qh4oZ8VbG8y2hlQ_OH7UAKix")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def push_jobs_to_supabase(jobs_data: list):
    """
    Đẩy danh sách công việc sự cố lên bảng 'thong_tin_su_co' trên Supabase.
    Sử dụng upsert dựa trên khoá chính/duy nhất là 'job_id'.
    """
    if not jobs_data:
        print("⚠️ Không có dữ liệu để đẩy lên Supabase.")
        return

    print(f"🚀 Bắt đầu đẩy {len(jobs_data)} bản ghi lên Supabase bảng 'thong_tin_su_co'...")

    success_count = 0
    fail_count = 0

    for job in jobs_data:
        try:
            # Format dữ liệu khớp với cấu trúc bảng thong_tin_su_co
            payload = {
                "job_id": job.get("job_id"),
                "job_title": job.get("job_title"),
                "assignee": job.get("assignee"),
                "status_time": job.get("status_time"),
                "tagline_info": job.get("tagline_info"),
                "tags": job.get("tags", []),           # Mảng danh sách các tag
                "url": job.get("url"),
                "stage_name": job.get("stage_name"),
            }

            # Thực hiện Upsert (Tránh trùng lặp theo job_id)
            response = (
                supabase.table("thong_tin_su_co")
                .upsert(payload, on_conflict="job_id")
                .execute()
            )

            if response.data:
                success_count += 1
            else:
                print(f"⚠️ Không nhận được phản hồi khi ghi job_id: {job.get('job_id')}")

        except Exception as e:
            print(f"❌ Lỗi khi ghi job_id {job.get('job_id')} vào Supabase: {e}")
            fail_count += 1

    print(f"✅ Hoàn thành! Đã đẩy thành công: {success_count}/{len(jobs_data)} bản ghi.")
    if fail_count > 0:
        print(f"❌ Thất bại: {fail_count} bản ghi.")


if __name__ == "__main__":
    # Test thử gửi dữ liệu mẫu
    sample_data = [
        {
            "job_id": "3849077",
            "job_title": "Hà Nam- Lại Văn Thật- Sự cố pin",
            "assignee": "Nguyễn Như Quỳnh",
            "status_time": "Không thời hạn",
            "tagline_info": "Nội dung sự cố: Lỗi pin...",
            "tags": ["gap", "loithietbi"],
            "url": "https://workflow.base.vn/job/3849077",
            "stage_name": "Xác nhận hoàn thành với khách hàng",
        }
    ]
    push_jobs_to_supabase(sample_data)