import re
from playwright.sync_api import Page


def scrape_nghiem_thu_ban_giao(page: Page):
    """
    Cào dữ liệu các công việc thuộc cột 'Xác nhận hoàn thành với khách hàng' (stage-118754)
    của Bảng QT Xử lý sự cố.
    """
    print("🔍 Đang cào dữ liệu từ cột 'Xác nhận hoàn thành với khách hàng'...")

    # Selector của cột 'Xác nhận hoàn thành với khách hàng' trong QT Sự cố
    stage_selector = "#stage-118754"
    
    try:
        page.wait_for_selector(stage_selector, timeout=15000)
    except Exception:
        print(f"⚠️ Không tìm thấy cột với selector {stage_selector}")
        return []

    # Lấy tất cả các thẻ công việc (.item hoặc .--job-wrapper) trong cột
    job_elements = page.query_selector_all(
        f"{stage_selector} .items .--job-wrapper"
    )
    print(f"📊 Tìm thấy {len(job_elements)} công việc trong cột.")

    jobs_data = []

    for job_el in job_elements:
        try:
            # 1. Lấy Job ID (từ data-id)
            job_id = job_el.get_attribute("data-id")

            # 2. Lấy Tên công việc / Tên dự án
            name_el = job_el.query_selector(".name")
            job_title = name_el.inner_text().strip() if name_el else ""

            # 3. Lấy Nội dung sự cố (Tagline)
            tagline_el = job_el.query_selector(".tagline")
            tagline_text = tagline_el.inner_text().strip() if tagline_el else ""

            # 4. Lấy danh sách Tag phân loại lỗi (gap, loithietbi, loikhachhang...)
            tag_list_attr = job_el.get_attribute("data-taglist") or ""
            tags = tag_list_attr.split() if tag_list_attr else []
            
            # Nếu data-taglist rỗng thì fallback tìm trong DOM .ui-tag
            if not tags:
                tag_els = job_el.query_selector_all(".ui-tags .ui-tag")
                tags = [t.inner_text().strip() for t in tag_els if t.inner_text().strip()]

            # 5. Lấy Người xử lý / Phụ trách (Assignee)
            uname_el = job_el.query_selector(".uname")
            assignee = uname_el.inner_text().strip() if uname_el else ""

            # 6. Lấy Thời hạn / Deadline
            time_el = job_el.query_selector(".time")
            status_time = time_el.inner_text().strip() if time_el else ""

            # 7. Lấy URL chi tiết job (https://workflow.base.vn/job/3849077)
            url_el = job_el.query_selector(".name.url")
            raw_url = url_el.get_attribute("data-url") if url_el else ""
            job_url = ""
            if raw_url:
                clean_path = raw_url.replace(":job/", "job/").replace("/open_job", "")
                job_url = f"https://workflow.base.vn/{clean_path}"

            # Tạo dict dữ liệu chuẩn
            job_item = {
                "job_id": job_id,
                "job_title": job_title,
                "assignee": assignee,
                "status_time": status_time,
                "tagline_info": tagline_text,
                "tags": tags,                     # Thêm mảng danh sách các tag lỗi
                "url": job_url,                   # Thêm link trực tiếp đến job
                "stage_name": "Xác nhận hoàn thành với khách hàng",
            }

            jobs_data.append(job_item)

        except Exception as e:
            print(f"⚠️ Lỗi khi parse 1 item công việc: {e}")
            continue

    print(
        f"✅ Đã trích xuất thành công {len(jobs_data)} công việc Sự cố."
    )
    return jobs_data