"""Detect waste on a tray by comparing frames with an empty-tray background."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np

from config import DIFF_AREA_RATIO, DIFF_EMA_ALPHA, DIFF_MIN_MOTION, DIFF_THRESH, DIFF_WARMUP, ROI_SIZE


class FrameDiffer:
    def __init__(self):
        self.background = None
        self._warmup_count = 0
        self._object_count = 0
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def has_object(self, frame) -> bool:
        h, w = frame.shape[:2]
        roi_w, roi_h = min(ROI_SIZE, w), min(ROI_SIZE, h)
        frame = frame[(h - roi_h) // 2:(h + roi_h) // 2, (w - roi_w) // 2:(w + roi_w) // 2]
        gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (5, 5), 0)

        # The tray must be empty while the first DIFF_WARMUP frames are captured.
        if self.background is None:
            self.background = gray.astype(np.float32)
        if self._warmup_count < DIFF_WARMUP:
            if self._warmup_count:
                cv2.accumulateWeighted(gray, self.background, DIFF_EMA_ALPHA)
            self._warmup_count += 1
            if self._warmup_count == DIFF_WARMUP:
                print(f"[FrameDiffer] Captured {DIFF_WARMUP} background frames; detection ready")
            return False

        diff = cv2.absdiff(gray, cv2.convertScaleAbs(self.background))
        _, mask = cv2.threshold(diff, DIFF_THRESH, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        changed_ratio = cv2.countNonZero(mask) / gray.size

        if changed_ratio >= DIFF_AREA_RATIO:
            self._object_count += 1
        else:
            self._object_count = 0
            cv2.accumulateWeighted(gray, self.background, DIFF_EMA_ALPHA)
        return self._object_count >= DIFF_MIN_MOTION

    def reset(self):
        self.background = None
        self._warmup_count = 0
        self._object_count = 0


if __name__ == "__main__":
    from core.camera import CameraStream

    source = sys.argv[1] if len(sys.argv) > 1 else "0"
    camera = CameraStream(source, name="test", is_webcam=not source.startswith("http"))
    differ = FrameDiffer()
    print(f"Keep the tray empty for the first {DIFF_WARMUP} frames. Press q to quit.")
    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue
            occupied = differ.has_object(frame)
            status = f"WARMUP {differ._warmup_count}/{DIFF_WARMUP}" if differ._warmup_count < DIFF_WARMUP else ("OBJECT" if occupied else "EMPTY")
            cv2.putText(frame, status, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Tray detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        cv2.destroyAllWindows()
