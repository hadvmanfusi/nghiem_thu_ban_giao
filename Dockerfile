FROM mcr.microsoft.com/playwright/python:v1.62.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render tự cấp biến $PORT, nếu không có sẽ lấy mặc định 10000
ENV PORT=10000
EXPOSE 10000

# Dùng CMD để vừa chạy http.server báo port cho Render, vừa chạy main_all.py
CMD ["python", "-u", "workflow_su_co/main.py"]
