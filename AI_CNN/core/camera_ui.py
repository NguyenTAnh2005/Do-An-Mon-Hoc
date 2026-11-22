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

# UI palette
BG          = "#0a1020"
HEADER_BG   = "#0d1626"
CARD_BG     = "#131c2e"
CARD_BORDER = "#22304d"
CARD_INNER  = "#1b2540"
TEXT        = "#e5e9f0"
MUTED       = "#8892a6"
SUBTLE      = "#475569"
FOOT_BG     = "#0d1524"


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

    def _card(self, draw, x, y, w, h):
        draw.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=CARD_BG, outline=CARD_BORDER, width=1)

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
        cw, ch = camera.shape[1], camera.shape[0]

        # Layout metrics
        HEADER_H = 64
        PANEL_W  = 460
        CANVAS_W = cw + PANEL_W
        CANVAS_H = max(840, HEADER_H + ch + 100)
        FOOTER_H = CANVAS_H - HEADER_H - ch

        canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
        draw = ImageDraw.Draw(canvas)

        def text(x, y, s, fill=TEXT, size=17, anchor=None):
            draw.text((x, y), s, font=self._font(size), fill=fill, anchor=anchor)

        # === Header ===
        draw.rectangle((0, 0, CANVAS_W, HEADER_H), fill=HEADER_BG)
        draw.rectangle((0, HEADER_H - 2, CANVAS_W, HEADER_H), fill=color)
        draw.ellipse((22, 27, 34, 39), fill=color)
        text(48, 18, "SMART WASTE", "#f8fafc", 20)
        text(48, 42, f"KHU VỰC {self.area}", MUTED, 13)

        # Status pill (right-aligned)
        f13 = self._font(13)
        pill_text = view["phase"]
        tw = int(draw.textlength(pill_text, font=f13))
        pill_x = CANVAS_W - tw - 50
        draw.rounded_rectangle((pill_x, 19, CANVAS_W - 22, 45), radius=13, fill="#1e293b", outline=color, width=1)
        text(pill_x + 14, 25, pill_text, color, 13)

        # === Camera feed ===
        canvas.paste(Image.fromarray(cv2.cvtColor(camera, cv2.COLOR_BGR2RGB)), (0, HEADER_H))

        # === Footer strip below camera ===
        if FOOTER_H > 0:
            draw.rectangle((0, HEADER_H + ch, CANVAS_W, CANVAS_H), fill=FOOT_BG)
            hints = [
                "Đặt rác trong khung xanh • Q / Esc để thoát",
                "Camera vẫn so nền trong lúc nghỉ; YOLO tạm dừng.",
                "Miss = không có detection hợp lệ, khác với mất kết nối camera.",
            ]
            fy = HEADER_H + ch + 18
            for i, hint in enumerate(hints):
                draw.ellipse((22, fy + 7, 28, fy + 13), fill=color if i == 0 else SUBTLE)
                text(36, fy, hint, TEXT if i == 0 else MUTED, 14)
                fy += 24
            if upload_events:
                event = upload_events[-1]
                fy = CANVAS_H - 40
                for row in textwrap.wrap(event["message"], 78)[:2]:
                    text(22, fy, row, "#fbbf24", 13)
                    fy += 18

        # === Right panel ===
        px = cw + 20
        pw = PANEL_W - 40
        py = HEADER_H + 16

        # Card 1: current status
        c1h = 250
        self._card(draw, px, py, pw, c1h)
        text(px + 18, py + 16, "TRẠNG THÁI HIỆN TẠI", MUTED, 12)
        text(px + 18, py + 40, view["title"], color, 24)
        yy = py + 78
        for row in textwrap.wrap(view["message"], 44):
            text(px + 18, yy, row, TEXT, 15)
            yy += 22
        bar_y = py + 155
        draw.rounded_rectangle((px + 18, bar_y, px + pw - 18, bar_y + 10), radius=5, fill=CARD_INNER)
        progress = min(1., max(0., view["progress"]))
        if progress > 0:
            bw = max(10, int((pw - 36) * progress))
            draw.rounded_rectangle((px + 18, bar_y, px + 18 + bw, bar_y + 10), radius=5, fill=color)
        yy = bar_y + 24
        for row in textwrap.wrap(view["detail"], 50):
            text(px + 18, yy, row, color, 13)
            yy += 19

        # Card 2: vote breakdown
        py += c1h + 14
        c2h = 185
        self._card(draw, px, py, pw, c2h)
        text(px + 18, py + 16, "PHIẾU PHIÊN HIỆN TẠI", MUTED, 12)
        votes = status["votes"]
        total_votes = max(1, sum(votes.get(k, 0) for k in LABELS))
        for i, (key, label) in enumerate(LABELS.items()):
            vy = py + 42 + i * 42
            v = votes.get(key, 0)
            text(px + 18, vy, label, TEXT, 15)
            text(px + pw - 18, vy, str(v), color if v else MUTED, 15, anchor="ra")
            vy2 = vy + 22
            draw.rounded_rectangle((px + 18, vy2, px + pw - 18, vy2 + 8), radius=4, fill=CARD_INNER)
            if v > 0:
                bw = max(8, int((pw - 36) * (v / total_votes)))
                draw.rounded_rectangle((px + 18, vy2, px + 18 + bw, vy2 + 8), radius=4, fill=color)

        # Card 3: last result (no MQTT text)
        py += c2h + 14
        c3h = CANVAS_H - py - 20
        self._card(draw, px, py, pw, max(120, c3h))
        text(px + 18, py + 16, "KẾT QUẢ GẦN NHẤT", MUTED, 12)
        result = status["last_result"]
        if result and result["outcome"] == "classified":
            text(px + 18, py + 44, LABELS[result["waste_type"]], "#34d399", 24)
            text(px + 18, py + 80, f'{result["confidence"]:.0%}', "#a7f3d0", 18)
            text(px + 18, py + 108, f'ID: {result["log_id"][:20]}…', MUTED, 12)
        elif result:
            yy = py + 44
            for row in textwrap.wrap(result.get("reason", "Đã bỏ qua"), 46):
                text(px + 18, yy, row, "#fbbf24", 15)
                yy += 22
        else:
            text(px + 18, py + 44, "Chưa có kết quả", MUTED, 15)

        return cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

    def show(self, frame, status, background, occupied, upload_events=()):
        cv2.imshow(self.window, self.render(frame, status, background, occupied, upload_events))
        key = cv2.waitKey(1) & 0xff
        return key not in (ord("q"), 27) and cv2.getWindowProperty(self.window, cv2.WND_PROP_VISIBLE) >= 1

    def close(self):
        cv2.destroyAllWindows()