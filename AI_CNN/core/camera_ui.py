"""Vietnamese camera HUD. Render on a copy, after detection and image capture."""
from pathlib import Path
import textwrap

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import ROI_SIZE

LABELS = {"organic": "Hữu cơ", "inorganic": "Vô cơ", "recyclable": "Tái chế"}
COLORS = {"WARMUP": "#60a5fa", "READY": "#34d399", "WAITING": "#fbbf24",
          "DETECTING": "#fbbf24", "COOLDOWN": "#a78bfa", "REMOVE_WASTE": "#fb7185"}


def build_view(status, background, occupied):
    """Turn actual pipeline state into instructions; never advance a timer/state here."""
    if not background["ready"]:
        count, total = background["warmup_count"], background["warmup_total"]
        return dict(phase="WARMUP", title="ĐANG LẤY NỀN", message="Giữ khay trống, không đặt rác vào.",
                    detail=f"Đã lấy {count}/{total} frame", progress=count / total)
    if status["state"] == "COOLDOWN":
        remaining = status["cooldown_remaining"]
        if remaining <= 0 and not status["tray_cleared"]:
            return dict(phase="REMOVE_WASTE", title="CHỜ LẤY RÁC RA", message=f'Đã hết {status["cooldown_total"]:g} giây nghỉ. Hãy lấy rác khỏi khay.',
                        detail="Chưa thấy khay trống — chưa nhận lượt mới", progress=1.)
        return dict(phase="COOLDOWN", title="ĐANG NGHỈ", message=f"Còn {remaining:.1f} giây trước lượt tiếp theo.",
                    detail=("Đã thấy khay trống — chờ hết giờ" if status["tray_cleared"]
                            else "Hãy lấy rác ra để mở khóa lượt tiếp theo"),
                    progress=1 - remaining / status["cooldown_total"])
    if status["state"] == "DETECTING":
        return dict(phase="DETECTING", title="ĐANG NHẬN DIỆN", message="Giữ rác trong khung nhận diện.",
                    detail=f'Còn {status["window_remaining"]:.1f}s | Miss {status["miss_count"]}/{status["miss_max"]} frame',
                    progress=1 - status["window_remaining"] / status["window_total"])
    if occupied:
        return dict(phase="WAITING", title="CHỜ NHẬN DIỆN RÕ", message="Có vật trên khay, YOLO chưa chốt detection.",
                    detail="Điều chỉnh vị trí rác, giữ trong khung", progress=0.)
    return dict(phase="READY", title="SẴN SÀNG NHẬN RÁC", message="Đặt một món rác vào khung nhận diện.",
                detail="Đã lấy nền xong — đang chờ vật", progress=1.)


class CameraUI:
    def __init__(self, area):
        self.area = area
        self.window = f"Smart Waste - Area {area}"
        self._fonts = {}

    def _font(self, size):
        if size not in self._fonts:
            candidates = ("C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
            path = next((p for p in candidates if Path(p).is_file()), None)
            self._fonts[size] = ImageFont.truetype(path, size) if path else ImageFont.load_default(size=size)
        return self._fonts[size]

    def render(self, frame, status, background, occupied, upload_events=()):
        view = build_view(status, background, occupied)
        color = COLORS[view["phase"]]
        # Annotation is isolated from the frame used by YOLO and the uploader.
        camera = frame.copy()
        h, w = camera.shape[:2]
        rw, rh = min(ROI_SIZE, w), min(ROI_SIZE, h)
        cv2.rectangle(camera, ((w-rw)//2, (h-rh)//2), ((w+rw)//2, (h+rh)//2), (80, 210, 140), 2)
        scale = min(800 / w, 600 / h)
        camera = cv2.resize(camera, (int(w * scale), int(h * scale)))
        cw = camera.shape[1]
        canvas = Image.new("RGB", (cw + 460, 840), "#0b1220")
        canvas.paste(Image.fromarray(cv2.cvtColor(camera, cv2.COLOR_BGR2RGB)), (0, 65))
        draw = ImageDraw.Draw(canvas)

        def line(x, y, text, fill="#dbeafe", size=17):
            draw.text((x, y), text, font=self._font(size), fill=fill)

        line(22, 20, f"SMART WASTE  /  KHU VỰC {self.area}", size=22)
        line(22, 690, "Đặt rác trong khung xanh • Q / Esc để thoát", size=18)
        line(22, 725, "Camera vẫn so nền trong lúc nghỉ; YOLO tạm dừng.", size=16)
        line(22, 755, "Miss = không có detection hợp lệ, khác với mất kết nối camera.", size=15)
        x = cw + 20
        line(x, 22, "TRẠNG THÁI HIỆN TẠI", "#94a3b8", 14)
        line(x, 55, view["title"], color, 24)
        y = 100
        for row in textwrap.wrap(view["message"], 43):
            line(x, y, row)
            y += 25
        draw.rounded_rectangle((x, 165, x+418, 177), radius=6, fill="#253047")
        progress = min(1., max(0., view["progress"]))
        if progress:
            draw.rounded_rectangle((x, 165, x+max(12, int(418*progress)), 177), radius=6, fill=color)
        for i, row in enumerate(textwrap.wrap(view["detail"], 46)):
            line(x, 192 + i*23, row, color, 16)
        votes = status["votes"]
        line(x, 250, "PHIẾU PHIÊN HIỆN TẠI", "#94a3b8", 14)
        for i, (key, label) in enumerate(LABELS.items()):
            line(x, 280+i*27, f"{label}: {votes.get(key, 0)}", size=18)
        result = status["last_result"]
        line(x, 378, "KẾT QUẢ GẦN NHẤT", "#94a3b8", 14)
        if result and result["outcome"] == "classified":
            line(x, 407, f'{LABELS[result["waste_type"]]} • {result["confidence"]:.0%}', "#34d399", 21)
            line(x, 439, f'ID: {result["log_id"][:18]}…', size=14)
            mqtt = "LỖI GỬI" if result["mqtt"] == "error" else "Đã giao client (chưa xác nhận servo)"
            line(x, 463, f"MQTT: {mqtt}", size=14)
        elif result:
            for i, row in enumerate(textwrap.wrap(result.get("reason", "Đã bỏ qua"), 45)):
                line(x, 407+i*24, row, "#fbbf24", 16)
        else:
            line(x, 407, "Chưa có kết quả", "#94a3b8")
        line(x, 510, "NHẬT KÝ GẦN NHẤT", "#94a3b8", 14)
        y = 540
        # Keep cancellation/errors readable after counters have reset.
        for event in reversed(status["events"][-4:]):
            tint = "#fb7185" if event["kind"] in ("cancelled", "error", "uncertain") else "#cbd5e1"
            rows = textwrap.wrap(f'{event["time"]}  {event["message"]}', 52)
            for row in rows[:2]:
                line(x, y, row, tint, 14)
                y += 20
            y += 9
        if upload_events:
            event = upload_events[-1]
            for i, row in enumerate(textwrap.wrap(event["message"], 75)[:2]):
                line(22, 790+i*20, row, "#fbbf24", 14)
        return cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

    def show(self, frame, status, background, occupied, upload_events=()):
        cv2.imshow(self.window, self.render(frame, status, background, occupied, upload_events))
        key = cv2.waitKey(1) & 0xff
        return key not in (ord("q"), 27) and cv2.getWindowProperty(self.window, cv2.WND_PROP_VISIBLE) >= 1

    def close(self):
        cv2.destroyAllWindows()
