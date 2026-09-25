"""
camera.py — Quản lý kết nối camera (IP Webcam / DroidCam / webcam laptop).

Nhiệm vụ:
    - Bọc cv2.VideoCapture, tự động reconnect khi mất kết nối.
    - Set CAP_PROP_BUFFERSIZE=1 để giảm delay (IP camera rất quan trọng).

Input:  URL camera (từ config.CAMERAS)
Output: frame (numpy array) hoặc None nếu mất frame

Ai dùng:
    - worker.py gọi camera.read() mỗi vòng lặp.

Tại sao cần class riêng:
    - cv2.VideoCapture gốc KHÔNG tự reconnect khi mất WiFi → script chết.
    - IP camera buffer mặc định rất lớn → delay 1-2s nếu không set buffer=1.

Test riêng:
    - Rút WiFi 10s → cắm lại → script phải tự phục hồi, không crash.
"""