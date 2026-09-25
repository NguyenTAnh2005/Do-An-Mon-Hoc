"""
detector.py — TRÁI TIM của AI service (file khó nhất).

Nhiệm vụ:
    - State machine 3 trạng thái: IDLE → DETECTING → COOLDOWN.
    - Vote theo TẦN SUẤT xuất hiện của class (KHÔNG phải conf cao nhất).
    - Chọn ảnh đẹp nhất trong nhóm class thắng.
    - Xử lý case "không tự tin" → publish tín hiệu riêng.

Input:  frame (đã qua frame_diff)
Output: KHÔNG return — side effect:
        - Gọi mqtt_pub.publish_classification() khi chốt thành công.
        - Gọi mqtt_pub.publish_unsure() khi không đủ tự tin.
        - Gọi uploader.submit() để POST ảnh async.

Ai dùng:
    - worker.py gọi detector.process(frame) mỗi frame.

Luồng state:
    IDLE ──(thấy object ≥ CONF_MIN)──► DETECTING
    DETECTING ──(hết cửa sổ WINDOW_SEC)──► chốt kết quả → COOLDOWN
    DETECTING ──(miss liên tục ≥ MISS_MAX)──► huỷ phiên → IDLE
    COOLDOWN ──(hết COOLDOWN_SEC)──► IDLE

⚠️  LƯU Ý QUAN TRỌNG:
    - KHÔNG dùng boxes[0] — phải vote theo tần suất (Counter).
    - loai_rac BẮT BUỘC map qua CLASS_MAP → tai_che/huu_co/vo_co.
    - log_id do AI tự sinh (uuid4) — KHÔNG xin backend cấp.
    - Nếu 2 class vote ngang nhau → coi là "không tự tin".

Ngưỡng tune (trong config.py):
    - CONF_MIN, WINDOW_SEC, MISS_MAX, COOLDOWN_SEC, MIN_VOTES
"""