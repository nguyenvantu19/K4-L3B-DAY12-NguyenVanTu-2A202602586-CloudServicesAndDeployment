# Hướng dẫn hoàn thành CP5 — Cloud Deployment

> Tài liệu này diễn giải các yêu cầu CP5 trong `CHECKPOINTS.md` và cách nộp trong `DEPLOYMENT.md`/`LAB_GUIDE.md`. Mục tiêu là có service chạy bằng HTTPS công khai, kết nối Redis, biến môi trường an toàn và bằng chứng kiểm tra.

## 1. Kiểm tra trước khi deploy

- [ ] CP1–CP4 đã làm xong và các test tương ứng đã chạy qua.
- [ ] Docker Desktop đang chạy; Dockerfile CP2 đã build được.
- [ ] Repo có tên theo mẫu yêu cầu của môn học và đã được push lên GitHub.
- [ ] `.env` có trong `.gitignore`; chỉ commit `.env.example`, tuyệt đối không commit `.env`.
- [ ] Đã chuẩn bị một API key mạnh dành cho service trên cloud. Không dùng key mẫu trong `.env.example`.

Có thể tạo key mới trên máy bằng lệnh sau. Hãy đưa kết quả trực tiếp vào phần quản lý secret của platform; đừng dán kết quả vào repo hay tài liệu:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))" # Tạo khóa ngẫu nhiên đủ dài cho AGENT_API_KEY.
```

## 2. Deploy bằng Render

Repo đã có `render.yaml` làm Blueprint để Render tạo web service và Redis. Làm theo các bước sau:

1. Push repo cá nhân lên GitHub; đảm bảo `render.yaml`, `Dockerfile` và các thay đổi CP1–CP4 đã được đẩy lên.
2. Đăng nhập Render, chọn **New → Blueprint** rồi kết nối tài khoản GitHub nếu được yêu cầu.
3. Chọn repository của bài lab. Render sẽ đọc `render.yaml` và hiển thị các resource sẽ tạo: web service `day12-agent` và Redis `day12-redis`.
4. Xem lại cấu hình rồi tạo Blueprint. Vì `AGENT_API_KEY` được đánh dấu `sync: false`, nhập key mạnh đã tạo ở bước 1 khi Render yêu cầu. Không commit key vào repo.
5. Chờ Render tạo Redis, build Docker image và deploy web service. Mở mục **Events** hoặc **Logs** nếu có bước thất bại.
6. Trong trang Environment của web service, kiểm tra các biến `AGENT_API_KEY`, `REDIS_URL`, `RATE_LIMIT_PER_MINUTE`, `MONTHLY_BUDGET_USD` và `LOG_LEVEL` đã được thiết lập. `render.yaml` khai báo sẵn các biến này và nối `REDIS_URL` tới Redis service.
7. Để Render quản lý cổng `PORT`; không đặt cố định cổng `8000` trên cloud.
8. Khi service deploy thành công, mở trang service và sao chép URL HTTPS công khai. URL này sẽ dùng ở phần kiểm tra và trong `DEPLOYMENT.md`.

Chỉ nhập secret trong prompt hoặc dashboard Render. Không đưa giá trị API key vào source code, `render.yaml`, `DEPLOYMENT.md` hay ảnh chụp màn hình.

## 3. Kiểm tra service đang chạy

Thay domain mẫu bằng URL service thật, không thêm dấu `/` ở cuối. Các lệnh dưới đây dùng `curl.exe` để tránh bí danh `curl` trong một số phiên bản PowerShell:

```powershell
$Url = "https://ten-service-cua-ban.example" # Đặt URL HTTPS công khai của service.
curl.exe -i "$Url/health" # Mong đợi HTTP 200 và JSON có status=ok; đây là liveness.
curl.exe -i "$Url/ready" # Mong đợi HTTP 200 và status=ready; điều này xác nhận Redis kết nối được.
curl.exe -i -X POST "$Url/ask" -H "Content-Type: application/json" --data '{"question":"Hello"}' # Mong đợi HTTP 401 vì chưa gửi API key.
```

`/health` kiểm tra process còn chạy. `/ready` kiểm tra service có thể nhận traffic, bao gồm khả năng kết nối Redis. `/ask` không có key phải trả `401`; đó là hành vi bảo mật mong đợi.

## 4. Hoàn thiện `DEPLOYMENT.md`

Mở `DEPLOYMENT.md` và thay toàn bộ nội dung mẫu bằng thông tin thật:

- Họ tên, mã học viên và link repo.
- Public URL HTTPS và tên platform.
- Ngày deploy.
- Tên các biến môi trường đã cấu hình và nguồn của chúng, **không ghi giá trị secret**.
- Output kiểm tra `/health`, `/ready` và `/ask` không có key.
- Nếu cần kiểm tra `/ask` có key, có thể ghi lại HTTP status và phần phản hồi đã loại bỏ thông tin nhạy cảm.

Xóa mọi chỗ còn `(điền ...)` hoặc URL mẫu `TODO...`. Test CP5 sẽ không đạt khi tài liệu còn chỗ trống. Không ghi `AGENT_API_KEY=<giá trị thật>`; chỉ liệt kê tên biến và đánh dấu đã set.

## 5. Chạy test CP5

Để test đầy đủ cả request có xác thực, thêm key của **service đã deploy** vào file `.env` cục bộ, file này đã được Git bỏ qua:

```dotenv
DEPLOY_API_KEY=<key-dang-dung-tren-cloud> # Thay bằng AGENT_API_KEY của service; chỉ lưu trong .env cục bộ.
```

Sau đó chạy test từ thư mục gốc:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_cp5.py -v # Kiểm tra tài liệu, HTTPS, health, readiness và API đã deploy.
```

