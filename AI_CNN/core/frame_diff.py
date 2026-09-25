"""
frame_diff.py — Lớp lọc nhiễu chống nhận nhầm khay trống (PA3).

Nhiệm vụ:
    - So sánh frame hiện tại với background (khay trống) → quyết định
      có nên chạy YOLO hay không.
    - Update background bằng EMA để thích ứng khi ánh sáng thay đổi.

Input:  frame (numpy array)
Output: True  = có vật → cho YOLO chạy
        False = khay trống → bỏ qua, tiết kiệm CPU/GPU

Ai dùng:
    - worker.py gọi TRƯỚC khi đưa frame cho detector.

Tại sao cần:
    - Chống YOLO nhận nhầm khay trống thành rác (false positive).
    - Giảm ~90% tải CPU/GPU vì 90% thời gian khay trống.

Ngưỡng tune (trong config.py):
    - DIFF_THRESH, DIFF_AREA_RATIO, DIFF_EMA_ALPHA, DIFF_MIN_MOTION
"""