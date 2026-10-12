"""
detector.py — TRÁI TIM của AI service (file khó nhất).

Nhiệm vụ:
    - State machine 3 trạng thái: IDLE -> DETECTING -> COOLDOWN.
    - Vote theo TẦN SUẤT xuất hiện của class (KHÔNG phải conf cao nhất).
    - Chọn ảnh đẹp nhất trong nhóm class thắng.
    - Xử lý case "không tự tin" -> publish tín hiệu riêng.

Input:  frame (đã qua frame_diff)
Output: KHÔNG return — side effect:
        - Gọi publisher.publish_classification() khi chốt thành công.
        - Gọi publisher.publish_unsure() khi không đủ tự tin.
        - Gọi uploader.submit() để POST ảnh async.

Ai dùng:
    - worker.py gọi detector.process(frame) mỗi frame.

Luồng state:
    IDLE      --(thấy object >= CONF_MIN)--> DETECTING
    DETECTING --(hết cửa sổ WINDOW_SEC)--> chốt -> COOLDOWN
    DETECTING --(miss liên tục >= MISS_MAX)--> hủy phiên -> IDLE
    COOLDOWN  --(hết COOLDOWN_SEC)--> IDLE

Interface publisher (do mqtt_pub.py cung cấp):
    - publish_classification(log_id, loai_rac, confidence, timestamp)
    - publish_unsure()

Interface uploader (do uploader.py cung cấp):
    - submit(log_id, image_bytes)
"""
import sys
from pathlib import Path

# Thêm thư mục cha vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid
import time
from collections import Counter
from enum import Enum
from datetime import datetime, timezone

import cv2

from config import (
    CLASS_MAP,
    SYSTEM_CLASSES,
    CONF_MIN,
    WINDOW_SEC,
    MISS_MAX,
    COOLDOWN_SEC,
    MIN_VOTES,
    DOMINANCE_RATIO,
    ROI_SIZE,
)


class State(Enum):
    """3 trạng thái của state machine."""
    IDLE = "IDLE"
    DETECTING = "DETECTING"
    COOLDOWN = "COOLDOWN"


