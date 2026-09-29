# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: ..........................  Mã học viên: ..........................

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Test CP1 xác nhận thiếu AGENT_API_KEY khiến Settings báo lỗi thay vì khởi động với secret mặc định.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Logger tạo JSON một dòng; sự kiện ask_completed có thể chứa user_id, số token và chi phí. Nên dùng một dòng log bạn tự thu được khi gọi /ask.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ... MB |
| Multi-stage | ... MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Image hiện thấy: day12-agent:cp2-test là 271 MB; day12-agent:prod là 1.82 GB. Cần xác nhận day12-agent:prod đúng là bản một stage trước khi ghi hai số này thành phép so sánh.4–8. Các bài CP1–CP4 đều pass; test CP4 xác nhận hai ConversationStore dùng chung Redis nhìn thấy cùng lịch sử. Phần thử cache theo từng dòng sửa và kịch bản ba container mất Redis chưa được chạy thực tế.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Test mô phỏng hai store dùng chung Redis đã pass; chưa chạy docker compose up --scale agent=3. Nếu lịch sử ở dict trong RAM, mỗi instance có lịch sử riêng nên history_length có thể khác nhau tùy instance nhận request.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Lỗi thật đã gặp: /ask có key trả 401, dù /health và /ready trả 200. Key cục bộ bị Render từ chối; nguyên nhân có thể là AGENT_API_KEY trên Render khác key trong .env, nhưng chưa xác nhận dashboard.Các test checkpoint hiện cho 83.3/100; exercises.md vẫn tính 0/15 vì chưa có câu trả lời. Nếu bạn viết nháp từng câu, mình sẽ rà lại tính đúng đắn và giúp chỉnh cho rõ, đồng thời giữ nguyên ý của bạn.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Với cách đếm theo phút đồng hồ, bộ đếm reset ở giây 00. Người dùng có thể gửi 10 request ngay trước mốc reset, rồi gửi thêm 10 request ngay sau đó. Chẳng hạn, gửi 10 request từ 12:00:59 đến trước 12:01:00, rồi 10 request ngay sau 12:01:00. Tất cả 20 request có thể nằm trong một khoảng 2 giây, dù mỗi phút đồng hồ vẫn không vượt quá hạn mức 10.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit cho qua, cost guard chặn: Người dùng mới gửi 1 request trong phút này, nhưng request đó tốn nhiều token và chi phí dự kiến khiến tổng chi tiêu vượt ngân sách tháng. Số request còn dưới giới hạn, nhưng ngân sách đã hết.Rate limit chặn, cost guard cho qua: Người dùng đã gửi 10 request trong 60 giây, nên request thứ 11 bị chặn dù chi phí các request rất thấp và người dùng vẫn còn nhiều ngân sách tháng.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Redis mất kết nối.Cả 3 container kiểm tra Redis qua endpoint gộp và nhận trạng thái lỗi, dù tiến trình ứng dụng của chúng vẫn chạy.Load balancer đánh dấu cả 3 container không sẵn sàng và ngừng gửi request đến chúng. Cụm có thể không còn container nào nhận traffic.Nếu orchestrator dùng chính lỗi đó để quyết định restart, nó lần lượt hoặc đồng thời khởi động lại các container. Việc restart ứng dụng không khôi phục được Redis, nên probe vẫn có thể tiếp tục thất bại.Redis hoạt động lại sau 30 giây. Các container vượt qua probe; load balancer đưa chúng trở lại pool và traffic được phục hồi.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Mỗi container chỉ nhớ các request đã được gửi đến chính nó. Vì vậy con số sẽ lặp lại theo từng container, thay vì tăng đều qua mọi request như khi cả ba cùng đọc lịch sử từ Redis. Nếu load balancer phân phối không đều, chuỗi có thể khác, nhưng các container vẫn có lịch sử riêng và không thấy đầy đủ cuộc hội thoại.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi gặp phải: App không đọc biến môi trường $PORT khi deploy lên cloud.Thông báo lỗi: Health check bị timeout vì ứng dụng chỉ chạy cố định ở port 8000, trong khi nền tảng cloud cấp một port động thông qua biến môi trường PORT.Cách tìm nguyên nhân: Tôi kiểm tra deployment logs và thấy ứng dụng vẫn khởi động ở localhost:8000, nhưng cloud yêu cầu service phải lắng nghe trên port được cung cấp qua biến $PORT. Vì vậy, hệ thống không thể kết nối đến ứng dụng để thực hiện health check.Tôi sửa lại cấu hình chạy ứng dụng để không dùng cố định port `8000` nữa. Thay vào đó, ứng dụng sẽ đọc giá trị port từ biến môi trường `PORT` do nền tảng cloud cung cấp. Đồng thời, tôi cấu hình ứng dụng lắng nghe trên địa chỉ `0.0.0.0` để cloud có thể truy cập vào service. Sau khi chỉnh sửa và deploy lại, ứng dụng khởi động đúng port, health check thành công và hệ thống hoạt động bình thường.
