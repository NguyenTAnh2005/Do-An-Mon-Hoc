"""
frame_diff.py — Lớp lọc nhiễu chống nhận nhầm khay trống (PA3).

Thuật toán: MOTION DETECTION (so sánh 2 frame liên tiếp)
    - So sánh frame hiện tại vs frame TRƯỚC ĐÓ (không dùng background)
    - Chỉ báo "có vật" khi phát hiện CỬ ĐỘNG (ai đặt vật xuống)
    - Giữ trạng thái "có vật" trong MOTION_HOLD_SEC giây sau cử động cuối
      → đủ để detector chốt kết quả

Tại sao dùng motion detection thay vì background subtraction:
    - Background subtraction bị "học" sai nếu warmup gặp cảnh không đúng
    - Motion detection ổn định hơn: chỉ quan tâm có thay đổi giữa các frame
    - Phù hợp use case: user đặt rác → có cử động → detect → chốt

Input:  frame (numpy array từ camera)
Output: True  = có cử động → cho YOLO chạy
        False = đứng yên → bỏ qua

Ai dùng: worker.py gọi TRƯỚC khi đưa frame cho detector.
"""
import sys
from pathlib import Path

# Thêm thư mục cha (AI_CNN/) vào sys.path → import được config.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import cv2
import numpy as np

from config import (
    DIFF_THRESH,
    DIFF_AREA_RATIO,
    DIFF_MIN_MOTION,
    DIFF_WARMUP,
)


class FrameDiffer:
    """
    Phát hiện cử động bằng cách so sánh 2 frame liên tiếp.

    Cách hoạt động:
        1. Warmup: Bỏ qua N frame đầu để camera ổn định
        2. Mỗi frame mới:
           - So sánh với frame trước đó (absdiff)
           - Đếm % pixel thay đổi
           - Nếu > ngưỡng → có cử động
        3. Giữ trạng thái "có vật" trong MOTION_HOLD_SEC giây
           → để detector kịp chốt kết quả
    """

    # Giữ trạng thái "có vật" bao lâu sau cử động cuối (giây)
    MOTION_HOLD_SEC = 2.0

    def __init__(self):
        """Khởi tạo FrameDiffer."""
        # Frame trước (grayscale, đã blur)
        self.prev_gray = None

        # Đếm số frame đã warmup
        self._warmup_count = 0

        # Đếm số frame liên tiếp có cử động
        self._motion_count = 0

        # Timestamp lần cuối phát hiện cử động
        self._last_motion_time = 0.0

        # Kernel morphology
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def has_object(self, frame) -> bool:
        """
        Kiểm tra frame có cử động hay không.

        Args:
            frame: numpy array (BGR từ cv2)

        Returns:
            True  = có cử động gần đây → cho YOLO chạy
            False = đứng yên → bỏ qua
        """
        # Bước 1: Chuyển grayscale + blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Bước 2: Warmup — bỏ qua N frame đầu để camera ổn định
        if self.prev_gray is None:
            self.prev_gray = gray
            self._warmup_count = 1
            return False

        if self._warmup_count < DIFF_WARMUP:
            self.prev_gray = gray
            self._warmup_count += 1
            return False

        # Bước 3: So sánh frame hiện tại với frame TRƯỚC ĐÓ
        diff = cv2.absdiff(self.prev_gray, gray)

        # Threshold: pixel khác > DIFF_THRESH → trắng
        _, thresh = cv2.threshold(diff, DIFF_THRESH, 255, cv2.THRESH_BINARY)

        # Morphology: xóa nhiễu muối tiêu
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, self.kernel)

        # Tính % pixel thay đổi
        changed_ratio = thresh.sum() / 255 / gray.size

        # Lưu frame hiện tại làm frame trước cho lần sau
        self.prev_gray = gray

        # Bước 4: Cập nhật trạng thái cử động
        now = time.time()

        if changed_ratio >= DIFF_AREA_RATIO:
            # Có thay đổi đáng kể → ghi nhận cử động
            self._last_motion_time = now
            self._motion_count += 1
        else:
            # Không có thay đổi → giảm dần motion_count
            self._motion_count = max(0, self._motion_count - 1)

        # Bước 5: Quyết định có vật hay không
        # Có vật nếu:
        #   (a) Có cử động trong MOTION_HOLD_SEC giây gần đây
        #   (b) HOẶC motion_count tích lũy ≥ DIFF_MIN_MOTION
        time_since_motion = now - self._last_motion_time
        has_recent_motion = time_since_motion < self.MOTION_HOLD_SEC
        has_accumulated = self._motion_count >= DIFF_MIN_MOTION

        return has_recent_motion or has_accumulated

    def reset(self):
        """Reset về trạng thái ban đầu."""
        self.prev_gray = None
        self._warmup_count = 0
        self._motion_count = 0
        self._last_motion_time = 0.0


# ============================================================
# TEST RIÊNG
# ============================================================
if __name__ == "__main__":
    import sys as _sys

    # Parse argument
    if len(_sys.argv) < 2:
        cam_source = "0"
        is_webcam = True
        print("[TEST] Webcam laptop (index 0)")
    elif _sys.argv[1].startswith("http"):
        cam_source = _sys.argv[1]
        is_webcam = False
        print(f"[TEST] IP camera: {cam_source}")
    else:
        cam_source = _sys.argv[1]
        is_webcam = True
        print(f"[TEST] Webcam (index {cam_source})")

    from core.camera import CameraStream

    cam = CameraStream(url=cam_source, name="test", is_webcam=is_webcam)
    differ = FrameDiffer()

    print("\n>>> Bat dau doc frame. Nhan 'q' de thoat.\n")
    print(f"    Warmup: {DIFF_WARMUP} frame dau")
    print(f"    Nguong: dien tich thay doi >= {DIFF_AREA_RATIO * 100:.1f}%")
    print(f"    Giu trang thai: {FrameDiffer.MOTION_HOLD_SEC}s sau cu dong cuoi\n")

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            has_obj = differ.has_object(frame)

            # Vẽ mask để hiển thị
            if differ.prev_gray is not None and differ._warmup_count >= DIFF_WARMUP:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                # Note: prev_gray đã được update trong has_object()
                # Cần trick: so sánh lại để hiển thị
                # Đơn giản: vẽ mask từ frame hiện tại vs chính nó
                mask_bgr = np.zeros_like(frame)
                cv2.putText(
                    mask_bgr,
                    f"Motion count: {differ._motion_count}",
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )
                # Hiển thị thời gian từ cử động cuối
                if differ._last_motion_time > 0:
                    elapsed = time.time() - differ._last_motion_time
                    cv2.putText(
                        mask_bgr,
                        f"Last motion: {elapsed:.1f}s ago",
                        (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2,
                    )
            else:
                mask_bgr = np.zeros_like(frame)

            # Status text
            if differ._warmup_count < DIFF_WARMUP:
                status = f"WARMUP {differ._warmup_count}/{DIFF_WARMUP}"
                status_color = (0, 200, 255)
            else:
                status = "CO VAT" if has_obj else "TRONG"
                status_color = (0, 255, 0) if has_obj else (150, 150, 150)

            cv2.putText(
                frame,
                f"Status: {status}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                status_color,
                3,
            )

            combined = np.hstack([frame, mask_bgr])
            cv2.imshow("FrameDiffer Motion - left: video, right: info", combined)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[!] Ctrl+C - thoat")
    finally:
        cam.release()
        cv2.destroyAllWindows()
        print("[OK] Da thoat sach")