class Detector:
    """
    State machine xử lý nhận diện và chốt kết quả phân loại rác.

    Vòng đời:
        1. Nhận frame từ worker.py (đã qua frame_diff)
        2. Chạy state machine theo frame
        3. Khi chốt kết quả -> gọi publisher + uploader
    """

    def __init__(self, khu_vuc: int, model, publisher, uploader):
        """
        Khởi tạo Detector.

        Args:
            khu_vuc: Số khu vực (1 hoặc 2) — dùng cho log + MQTT topic
            model: YOLO model đã load (từ ultralytics)
            publisher: Object có method publish_classification() + publish_unsure()
            uploader: Object có method submit()
        """
        self.khu_vuc = khu_vuc
        self.model = model
        self.publisher = publisher
        self.uploader = uploader

        # === State machine ===
        self.state = State.IDLE

        # Thời điểm bắt đầu cửa sổ DETECTING
        self._window_start = 0.0

        # Thời điểm hết COOLDOWN
        self._cooldown_until = 0.0

        # === Vote & lưu frame ===
        # Counter đếm số lần mỗi class xuất hiện
        self._votes = Counter()

        # {class_name: (confidence, frame_copy)} — frame tốt nhất từng class
        self._best_frames = {}

        # === Miss counter ===
        # Số frame liên tiếp không thấy object trong DETECTING
        self._miss_count = 0

        # === Dedup (tránh publish trùng do bug) ===
        # Set các log_id đã publish trong X giây gần đây
        self._recent_log_ids = set()

    # ============================================================
    # HELPER — Crop ROI + chạy YOLO
    # ============================================================
    def _crop_roi(self, frame):
        """
        Crop vùng ROI vuông ở giữa khung.

        Args:
            frame: numpy array (BGR)

        Returns:
            frame_roi: numpy array (ROI vuông)
        """
        h, w = frame.shape[:2]

        # Tính tọa độ ROI vuông ở giữa
        roi_w = ROI_SIZE
        roi_h = ROI_SIZE

        # Nếu ROI lớn hơn frame -> giới hạn lại
        roi_w = min(roi_w, w)
        roi_h = min(roi_h, h)

        x1 = (w - roi_w) // 2
        y1 = (h - roi_h) // 2
        x2 = x1 + roi_w
        y2 = y1 + roi_h

        return frame[y1:y2, x1:x2]

    def _run_yolo(self, frame_roi):
        """
        Chạy YOLO trên ROI, trả về list các detection.

        Args:
            frame_roi: numpy array ROI

        Returns:
            list of (class_name, confidence, bbox) — đã filter conf >= CONF_MIN
        """
        results = self.model.predict(source=frame_roi, verbose=False, conf=CONF_MIN)

        detections = []
        if results and len(results) > 0:
            r = results[0]
            if r.boxes is not None:
                for box in r.boxes:
                    conf = float(box.conf[0])
                    if conf < CONF_MIN:
                        continue

                    # Lấy tên class gốc từ model
                    raw_name = self.model.names[int(box.cls[0])]

                    # Map sang enum hệ thống
                    system_name = CLASS_MAP.get(raw_name)
                    if system_name is None:
                        # Class lạ — bỏ qua
                        continue

                    # Validate system_name thuộc enum chuẩn
                    if system_name not in SYSTEM_CLASSES:
                        continue

                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    detections.append((system_name, conf, bbox))

        return detections

    # ============================================================
    # MAIN — Xử lý 1 frame
    # ============================================================
    def process(self, frame):
        """
        Xử lý 1 frame — gọi từ worker.py mỗi frame.

        Args:
            frame: numpy array (BGR) — frame gốc từ camera
        """
        now = time.time()

        # Crop ROI để chạy YOLO
        frame_roi = self._crop_roi(frame)

        # ============================================================
        # STATE: COOLDOWN — chỉ đếm thời gian, không chạy YOLO
        # ============================================================
        if self.state == State.COOLDOWN:
            if now >= self._cooldown_until:
                # Hết cooldown -> về IDLE
                self.state = State.IDLE
                self._reset_session()
            return

        # ============================================================
        # STATE: IDLE — chạy YOLO, chờ có object
        # ============================================================
        if self.state == State.IDLE:
            detections = self._run_yolo(frame_roi)

            if detections:
                # Có object -> chuyển sang DETECTING
                self._start_detecting(now)

                # Ghi nhận detection đầu tiên
                for cls_name, conf, bbox in detections:
                    self._accumulate(cls_name, conf, frame_roi)

            return

        # ============================================================
        # STATE: DETECTING — tích lũy vote trong cửa sổ thời gian
        # ============================================================
        if self.state == State.DETECTING:
            elapsed = now - self._window_start

            # Kiểm tra hết cửa sổ -> chốt kết quả
            if elapsed >= WINDOW_SEC:
                self._finalize()
                return

            # Còn trong cửa sổ -> chạy YOLO tiếp
            detections = self._run_yolo(frame_roi)

            if detections:
                # Có object -> reset miss_count
                self._miss_count = 0

                for cls_name, conf, bbox in detections:
                    self._accumulate(cls_name, conf, frame_roi)
            else:
                # Không có object -> tăng miss_count
                self._miss_count += 1

                if self._miss_count >= MISS_MAX:
                    # Mất object quá lâu -> huỷ phiên
                    print(f"[Detector-khu{self.khu_vuc}] Miss {MISS_MAX} lan -> huy phien")
                    self.state = State.IDLE
                    self._reset_session()

            return

    # ============================================================
    # STATE MACHINE — Các action
    # ============================================================
    def _start_detecting(self, now):
        """Bắt đầu phiên DETECTING."""
        self.state = State.DETECTING
        self._window_start = now
        self._votes.clear()
        self._best_frames.clear()
        self._miss_count = 0

    def _accumulate(self, cls_name, conf, frame_roi):
        """
        Tích lũy 1 detection vào phiên hiện tại.

        Args:
            cls_name: tên class hệ thống (tai_che/huu_co/vo_co)
            conf: confidence (0.0 - 1.0)
            frame_roi: frame ROI (sẽ copy nếu là best)
        """
        # Tăng vote cho class
        self._votes[cls_name] += 1

        # Lưu frame nếu conf cao hơn frame tốt nhất hiện tại của class này
        if cls_name not in self._best_frames or conf > self._best_frames[cls_name][0]:
            # QUAN TRỌNG: .copy() để tránh frame bị ghi đè ở vòng lặp sau
            self._best_frames[cls_name] = (conf, frame_roi.copy())

    def _finalize(self):
        """
        Chốt kết quả khi hết cửa sổ DETECTING.

        Logic:
            1. Nếu không có vote -> không publish, về COOLDOWN
            2. Xác định class thắng (most_common)
            3. Kiểm tra áp đảo (dominance) — nếu 2 class ngang nhau -> không tự tin
            4. Kiểm tra MIN_VOTES — nếu ít quá -> không tự tin
            5. Nếu OK -> publish_classification + uploader.submit
            6. Nếu không -> publish_unsure
            7. Về COOLDOWN
        """
        print(f"[Detector-khu{self.khu_vuc}] Cua so ket thuc — votes: {dict(self._votes)}")

        # === Trường hợp 1: Không có vote nào ===
        if not self._votes:
            print(f"[Detector-khu{self.khu_vuc}] Khong co vote -> bo qua")
            self._go_cooldown()
            return

        # === Xác định class thắng ===
        top2 = self._votes.most_common(2)
        winner = top2[0][0]
        winner_votes = top2[0][1]

        # === Kiểm tra áp đảo ===
        # Nếu có >= 2 class và class nhì chiếm > DOMINANCE_RATIO * top1
        # -> 2 class ngang nhau -> không tự tin
        if len(top2) >= 2:
            second_votes = top2[1][1]
            # Điều kiện "không tự tin": top2 > DOMINANCE_RATIO * top1
            # VD: DOMINANCE_RATIO = 0.5
            #     top1=10, top2=5  -> 5 > 5?  Không  -> OK
            #     top1=10, top2=8  -> 8 > 5?  Có     -> không tự tin
            if second_votes > DOMINANCE_RATIO * winner_votes:
                print(f"[Detector-khu{self.khu_vuc}] Khong ap dao "
                      f"({winner}={winner_votes}, {top2[1][0]}={second_votes}) -> KHONG TU TIN")
                self.publisher.publish_unsure()
                self._go_cooldown()
                return

        # === Kiểm tra số vote tối thiểu ===
        if winner_votes < MIN_VOTES:
            print(f"[Detector-khu{self.khu_vuc}] It vote qua "
                  f"({winner}={winner_votes} < {MIN_VOTES}) -> KHONG TU TIN")
            self.publisher.publish_unsure()
            self._go_cooldown()
            return

        # === THÀNH CÔNG — Chốt kết quả ===
        log_id = str(uuid.uuid4())
        conf, best_frame = self._best_frames[winner]
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        print(f"[Detector-khu{self.khu_vuc}] CHOT: {winner} "
              f"(conf={conf:.2f}, votes={winner_votes}, log_id={log_id[:8]}...)")

        # === Publish MQTT ===
        try:
            self.publisher.publish_classification(
                log_id=log_id,
                loai_rac=winner,
                confidence=conf,
                timestamp=timestamp,
            )
            # Ghi nhận log_id để dedup
            self._recent_log_ids.add(log_id)
        except Exception as e:
            print(f"[Detector-khu{self.khu_vuc}] Loi publish MQTT: {e}")

        # === Encode ảnh + submit uploader (async) ===
        try:
            # Encode JPEG để giảm dung lượng
            success, img_encoded = cv2.imencode(
                ".jpg", best_frame, [cv2.IMWRITE_JPEG_QUALITY, 85]
            )
            if success:
                img_bytes = img_encoded.tobytes()
                self.uploader.submit(log_id, img_bytes)
            else:
                print(f"[Detector-khu{self.khu_vuc}] Encode JPEG that bai")
        except Exception as e:
            print(f"[Detector-khu{self.khu_vuc}] Loi submit uploader: {e}")

        # === Về COOLDOWN ===
        self._go_cooldown()

    def _go_cooldown(self):
        """Chuyển sang COOLDOWN và reset phiên."""
        self.state = State.COOLDOWN
        self._cooldown_until = time.time() + COOLDOWN_SEC
        self._reset_session()

    def _reset_session(self):
        """Xóa vote + best_frames của phiên hiện tại."""
        self._votes.clear()
        self._best_frames.clear()
        self._miss_count = 0


