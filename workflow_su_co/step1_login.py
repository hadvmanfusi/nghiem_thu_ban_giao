import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://workflow.base.vn/qtxulysuco-12626"
USERNAME = "ha.dv@manfusi.com"
PASSWORD = "RXZZL48Q4C"

def login_and_get_page(playwright_instance):
    print("--- KHỞI TẠO & ĐĂNG NHẬP BASE ---")
    
    # 1. Thêm cờ tối ưu RAM & chống crash trong Docker Container (Render)
    browser = playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            '--single-process',
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu"
            '--disable-render-backgrounding',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-component-extensions-with-background-pages',
        ]
    )
    
    # 2. Giả dạng User-Agent trình duyệt thật để không bị Base/Cloudflare block
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080},
        permissions=['notifications']
    )
    page = context.new_page()

    print("1. Đang mở trang Base Workflow...")
    # Tăng timeout và bọc try-except để xử lý chập chờn đường truyền mạng quốc tế
    try:
        page.goto(BASE_URL, wait_until="commit", timeout=90000)
    except Exception as e:
        print(f"Lần 1 goto chập chờn, thử lại... Chi tiết: {e}")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=90000)

    page.wait_for_timeout(3000)

    # Đăng nhập Email
    if "account.base.vn" in page.url or page.query_selector("input[name='email']"):
        print("2. Nhập Email...")
        page.wait_for_selector("input[name='email']", timeout=30000)
        page.fill("input[name='email']", USERNAME)
        page.wait_for_timeout(500)

        btn_ok = page.locator("div.ok").first
        if btn_ok.count() > 0 and btn_ok.is_visible():
            btn_ok.click()
        else:
            page.press("input[name='email']", "Enter")

        # Đăng nhập Mật khẩu
        print("3. Nhập Mật khẩu...")
        page.wait_for_selector("input[name='password']", timeout=30000)
        page.fill("input[name='password']", PASSWORD)
        page.wait_for_timeout(500)

        btn_login_ok = page.locator("div.ok").first
        if btn_login_ok.count() > 0 and btn_login_ok.is_visible():
            btn_login_ok.click()
        else:
            page.press("input[name='password']", "Enter")

        page.wait_for_url(lambda url: "workflow.base.vn" in url, timeout=45000)
        print("-> ✅ Đăng nhập thành công!")

    page.wait_for_timeout(3000)

    # Xử lý Popup
    print("4. Xử lý Popup thông báo...")
    popup_btn = page.locator("text='TIẾP TỤC'").first
    if popup_btn.count() > 0 and popup_btn.is_visible():
        popup_btn.click()
        print("-> ✅ Đã tắt Popup!")
    
    return browser, page
