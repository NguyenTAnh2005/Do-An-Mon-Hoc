"""Chạy vòng lặp phân loại AI cho một khu thu gom rác"""

import argparse

from ultralytics import YOLO

from config import CAMERAS, CLASS_MAP, DIFF_WARMUP, MODEL_PATH
from core.camera import CameraStream
from core.detector import Detector
from core.frame_diff import FrameDiffer
from core.mqtt_pub import MqttPublisher
from core.uploader import Uploader


def main(khu_vuc: int):
    if khu_vuc not in CAMERAS:
        raise ValueError(f"Unknown area: {khu_vuc}")
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model weights missing: {MODEL_PATH}")

    model = YOLO(str(MODEL_PATH))
    missing = set(CLASS_MAP) - set(model.names.values())
    if missing:
        raise ValueError(f"Model class names do not match CLASS_MAP: {sorted(missing)}")

    camera = publisher = uploader = None
    try:
        camera = CameraStream(CAMERAS[khu_vuc], name=f"area{khu_vuc}")
        publisher = MqttPublisher(khu_vuc)
        uploader = Uploader()
        differ = FrameDiffer()
        detector = Detector(khu_vuc, model, publisher, uploader)
        print(f"[AI-area{khu_vuc}] Keep tray empty for the first {DIFF_WARMUP} frames")

        while True:
            frame = camera.read()
            if frame is None:
                continue
            detector.process(frame, differ.has_object(frame))
    except KeyboardInterrupt:
        print(f"[AI-area{khu_vuc}] Stopping")
    finally:
        if camera is not None:
            camera.release()
        if uploader is not None:
            uploader.close()
        if publisher is not None:
            try:
                publisher.publish_offline()
            finally:
                publisher.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI waste classification for one area")
    parser.add_argument("area", type=int, choices=CAMERAS)
    main(parser.parse_args().area)