# ============================================================
# TEST RIÊNG — dùng MockPublisher + MockUploader
# ============================================================
if __name__ == "__main__":
    """
    Script test Detector độc lập (không cần MQTT/backend thật).

    Cách chạy:
        cd AI_CNN
        python core/detector.py http://192.168.0.3:4747/video

    Kiểm tra:
        - State machine chuyển IDLE -> DETECTING -> COOLDOWN
        - Khi đưa vật vào + giữ yên ~1.5s -> publish kết quả
        - Xem console log
        - Nhấn 'q' để thoát
    """
    import sys as _sys
    from ultralytics import YOLO
    import torch
    from ultralytics.nn.tasks import DetectionModel

    # Fix lỗi PyTorch 2.6+
    torch.serialization.add_safe_globals([DetectionModel])

    # ===== Mock Publisher =====
    class MockPublisher:
        """Publisher giả — chỉ in ra console."""
        def __init__(self, khu_vuc):
            self.khu_vuc = khu_vuc

        def publish_classification(self, log_id, loai_rac, confidence, timestamp):
            print(f"\n{'='*60}")
            print(f"[MOCK PUBLISH] Topic: truong/khu{self.khu_vuc}/phanloai")
            print(f"  log_id:     {log_id}")
            print(f"  loai_rac:   {loai_rac}")
            print(f"  confidence: {confidence:.3f}")
            print(f"  timestamp:  {timestamp}")
            print(f"{'='*60}\n")

        def publish_unsure(self):
            print(f"\n[MOCK PUBLISH] Topic: truong/khu{self.khu_vuc}/khongchac")
            print(f"[MOCK PUBLISH] -> KHONG TU TIN\n")

    # ===== Mock Uploader =====
    class MockUploader:
        """Uploader giả — chỉ in ra console."""
        def submit(self, log_id, image_bytes):
            size_kb = len(image_bytes) / 1024
            print(f"[MOCK UPLOAD] log_id={log_id[:8]}... size={size_kb:.1f}KB\n")

    # ===== Parse argument =====
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

    # ===== Load model =====
    from config import MODEL_PATH
    print(f"[TEST] Loading model: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    print(f"[TEST] Model classes: {model.names}")

    # ===== Init components =====
    from core.camera import CameraStream
    from core.frame_diff import FrameDiffer

    cam = CameraStream(url=cam_source, name="test", is_webcam=is_webcam)
    differ = FrameDiffer()
    publisher = MockPublisher(khu_vuc=1)
    uploader = MockUploader()
    detector = Detector(khu_vuc=1, model=model, publisher=publisher, uploader=uploader)

    print("\n>>> Bat dau test. Nhan 'q' de thoat.\n")
    print("    - Dua vat vao khay -> giu yen ~1.5s -> xem console\n")

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            # Bước 1: Lọc nhiễu
            has_obj = differ.has_object(frame)

            # Bước 2: Nếu có cử động -> đưa vào detector
            if has_obj:
                detector.process(frame)

            # ===== Hiển thị =====
            # Vẽ trạng thái state lên frame
            state_color = {
                State.IDLE: (150, 150, 150),
                State.DETECTING: (0, 200, 255),
                State.COOLDOWN: (0, 100, 255),
            }[detector.state]

            cv2.putText(
                frame,
                f"State: {detector.state.value}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                state_color,
                3,
            )

            cv2.putText(
                frame,
                f"Votes: {dict(detector._votes)}",
                (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.imshow("Detector Test - Nhan 'q' de thoat", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[!] Ctrl+C - thoat")
    finally:
        cam.release()
        cv2.destroyAllWindows()
        print("[OK] Da thoat sach")