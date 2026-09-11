import time
import cv2
import torch
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel

# Fix lỗi PyTorch 2.6+
torch.serialization.add_safe_globals([DetectionModel])

# 1. Load mô hình
MODEL_PATH = r"D:\Do-An-Mon-Hoc\AI_CNN\best.pt"
model = YOLO(MODEL_PATH)

# 2. Mở Webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
  cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)


# --- HAM HO TRO UI/UX ---
def draw_corners(img, pt1, pt2, color, thickness=2, length=20):
  """Vẽ 4 góc định vị tối giản cho khung ngắm (Camera Corner Style)"""
  x1, y1 = pt1
  x2, y2 = pt2
  # Top-Left
  cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
  cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
  # Top-Right
  cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
  cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
  # Bottom-Left
  cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
  cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
  # Bottom-Right
  cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
  cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)


# Biến lịch sử
history = []
last_detected_time = 0
last_label = ""

while True:
  ret, frame = cap.read()
  if not ret or frame is None:
    break

  h, w, _ = frame.shape

  # 3. Kích thước và Tọa độ Khung ngắm trung tâm (ROI)
  roi_w, roi_h = 280, 280
  x1, y1 = (w - roi_w) // 2, (h - roi_h) // 2
  x2, y2 = x1 + roi_w, y1 + roi_h

  # Dự đoán trong vùng ROI
  roi_frame = frame[y1:y2, x1:x2]
  results = model.predict(source=roi_frame, conf=0.5, verbose=False)

  # Màu chủ đạo: Mặc định Xám/Trắng mờ (Status: Idle)
  theme_color = (220, 220, 220)
  detected = False
  current_label = ""
  current_conf = 0.0

  if len(results[0].boxes) > 0:
    detected = True
    theme_color = (0, 230, 118)  # Xanh Lá Neon khi nhận diện thành công

    box = results[0].boxes[0]
    cls_id = int(box.cls[0])
    current_conf = float(box.conf[0])
    current_label = model.names[cls_id].upper()

    # Thêm vào lịch sử (chống trùng trong 2.5s)
    curr_time = time.time()
    if (current_label != last_label) or (curr_time - last_detected_time > 2.5):
      timestamp = time.strftime("%H:%M:%S")
      history.insert(0, (timestamp, current_label, current_conf))
      if len(history) > 4:
        history.pop()
      last_label = current_label
      last_detected_time = curr_time

  # --- VẼ GIAO DIỆN UI/UX ---

  # A. Khung ngắm trung tâm dạng 4 góc (Clean Target)
  draw_corners(frame, (x1, y1), (x2, y2), theme_color, thickness=3, length=25)

  # B. Floating Card: Thẻ thông tin bên dưới khung ngắm (Chỉ hiển thị khi phát hiện rác)
  if detected:
    card_w, card_h = 240, 60
    card_x1, card_y1 = (w - card_w) // 2, y2 + 15
    card_x2, card_y2 = card_x1 + card_w, card_y1 + card_h

    # Nền mờ cho Thẻ thông tin
    overlay = frame.copy()
    cv2.rectangle(
        overlay, (card_x1, card_y1), (card_x2, card_y2), (20, 20, 20), -1
    )
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    cv2.rectangle(
        frame, (card_x1, card_y1), (card_x2, card_y2), theme_color, 1
    )

    # Tên nhãn rác
    cv2.putText(
        frame,
        current_label,
        (card_x1 + 15, card_y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    # Thanh % độ tin cậy (Confidence Bar)
    bar_x = card_x1 + 15
    bar_y = card_y1 + 38
    bar_max_w = 210
    bar_h = 6
    fill_w = int(bar_max_w * current_conf)

    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + bar_max_w, bar_y + bar_h),
        (60, 60, 60),
        -1,
    )
    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + fill_w, bar_y + bar_h),
        theme_color,
        -1,
    )

    # % Con số
    cv2.putText(
        frame,
        f"{int(current_conf * 100)}%",
        (card_x1 + 180, card_y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        theme_color,
        1,
    )

  # C. Side Panel: Bảng Lịch Sử bên phải màn hình (Minimalist Sidebar)
  panel_w = 220
  panel_x1 = w - panel_w - 15
  panel_y1 = 15

  if len(history) > 0:
    # Nền sidebar mờ
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (panel_x1, panel_y1),
        (w - 15, panel_y1 + 35 + len(history) * 30),
        (15, 15, 15),
        -1,
    )
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # Tiêu đề Panel
    cv2.putText(
        frame,
        "RECENT LOGS",
        (panel_x1 + 10, panel_y1 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (150, 150, 150),
        1,
    )

    # Danh sách Log gọn gàng
    for idx, (t, lbl, c) in enumerate(history):
      item_y = panel_y1 + 45 + idx * 28
      # Thời gian
      cv2.putText(
          frame,
          t,
          (panel_x1 + 10, item_y),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.38,
          (180, 180, 180),
          1,
      )
      # Nhãn
      cv2.putText(
          frame,
          lbl,
          (panel_x1 + 75, item_y),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.42,
          (255, 255, 255),
          1,
      )
      # %
      cv2.putText(
          frame,
          f"{int(c*100)}%",
          (w - 50, item_y),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.38,
          (0, 230, 118),
          1,
      )

  # Hiển thị
  cv2.imshow("YOLOv8 Waste Scanner - UI/UX Pro", frame)

  if cv2.waitKey(1) & 0xFF == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()