Test gọi service thật qua Internet. Nếu bỏ trống `DEPLOY_API_KEY`, riêng bài kiểm tra `/ask` có key sẽ tự bỏ qua; các kiểm tra còn lại vẫn chạy.

## 6. Chụp ảnh minh chứng

Lưu ảnh trong thư mục `screenshots/`:

- `dashboard.png` — dashboard platform, thể hiện service đã deploy; che hoặc không mở phần hiển thị giá trị secret.
- `health.png` — kết quả gọi URL công khai `/health`; có thể thêm ảnh `/ready` để thể hiện Redis đã nối.

Không để API key xuất hiện trong ảnh, terminal, log hoặc tài liệu đã commit.

## 7. Nếu không thể deploy cloud

Checkpoint cho phép phương án local, nhưng điểm CP5 tối đa **9/15**. Cần có Docker đang chạy:

1. Trong `.env` cục bộ, đặt `LOCAL_FALLBACK=true`.
2. Đảm bảo `AGENT_API_KEY` có giá trị dùng được và `REDIS_URL` phù hợp với Compose.
3. Khởi động stack và xem trạng thái:

```powershell
docker compose up -d # Khởi động agent và Redis ở máy local.
docker compose ps # Xác nhận container đang chạy/healthy.
curl.exe -i http://localhost:8000/health # Xác nhận endpoint health trả HTTP 200.
curl.exe -i http://localhost:8000/ready # Xác nhận agent nối được Redis và trả HTTP 200.
```

4. Chụp ảnh `docker compose ps` và kết quả gọi endpoint, lưu trong `screenshots/`.
5. Ghi rõ lý do dùng fallback trong `DEPLOYMENT.md`; không để dòng hướng dẫn `(điền lý do...)` nguyên trạng.
6. Chạy lại `tests/test_cp5.py -v`; chế độ fallback sẽ kiểm tra `http://localhost:8000` và yêu cầu có ít nhất một ảnh trong `screenshots/`.

## 8. Xử lý lỗi thường gặp

| Triệu chứng | Việc cần kiểm tra |
|---|---|
| Build thất bại | Mở Build Logs của Render; kiểm tra Dockerfile, dependency và lỗi cấu hình Blueprint. |
| App thoát ngay khi khởi động | Kiểm tra `AGENT_API_KEY` đã được đặt trong Environment của web service; ứng dụng cố ý dừng nếu thiếu secret. |
| `/health` không trả 200 | Xem Events/Logs, trạng thái deploy và URL service; đợi hoàn tất cold start nếu service vừa thức dậy. |
| `/ready` trả 503 | Kiểm tra Redis resource đã tạo và `REDIS_URL` đang tham chiếu tới `day12-redis`. |
| `/ask` có key vẫn trả 401 | So sánh key gửi đi với `AGENT_API_KEY` trên cloud; dùng cùng key và không có khoảng trắng thừa. |
| Test báo chưa điền thông tin | Tìm và thay toàn bộ URL mẫu, `TODO` và các chỗ `(điền ...)` trong `DEPLOYMENT.md`. |
| Test không gọi được URL | Kiểm tra URL HTTPS, service còn hoạt động và mạng cho phép kết nối ra ngoài. |

## Checklist hoàn tất CP5

- [ ] URL HTTPS công khai hoạt động.
- [ ] `/health` trả 200 và `/ready` trả 200.
- [ ] `/ask` không có key trả 401; test có key chạy qua nếu đã cấu hình `DEPLOY_API_KEY`.
- [ ] `AGENT_API_KEY` và `REDIS_URL` được cấu hình trên platform, không lưu trong repo.
- [ ] `DEPLOYMENT.md` đã điền đủ và không còn placeholder.
- [ ] Ảnh minh chứng đã lưu trong `screenshots/`.
- [ ] `pytest tests/test_cp5.py -v` đã chạy và kết quả đã được xem lại.
