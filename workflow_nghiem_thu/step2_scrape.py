import re
from playwright.sync_api import Page


def scrape_nghiem_thu_ban_giao(page: Page):
    """
    Cào dữ liệu các công việc thuộc cột 'Nghiệm thu và bàn giao' (stage-88609)
    """
    print("🔍 Đang cào dữ liệu từ cột 'Nghiệm thu và bàn giao'...")

    # Chờ cột 'Nghiệm thu và bàn giao' (stage-88609) xuất hiện trên DOM
    stage_selector = "#stage-88609"
    page.wait_for_selector(stage_selector, timeout=15000)

    # Lấy tất cả các thẻ công việc (job items) nằm trong cột này
    job_elements = page.query_selector_all(
        f"{stage_selector} .items .--job-wrapper"
    )
    print(f"📊 Tìm thấy {len(job_elements)} công việc trong cột.")

    jobs_data = []

    for job_el in job_elements:
        try:
            # 1. Lấy Job ID (ưu tiên lấy từ attribute data-id)
            job_id = job_el.get_attribute("data-id")

            # 2. Lấy Tên dự án/công việc
            name_el = job_el.query_selector(".name")
            job_title = name_el.inner_text().strip() if name_el else ""

            # 3. Lấy thông tin tagline (Khu vực, SĐT, Nguồn...)
            tagline_el = job_el.query_selector(".tagline")
            tagline_text = tagline_el.inner_text().strip() if tagline_el else ""

            # Trích xuất số điện thoại từ tagline (nếu cần tách riêng)
            phone = ""
            phone_match = re.search(r"Số điện thoại:\s*(\d+)", tagline_text)
            if phone_match:
                phone = phone_match.group(1)

            # 4. Lấy Người thực hiện / Phụ trách (Assignee)
            uname_el = job_el.query_selector(".uname")
            assignee = uname_el.inner_text().strip() if uname_el else ""

            # 5. Lấy Trạng thái thời gian / Hạn chót
            time_el = job_el.query_selector(".time")
            status_time = time_el.inner_text().strip() if time_el else ""

            # Tạo dict dữ liệu chuẩn để đẩy sang step3 (Supabase)
            job_item = {
                "job_id": job_id,
                "job_title": job_title,
                "assignee": assignee,
                "phone": phone,
                "status_time": status_time,
                "tagline_info": tagline_text,
                "stage_name": "Nghiệm thu và bàn giao",
            }

            jobs_data.append(job_item)

        except Exception as e:
            print(f"⚠️ Lỗi khi parse 1 item công việc: {e}")
            continue

    print(
        f"✅ Đã trích xuất thành công {len(jobs_data)} công việc Nghiệm thu & Bàn giao."
    )
    return jobs_data