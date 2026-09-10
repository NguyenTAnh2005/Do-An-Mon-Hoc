import torch
from pathlib import Path
from ultralytics import YOLO

# Cấu hình đường dẫn tương đối từ vị trí đặt file train.py
ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "dataset" / "data.yaml"
PROJECT_PATH = ROOT_DIR / "model"

def main():
    print("🎬 Đang khởi tạo mô hình YOLOv8n...")
    model = YOLO("yolov8n.pt")

    # Kiểm tra thiết bị (ưu tiên GPU nếu có)
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"💻 Thiết bị sử dụng: {device}")

    print("🔥 Bắt đầu quá trình huấn luyện...")
    model.train(
        data=str(DATA_PATH),
        epochs=150,
        imgsz=640,         # Roboflow mặc định xuất ảnh 640. Nếu bạn muốn train nhẹ hơn, đổi về 224 như code cũ.
        batch=32,
        patience=30,       # Early stopping sau 30 epochs không cải thiện
        device=device,
        project=str(PROJECT_PATH), # Lưu kết quả vào folder AI_CNN/model
        name="yolo_v8_training",   # Tên thư mục con chứa trọng số
        save=True,
        plots=True
    )
    
    print(f"✅ DONE! Kết quả được lưu tại: {PROJECT_PATH}/yolo_v8_training")
    print(f"🚀 File 'best.pt' nằm trong: {PROJECT_PATH}/yolo_v8_training/weights/best.pt")

if __name__ == '__main__':
    main()