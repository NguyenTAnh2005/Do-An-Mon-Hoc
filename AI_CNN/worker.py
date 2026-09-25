"""
worker.py — Entry point chạy thật.

Cách chạy:
    python worker.py 1     # chạy khu A
    python worker.py 2     # chạy khu B
"""
import sys
from config import CAMERAS, MODEL_PATH, ...

def main(khu_vuc: int):
    if khu_vuc not in CAMERAS:
        print(f"❌ Khu vực {khu_vuc} không tồn tại. Chọn 1 hoặc 2.")
        sys.exit(1)

    print(f"🚀 Khởi động AI cho khu vực {khu_vuc}")
    # ... phần còn lại
    cam = CameraStream(CAMERAS[khu_vuc], name=f"khu{khu_vuc}")
    pub = MqttPublisher(khu_vuc=khu_vuc)
    # ...

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python worker.py <khu_vuc>")
        print("Ví dụ: python worker.py 1")
        sys.exit(1)
    
    khu_vuc = int(sys.argv[1])
    main(khu_vuc)