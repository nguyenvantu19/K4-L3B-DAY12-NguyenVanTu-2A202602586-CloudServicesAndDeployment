# Thông tin Deploy — Checkpoint 5

> Platform được chọn là Render. URL public được kiểm tra ngày 29/09/2026; không ghi giá trị `AGENT_API_KEY` vào file này, ảnh chụp, log hoặc repository.

## Thông tin học viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Nguyễn Văn Tứ |
| Mã học viên | 2A202602586 |
| Repo |https://github.com/nguyenvantu19/K4-L3B-DAY12-NguyenVanTu-2A202602586-CloudServicesAndDeployment.git |

## Service Render

| Mục | Trạng thái |
|---|---|
| Platform | Render |
| Blueprint | `render.yaml` — web service `day12-agent` và Key Value `day12-redis` |
| Public URL | https://day12-agent.onrender.com/ |
| Ngày deploy | 29/09/2026 |
| Tình trạng | Đã kiểm tra `/health`, `/ready` và xác thực `/ask` không có key |

## Environment dự kiến trên Render

Các biến được khai báo hoặc tham chiếu trong `render.yaml`. Kết quả `/ready` thành công xác nhận service sẵn sàng và dependency được kiểm tra bởi endpoint đang hoạt động.

| Biến | Nguồn / cấu hình | Trạng thái |
|---|---|---|
| `PORT` | Render cấp lúc chạy; ứng dụng đọc biến này | Không cần đặt thủ công |
| `AGENT_API_KEY` | Secret trong Environment của Render | `/ask` không key trả HTTP 401; key cục bộ hiện bị Render từ chối, cần đồng bộ lại |
| `REDIS_URL` | Kết nối Redis/Key Value do Render cấp | `/ready` trả HTTP 200 với `ready=true` |
| `RATE_LIMIT_PER_MINUTE` | `10` trong `render.yaml` | Đã khai báo trong Blueprint |
| `MONTHLY_BUDGET_USD` | `10.0` trong `render.yaml` | Đã khai báo trong Blueprint |
| `LOG_LEVEL` | `INFO` trong `render.yaml` | Đã khai báo trong Blueprint |

## Kiểm tra sau khi Render deploy

Các lệnh PowerShell dưới đây gọi URL Render thật. Mỗi dòng có giải thích và kết quả mong đợi:

```powershell
$Url = "https://day12-agent.onrender.com" # URL HTTPS public do chủ repo cung cấp.
curl.exe -i "$Url/health" # Mong đợi HTTP 200 với status=ok.
curl.exe -i "$Url/ready" # Mong đợi HTTP 200 với status=ready và Redis hoạt động.
curl.exe -i -X POST "$Url/ask" -H "Content-Type: application/json" --data '{"question":"Hello"}' # Mong đợi HTTP 401 vì request không có API key.
```

Kiểm tra trực tiếp ngày 29/09/2026:

| Request | HTTP | Kết quả |
|---|---:|---|
| `GET /health` | 200 | `status=ok`, `version=1.0.0`, `environment=production` |
| `GET /ready` | 200 | `ready=true` |
| `POST /ask` không có API key | 401 | Bị từ chối xác thực như mong đợi |
| `POST /ask` có API key | 401 | Key cục bộ đã gửi nhưng Render từ chối; cần đồng bộ với `AGENT_API_KEY` đang hoạt động trên Render |
| Rate limit | Chưa kiểm tra | Cần xác nhận bằng request có key |
| `pytest tests/test_cp5.py -v` | 8 passed, 1 failed, 4 skipped | Bài xác thực có key thất bại vì Render trả HTTP 401; 4 bài fallback bị bỏ qua vì đang dùng Render |

Lần chạy có `DEPLOY_API_KEY` đã gửi key qua HTTPS, nhưng service trả HTTP 401. Đối chiếu biến `AGENT_API_KEY` trong Environment của Render với `DEPLOY_API_KEY` trong `.env` cục bộ. Hai giá trị phải giống nhau; sau khi cập nhật giá trị đúng trên Render, redeploy service rồi chạy lại test. Không ghi key vào file này hoặc gửi key qua chat.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_cp5.py -v # Test sẽ gọi URL trong file này và kiểm tra service thật qua Internet.
```

Test CP5 kiểm tra URL, health, readiness và xác thực. Lần chạy ngày 29/09/2026 đạt 8 bài, 1 bài xác thực có key thất bại với HTTP 401, còn 4 bài fallback bị bỏ qua vì đang dùng Render. Cần đồng bộ `DEPLOY_API_KEY` với secret đang hoạt động trên Render và chạy lại test.

## Ảnh chụp màn hình

Đã có ảnh minh chứng CP5 trong `screenshots/`. Sau khi deploy, lưu:

- `screenshots/dashboard.png` — Render dashboard hiển thị service đã deploy; không để lộ secret.
- `screenshots/health.png` — kết quả gọi `/health` trên URL HTTPS công khai; nên chụp thêm `/ready` để chứng minh Redis đã nối.

## Bằng chứng còn lại

- [ ] URL HTTPS public có phản hồi; health, readiness và xác thực không key đã được kiểm tra.
- [ ] Đồng bộ `DEPLOY_API_KEY` cục bộ với `AGENT_API_KEY` trong Render Environment, redeploy, rồi xác nhận `/ask` có key trả 200.
- [ ] Xác nhận rate limit bằng các request đã xác thực.
- [ ] Chạy lại `pytest tests/test_cp5.py -v` đến khi bài có key đạt.
- [ ] Lưu ảnh dashboard và health vào `screenshots/`.
- [ ] Kiểm tra `DEPLOYMENT.md` không chứa giá trị API key trước khi commit.
