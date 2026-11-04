"""Chạy vòng lặp phân loại AI cho một khu thu gom rác"""

import argparse
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

from config import CAMERAS, CAMERA_TOP_CROP_RATIO, CLASS_MAP, DIFF_WARMUP, MODEL_PATH, ROI_SIZE
from core.camera import CameraStream
from core.detector import Detector
from core.frame_diff import FrameDiffer
from core.mqtt_pub import MqttPublisher
from core.uploader import Uploader


RESULT_LABELS = {
    "recyclable": "Rác tái chế",
    "organic": "Rác hữu cơ",
    "inorganic": "Rác vô cơ",
    "uncertain": "Chưa xác định",
}


@lru_cache(maxsize=8)
def _font(size: int, bold: bool = False):
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def show_preview(frame, differ, detector, khu_vuc: int) -> bool:
    h, w = frame.shape[:2]
    preview = Image.new("RGB", (w + 320, max(h + 125, 400)), (12, 19, 30))
    preview.paste(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), (20, 80))
    draw = ImageDraw.Draw(preview)
    panel_x = w + 40
    draw.rounded_rectangle((panel_x, 80, panel_x + 260, max(h + 80, 360)), radius=16, fill=(23, 33, 48))
    draw.text((20, 22), "PHÂN LOẠI RÁC", font=_font(27, True), fill=(245, 248, 252))
    draw.text((panel_x + 20, 30), f"KHU VỰC {khu_vuc}", font=_font(18), fill=(155, 174, 195))
    draw.text((20, h + 95), "Nhấn Q để thoát", font=_font(16), fill=(155, 174, 195))

    roi_size = min(ROI_SIZE, w, h)
    x1, y1 = (w - roi_size) // 2, (h - roi_size) // 2

    if differ._warmup_count < DIFF_WARMUP:
        status, detail = "Đang lấy nền", "Giữ khay trống"
        value = f"{differ._warmup_count}/{DIFF_WARMUP} khung hình"
        color = (245, 215, 110)
    elif detector.state.value == "DETECTING":
        status, detail = "Đang nhận diện", "Giữ vật trong khung"
        value = RESULT_LABELS.get(detector._votes.most_common(1)[0][0], "Đang quét") if detector._votes else "Đang quét"
        color = (110, 205, 245)
    elif detector.last_result:
        status, detail = "Đã phân loại", "Lấy vật ra để nhận lượt mới"
        value = RESULT_LABELS.get(detector.last_result, "Chưa xác định")
        color = (85, 215, 150) if detector.last_result != "uncertain" else (245, 215, 110)
    else:
        status, detail = "Sẵn sàng", "Đặt vật trong khung"
        value = "Chờ nhận diện"
        color = (85, 215, 150)

    draw.rectangle((20 + x1, 80 + y1, 20 + x1 + roi_size, 80 + y1 + roi_size), outline=color, width=3)
    draw.ellipse((panel_x + 20, 116, panel_x + 32, 128), fill=color)
    draw.text((panel_x + 44, 105), status, font=_font(21, True), fill=color)
    draw.text((panel_x + 20, 166), "KẾT QUẢ", font=_font(15, True), fill=(155, 174, 195))
    draw.text((panel_x + 20, 199), value, font=_font(25, True), fill=(245, 248, 252))
    draw.text((panel_x + 20, 253), detail, font=_font(17), fill=(184, 198, 213))
    if differ._warmup_count < DIFF_WARMUP:
        draw.rounded_rectangle((panel_x + 20, 302, panel_x + 220, 312), radius=5, fill=(54, 69, 87))
        draw.rounded_rectangle((panel_x + 20, 302, panel_x + 20 + 200 * differ._warmup_count // DIFF_WARMUP, 312), radius=5, fill=color)
    cv2.imshow(f"AI area {khu_vuc}", cv2.cvtColor(np.asarray(preview), cv2.COLOR_RGB2BGR))
    return cv2.waitKey(1) & 0xFF == ord("q")


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
        window_name = f"AI area {khu_vuc}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while True:
            frame = camera.read()
            if frame is None:
                continue
            # shortcut: DroidCam watermark is in the top quarter; adjust CAMERA_TOP_CROP_RATIO if the camera layout changes.
            frame = frame[int(frame.shape[0] * CAMERA_TOP_CROP_RATIO):]
            detector.process(frame, differ.has_object(frame))
            if show_preview(frame, differ, detector, khu_vuc):
                break
    except KeyboardInterrupt:
        print(f"[AI-area{khu_vuc}] Stopping")
    finally:
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()
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
