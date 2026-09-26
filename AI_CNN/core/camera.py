"""
camera.py — Quản lý kết nối camera (IP Webcam / DroidCam / webcam laptop).

Nhiệm vụ:
    - Bọc cv2.VideoCapture, tự động reconnect khi mất kết nối.
    - Set CAP_PROP_BUFFERSIZE=1 để giảm delay (IP camera rất quan trọng).

Input:  URL camera (từ config.CAMERAS)
Output: frame (numpy array) hoặc None nếu mất frame

Ai dùng:
    - worker.py gọi camera.read() mỗi vòng lặp.

Tại sao cần class riêng:
    - cv2.VideoCapture gốc KHÔNG tự reconnect khi mất WiFi → script chết.
    - IP camera buffer mặc định rất lớn → delay 1-2s nếu không set buffer=1.

Test riêng:
    - Rút WiFi 10s → cắm lại → script phải tự phục hồi, không crash.
"""
import cv2
import time


class CameraStream:
    """
    Bọc cv2.VideoCapture với 2 tính năng quan trọng:
        1. Tự động reconnect khi mất kết nối (không crash script)
        2. Set buffer=1 để giảm delay (IP camera)
    """

    # === Hằng số cấu hình ===
    MAX_RECONNECT_ATTEMPTS = 5      # Số lần thử reconnect liên tiếp
    RECONNECT_DELAY_SEC = 2         # Chờ bao lâu giữa 2 lần thử (giây)
    READ_RETRY_DELAY_SEC = 0.05     # Chờ bao lâu khi read() fail (giây)

    def __init__(self, url: str, name: str = "camera", is_webcam: bool = False):
        """
        Khởi tạo camera stream.

        Args:
            url: URL camera (VD: "http://192.168.1.10:8080/video")
                 Hoặc index webcam (VD: "0", "1")
            name: Tên hiển thị trong log (VD: "khu1", "webcam-laptop")
            is_webcam: True nếu là webcam laptop
        """
        self.url = url
        self.name = name
        self.is_webcam = is_webcam
        self.cap = None
        self._reconnect_fail_count = 0
        self._open()

    # ============================================================
    # METHOD NỘI BỘ — Mở / Reconnect camera
    # ============================================================
    def _open(self) -> bool:
        """
        Mở (hoặc mở lại) kết nối camera.

        Returns:
            True nếu mở thành công, False nếu thất bại.
        """
        # Đóng camera cũ (nếu có) trước khi mở cái mới
        if self.cap is not None:
            self.cap.release()

        # Chọn backend phù hợp với loại camera
        if self.is_webcam:
            cam_index = int(self.url)
            # ⚠️ FIX: KHÔNG hard-code CAP_DSHOW (lỗi trên máy AMD).
            # Thử lần lượt 3 backend — cái nào chạy được thì dùng.
            #   1. Default     — OpenCV tự chọn (thường OK nhất)
            #   2. CAP_MSMF    — Media Foundation (Windows 8+)
            #   3. CAP_DSHOW   — DirectShow (fallback cuối)
            self.cap = cv2.VideoCapture(cam_index)

            if not self.cap.isOpened():
                print(f"[{self.name}] Thử backend MSMF...")
                self.cap = cv2.VideoCapture(cam_index, cv2.CAP_MSMF)

            if not self.cap.isOpened():
                print(f"[{self.name}] Thử backend DSHOW...")
                self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        else:
            # IP camera — dùng FFMPEG để decode H.264/MJPEG ổn định
            self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

        # Kiểm tra mở thành công không
        if not self.cap.isOpened():
            print(f"[{self.name}] ❌ Không mở được camera: {self.url}")
            self.cap = None
            return False

        # ⚠️ QUAN TRỌNG: Set buffer = 1
        # Mặc định cv2 giữ nhiều frame cũ trong buffer → read() trả frame cũ
        # → AI nhận frame của 1-2 giây trước → xử lý sai
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Log thông tin camera (resolution, FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)

        print(f"[{self.name}] ✅ Đã kết nối camera — {width}x{height} @ {fps:.1f} FPS")

        # Reset bộ đếm fail khi mở thành công
        self._reconnect_fail_count = 0
        return True

    def _reconnect(self) -> bool:
        """
        Thử mở lại camera với retry logic.
        """
        self._reconnect_fail_count += 1

        if self._reconnect_fail_count > self.MAX_RECONNECT_ATTEMPTS:
            print(f"[{self.name}] 🚨 Reconnect thất bại {self.MAX_RECONNECT_ATTEMPTS} lần liên tiếp")
            print(f"[{self.name}]    → Kiểm tra: WiFi? Camera bật chưa? IP đúng chưa?")
            self._reconnect_fail_count = 0

        time.sleep(self.RECONNECT_DELAY_SEC)
        print(f"[{self.name}] 🔄 Đang thử reconnect (lần {self._reconnect_fail_count})...")
        return self._open()

    # ============================================================
    # API CÔNG KHAI — Dùng từ bên ngoài
    # ============================================================
    def read(self):
        """
        Đọc 1 frame từ camera.
        """
        if self.cap is None:
            self._reconnect()
            return None

        ret, frame = self.cap.read()

        if not ret or frame is None:
            print(f"[{self.name}] ⚠️  Mất frame — thử reconnect")
            self.cap.release()
            self.cap = None
            time.sleep(self.READ_RETRY_DELAY_SEC)
            self._reconnect()
            return None

        self._reconnect_fail_count = 0
        return frame

    def release(self):
        """Đóng camera sạch khi tắt script."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print(f"[{self.name}] 🔌 Đã đóng camera")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# ============================================================
# TEST RIÊNG — Chạy khi gọi `python core/camera.py`
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        cam_source = "0"
        is_webcam = True
        print("📷 Test webcam laptop (index 0)")
        print("   (Để test IP camera: python core/camera.py <url>)")
    elif sys.argv[1].startswith("http"):
        cam_source = sys.argv[1]
        is_webcam = False
        print(f"📷 Test IP camera: {cam_source}")
    else:
        cam_source = sys.argv[1]
        is_webcam = True
        print(f"📷 Test webcam laptop (index {cam_source})")

    cam = CameraStream(url=cam_source, name="test", is_webcam=is_webcam)

    frame_count = 0
    start_time = time.time()
    fps_display = 0.0

    print("\n▶️  Bắt đầu đọc frame. Nhấn 'q' để thoát.\n")

    try:
        while True:
            frame = cam.read()

            if frame is None:
                continue

            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

            cv2.putText(
                frame,
                f"FPS: {fps_display:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
            )

            cv2.imshow(f"Camera Test - {cam.name}", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n⚠️  Ctrl+C — thoát")
    finally:
        cam.release()
        cv2.destroyAllWindows()
        print("✅ Đã thoát sạch")