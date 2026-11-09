"""Offline camera UI walkthrough. Synthetic frames; no weights, camera, MQTT or HTTP."""
import argparse
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

for key, value in {"MQTT_HOST": "localhost", "MQTT_USER": "preview",
                   "MQTT_PASS": "preview", "BACKEND_URL": "http://localhost/unused"}.items():
    os.environ.setdefault(key, value)

import cv2
import numpy as np
from PIL import Image

from config import DIFF_WARMUP, MISS_MAX
from core.camera_ui import CameraUI
from core.detector import Detector
from core.frame_diff import FrameDiffer


def scenarios():
    ui = CameraUI(1)
    empty = np.full((480, 640, 3), 65, dtype=np.uint8)
    occupied = empty.copy()
    cv2.rectangle(occupied, (250, 160), (390, 340), (70, 160, 220), -1)
    detector = Detector(1, object(), MagicMock(), MagicMock())
    detector._run_yolo = lambda frame: [("organic", .92, None)]
    differ = FrameDiffer()

    def shot(name, now, has_object=False):
        frame = occupied if has_object else empty
        return name, ui.render(frame, detector.get_status(now), differ.get_status(), has_object)

    for _ in range(10):
        differ.has_object(empty)
    yield shot("01-warmup", 0)
    for _ in range(DIFF_WARMUP - 10):
        differ.has_object(empty)
    yield shot("02-ready", 0)
    with patch("core.detector.time.time") as clock:
        clock.return_value = 0
        detector.process(occupied, True)
        yield shot("03-detecting", .3, True)
        for index in range(MISS_MAX - 1):
            clock.return_value = .1 * (index + 1)
            detector.process(empty, False)
        yield shot("04-miss", .4)
        clock.return_value = .5
        detector.process(empty, False)
        yield shot("05-cancelled", .5)
        for moment in (1., 1.2, 1.4, 2.6):
            clock.return_value = moment
            detector.process(occupied, True)
        yield shot("06-cooldown", 4., True)
        clock.return_value = 12.
        detector.process(occupied, True)
        yield shot("07-remove-waste", 12., True)
        clock.return_value = 13.
        detector.process(empty, False)
        yield shot("08-ready-again", 13.)
        detector._votes.update({"organic": 4, "recyclable": 3})
        clock.return_value = 14.
        detector._finalize()
        yield shot("09-uncertain", 14., True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-only", action="store_true", help="Save previews without opening a window")
    args = parser.parse_args()
    folder = Path(__file__).parent / "previews"
    folder.mkdir(exist_ok=True)
    shots = list(scenarios())
    sheet = Image.new("RGB", (1260, 840), "#0b1220")
    try:
        for index, (name, frame) in enumerate(shots):
            cv2.imwrite(str(folder / f"{name}.png"), frame)
            thumbnail = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((420, 280))
            sheet.paste(thumbnail, ((index % 3)*420, (index // 3)*280))
        sheet.save(folder / "overview.jpg")
        print(f"Saved {len(shots)} scenarios to {folder}")
        if not args.save_only:
            print("PREVIEW ONLY. Space/Enter: next state. Q/Esc: quit.")
            for name, frame in shots:
                cv2.imshow("Smart Waste - OFFLINE PREVIEW", frame)
                while True:
                    key = cv2.waitKey(50) & 0xff
                    if key in (ord("q"), 27) or cv2.getWindowProperty("Smart Waste - OFFLINE PREVIEW", cv2.WND_PROP_VISIBLE) < 1:
                        return
                    if key in (32, 13):
                        break
    finally:
        if not args.save_only:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
