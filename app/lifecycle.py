"""CP4 — Graceful shutdown.

Khi bạn deploy phiên bản mới, orchestrator (Docker, Railway, Cloud Run, K8s)
gửi **SIGTERM** rồi đợi vài chục giây trước khi SIGKILL. Nếu app bỏ qua tín
hiệu đó, mọi request đang xử lý dở bị cắt giữa chừng — user thấy lỗi 502 mỗi
lần bạn deploy.

Ứng xử đúng: nhận SIGTERM → báo "tôi sắp tắt" qua health check để load
balancer ngừng đẩy traffic mới vào → xử lý nốt request đang chạy → thoát.
"""

from __future__ import annotations

import signal


class Lifecycle:
    """Giữ trạng thái vòng đời của process."""

    def __init__(self) -> None:
        self.shutting_down = False
        # Handler đã được đăng ký trước ta (của uvicorn) — xem install()
        self._previous: dict = {}

    def request_shutdown(self, signum=None, frame=None) -> None:
        """Signal handler: đánh dấu process đang tắt dần.

        TODO (CP4):
          1. ``self.shutting_down = True``
          2. Gọi lại handler cũ nếu có::

                previous = self._previous.get(signum)
                if callable(previous):
                    previous(signum, frame)

        Bước 2 quan trọng hơn vẻ ngoài của nó. Mỗi tín hiệu chỉ có **một**
        handler: đăng ký handler của mình là ghi đè handler của uvicorn — thứ
        chịu trách nhiệm thật sự cho việc dừng server. Không gọi lại nó thì
        app bật cờ "đang tắt" rồi... chạy tiếp mãi mãi, cho tới khi
        orchestrator hết kiên nhẫn và SIGKILL. Đúng cái mà graceful shutdown
        định tránh.

        Chữ ký ``(signum, frame)`` là bắt buộc vì Python gọi handler với 2
        tham số này. Không làm gì nặng ở đây (không gọi mạng, không ghi file)
        — handler chạy xen giữa bytecode.
        """
        self.shutting_down = True  # Báo cho health/readiness probe ngừng đưa traffic mới vào instance.
        previous = self._previous.get(signum)  # Tìm signal handler đã được đăng ký trước handler của ứng dụng.
        if callable(previous):  # Chỉ chuyển tiếp nếu handler cũ có thể được gọi như hàm.
            previous(signum, frame)  # Cho Uvicorn hoặc handler nền tảng thực hiện quy trình dừng server.

    def install(self) -> None:
        """Đăng ký handler cho SIGTERM và SIGINT, nhớ lại handler cũ.

        TODO (CP4): với mỗi tín hiệu trong ``(signal.SIGTERM, signal.SIGINT)``:

            self._previous[sig] = signal.getsignal(sig)   # nhớ handler cũ
            signal.signal(sig, self.request_shutdown)     # rồi mới ghi đè

        SIGTERM: orchestrator yêu cầu tắt. SIGINT: bạn bấm Ctrl+C.
        """
        for sig in (signal.SIGTERM, signal.SIGINT):  # Theo dõi cả tín hiệu dừng từ orchestrator và Ctrl+C.
            self._previous[sig] = signal.getsignal(sig)  # Lưu handler hiện tại để có thể chuyển tiếp sau này.
            signal.signal(sig, self.request_shutdown)  # Đăng ký handler ứng dụng để bật cờ shutdown.


# Một instance dùng chung cho cả app
lifecycle = Lifecycle()
