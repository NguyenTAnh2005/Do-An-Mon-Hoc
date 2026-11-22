from pathlib import Path

import torch
from ultralytics import YOLO

# Thư mục chứa file này = AI_CNN
BASE = Path(__file__).resolve().parent

WEIGHTS = BASE / "model" / "yolo_v8_training" / "weights" / "v1-best.pt"
DATA_YAML = BASE / "data" / "data.yaml"


def main():
    device = 0 if torch.cuda.is_available() else "cpu"

    model = YOLO(str(WEIGHTS))
    metrics = model.val(
        data=str(DATA_YAML),
        split="test",          # đánh giá trên tập test
        imgsz=640,
        batch=16,
        device=device,
        project=str(BASE / "model"),
        name="yolo_v8_test_eval",
        exist_ok=True,
        plots=True,            # lưu confusion matrix, đường cong PR/F1...
    )

    box = metrics.box
    print("\n===== KẾT QUẢ TRÊN TẬP TEST =====")
    print(f"Precision : {box.mp:.4f}")
    print(f"Recall    : {box.mr:.4f}")
    print(f"mAP50     : {box.map50:.4f}")
    print(f"mAP50-95  : {box.map:.4f}")

    print("\n----- Theo từng lớp -----")
    print(f"{'Lớp':<20}{'P':>8}{'R':>8}{'mAP50':>8}{'mAP50-95':>10}")
    for i, c in enumerate(box.ap_class_index):
        print(
            f"{metrics.names[c]:<20}"
            f"{box.p[i]:>8.3f}{box.r[i]:>8.3f}"
            f"{box.ap50[i]:>8.3f}{box.ap[i]:>10.3f}"
        )

    print("\nTốc độ (ms/ảnh):", metrics.speed)
    print("Kết quả và hình lưu tại:", metrics.save_dir)


if __name__ == "__main__":  # bắt buộc trên Windows
    main()