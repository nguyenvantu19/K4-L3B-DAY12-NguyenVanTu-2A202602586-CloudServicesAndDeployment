# CP2 — build dependencies separately from the small runtime image.
FROM python:3.11-slim AS builder
# Giải thích dòng trước: stage builder dùng Python slim để cài thư viện, không phải stage chạy ứng dụng.

WORKDIR /build
# Giải thích dòng trước: đặt thư mục làm việc riêng cho quá trình cài dependency.

COPY requirements.txt ./requirements.txt
# Giải thích dòng trước: copy riêng danh sách thư viện để Docker tái sử dụng cache khi source thay đổi.

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
# Giải thích dòng trước: cài thư viện vào /install để chỉ chuyển phần cần thiết sang runtime.

FROM python:3.11-slim AS runtime
# Giải thích dòng trước: tạo stage cuối gọn nhẹ, không mang theo công cụ build của builder.

ENV PYTHONDONTWRITEBYTECODE=1
# Giải thích dòng trước: tránh tạo file bytecode .pyc không cần thiết trong container.

ENV PYTHONUNBUFFERED=1
# Giải thích dòng trước: đẩy log Python ra stdout ngay lập tức để Docker thu thập được.

WORKDIR /app
# Giải thích dòng trước: đặt thư mục chạy ứng dụng.

COPY --from=builder /install /usr/local
# Giải thích dòng trước: chỉ chép các thư viện đã cài, không chép toàn bộ stage builder.

COPY app ./app
# Giải thích dòng trước: chép package ứng dụng sau bước cài thư viện để giữ cache dependency.

COPY utils ./utils
# Giải thích dòng trước: chép module mock LLM mà app.main import lúc khởi động.

RUN groupadd --system app && useradd --system --gid app --create-home app
# Giải thích dòng trước: tạo tài khoản hệ thống riêng để process không chạy dưới quyền root.

USER app
# Giải thích dòng trước: chạy các lệnh khởi động và ứng dụng bằng tài khoản giới hạn quyền.

EXPOSE 8000
# Giải thích dòng trước: ghi nhận cổng mặc định; cổng thực tế khi chạy lấy từ biến PORT.

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD ["python", "-c", "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/health',timeout=2)"]
# Giải thích dòng trước: Docker gọi /health theo PORT và đánh dấu container không khỏe nếu request lỗi.

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
# Giải thích dòng trước: đọc PORT lúc chạy, còn exec giúp Uvicorn nhận tín hiệu dừng trực tiếp.
