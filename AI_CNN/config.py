"""
config.py — Bảng điều khiển trung tâm của AI service.

Nhiệm vụ:
    - Chứa TẤT CẢ hằng số dùng chung (không có logic).
    - Đọc thông tin nhạy cảm (EMQX host/pass) từ file .env qua os.getenv().
    - Là NƠI DUY NHẤT để chỉnh ngưỡng — không hard-code ở file khác.

Ai import file này:
    - worker.py, core/camera.py, core/frame_diff.py,
      core/detector.py, core/mqtt_pub.py, core/uploader.py

Lưu ý:
    - Không commit file .env lên Git (chỉ commit .env.example).
    - CLASS_MAP phải khớp enum với IoT (Tường) và Web (Anh):
      tai_che / huu_co / vo_co — KHÔNG đổi tên khác.
    - Tên class bên TRÁI trong CLASS_MAP phải khớp CHÍNH XÁC model.names
      (in ra bằng: python check_classmap.py).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Nạp biến môi trường từ .env (cùng thư mục với file này)
load_dotenv()


# ============================================================
# 1. TỪ .env — config chung, giống nhau cho cả 2 khu
# ============================================================
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")
BACKEND_URL = os.getenv("BACKEND_URL")

# Validate: nếu thiếu config quan trọng → báo lỗi sớm
_required = ["MQTT_HOST", "MQTT_USER", "MQTT_PASS", "BACKEND_URL"]
_missing = [k for k in _required if not globals().get(k)]
if _missing:
    raise RuntimeError(
        f"❌ Thiếu biến môi trường: {_missing}. "
        f"Kiểm tra file .env (copy từ .env.example)."
    )


# ============================================================
# 2. PHẦN CỨNG — khác nhau giữa 2 khu
# ============================================================
CAMERAS = {
    1: "http://192.168.1.10:8080/video",   # Khu A — IP Webcam
    2: "http://192.168.1.11:8080/video",   # Khu B — IP Webcam
}


# ============================================================
# 3. MODEL & CLASS MAPPING
# ============================================================
# Đường dẫn tới file weights đã train xong
MODEL_PATH = Path(__file__).parent / "model" / "yolo_v8_training" / "weights" / "v1-best.pt"

# Map tên class gốc Roboflow → enum hệ thống
# ⚠️  Tên bên trái PHẢI khớp CHÍNH XÁC với model.names (in ra từ YOLO)
# ⚠️  Tên bên phải PHẢI khớp với IoT (Tường) + Web (Anh) — không đổi
CLASS_MAP = {
    "recyclable waste": "tai_che",     # ⚠️ DẤU CÁCH, không phải gạch ngang
    "organic-waste":    "huu_co",      # Hữu cơ
    "inorganic-waste":  "vo_co",       # Vô cơ
}

# Tập enum hợp lệ — dùng để validate trước khi publish
SYSTEM_CLASSES = {"tai_che", "huu_co", "vo_co"}


# ============================================================
# 4. NGƯỠNG DETECTOR (state machine)
# ============================================================
CONF_MIN = 0.6          # confidence tối thiểu để vào DETECTING
WINDOW_SEC = 1.5        # cửa sổ tích lũy (giây)
MISS_MAX = 5            # số frame miss liên tiếp → hủy phiên
COOLDOWN_SEC = 8        # nghỉ sau khi chốt (giây)
MIN_VOTES = 3           # số vote tối thiểu để 1 class thắng

# Ngưỡng áp đảo: class thắng phải ≥ DOMINANCE_RATIO × class nhì
# VD: 0.5 → class thắng phải gấp đôi class nhì (10 vs 5 OK, 10 vs 8 → không tự tin)
DOMINANCE_RATIO = 0.5


# ============================================================
# 5. FRAME DIFFERENCING (PA3)
# ============================================================
DIFF_THRESH = 25        # ngưỡng pixel diff
DIFF_AREA_RATIO = 0.02  # 2% diện tích thay đổi → coi là có vật
DIFF_EMA_ALPHA = 0.05   # tốc độ update background
DIFF_MIN_MOTION = 3     # cần N frame liên tiếp mới coi là "có vật"
DIFF_WARMUP = 30        # số frame đầu để build background


# ============================================================
# 6. ROI — vùng nhận diện ở giữa khung
# ============================================================
# Đọc từ .env để linh hoạt giữa máy test (yếu) và máy demo (GPU):
#   - Máy CPU (test logic): ROI_SIZE=280  → ~10 FPS
#   - Máy GPU (demo thật):  ROI_SIZE=640  → ~30-50 FPS
# Mặc định 640 nếu không có trong .env
ROI_SIZE = int(os.getenv("ROI_SIZE", "640"))


# ============================================================
# 7. THƯ MỤC LƯU ẢNH KHI LỖI MẠNG
# ============================================================
LOCAL_IMAGE_DIR = Path(__file__).parent / "local_images"
LOCAL_IMAGE_DIR.mkdir(exist_ok=True)


# ============================================================
# 8. MQTT TOPIC TEMPLATE
# ============================================================
def topic_phanloai(khu_vuc: int) -> str:
    """Topic publish kết quả phân loại thành công."""
    return f"truong/khu{khu_vuc}/phanloai"

def topic_khongchac(khu_vuc: int) -> str:
    """Topic publish tín hiệu 'không tự tin'."""
    return f"truong/khu{khu_vuc}/khongchac"

def topic_trangthai_ai(khu_vuc: int) -> str:
    """Topic LWT của AI script (online/offline)."""
    return f"truong/khu{khu_vuc}/trangthai/ai"

def topic_mucday(khu_vuc: int, loai_rac: str) -> str:
    """Topic publish mức đầy — ESP32 dùng topic này."""
    return f"truong/khu{khu_vuc}/mucday/{loai_rac}"