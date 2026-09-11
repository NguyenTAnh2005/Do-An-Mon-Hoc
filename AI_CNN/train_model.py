import torch
from pathlib import Path
from ultralytics import YOLO

# ==== ĐƯỜNG DẪN ====
ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "data" / "data.yaml"
PROJECT_PATH = ROOT_DIR / "model"
RUN_NAME = "yolo_v8_training"
LAST_WEIGHTS = PROJECT_PATH / RUN_NAME / "weights" / "last.pt"


def get_train_config(device) -> dict:
    """
    Tập trung toàn bộ tham số train ở đây để dễ chỉnh sau này,
    không cần mò trong hàm main().
    """
    return dict(
        data=str(DATA_PATH),
        epochs=150,
        imgsz=640,          # giữ nguyên theo ảnh Roboflow xuất ra, tránh resize lại tốn công
        batch=16,           # hạ từ 32 -> 16 để né OOM khi VRAM bị chiếm bởi tiến trình khác
        patience=30,        # early stopping sau 30 epoch không cải thiện
        device=device,
        project=str(PROJECT_PATH),
        name=RUN_NAME,
        save=True,
        save_period=10,     # lưu checkpoint phụ mỗi 10 epoch, phòng máy sập giữa chừng
        plots=True,
        cache="disk",        # để False nếu RAM laptop không dư nhiều; True (RAM) sẽ nhanh hơn nhưng tốn RAM
        workers=4,          # số luồng load ảnh, hạ nếu CPU yếu / máy nóng
        amp=True,           # mixed precision -> giảm VRAM, tăng tốc trên RTX 4050
        cos_lr=True,        # learning rate giảm dần theo cosine, ổn định hơn cho fine-tune
        exist_ok=True,      # QUAN TRỌNG: cho phép ghi tiếp vào đúng folder cũ, không tự tách "training2"
    )


def main():
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"💻 Thiết bị sử dụng: {device}")

    # Tự phát hiện: nếu đã có checkpoint dở dang -> resume, ngược lại train mới từ yolov8n.pt
    if LAST_WEIGHTS.exists():
        print(f"🔄 Phát hiện checkpoint dở dang tại: {LAST_WEIGHTS}")
        print("➡️  Resume training từ epoch đã dừng...")
        model = YOLO(str(LAST_WEIGHTS))
        model.train(resume=True)  # đọc lại toàn bộ config gốc từ args.yaml, không truyền tham số khác
    else:
        print("🎬 Không có checkpoint cũ, khởi tạo train mới từ yolov8n.pt...")
        model = YOLO("yolov8n.pt")
        config = get_train_config(device)
        model.train(**config)

    print(f"✅ DONE! Kết quả được lưu tại: {PROJECT_PATH}/{RUN_NAME}")
    print(f"🚀 File 'best.pt' nằm trong: {PROJECT_PATH}/{RUN_NAME}/weights/best.pt")


if __name__ == '__main__':
    main()