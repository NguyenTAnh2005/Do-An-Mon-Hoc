Đây là câu hỏi kiến trúc quan trọng, đáng phân tích kỹ hơn thay vì chốt nhanh. Có 2 hướng, mỗi hướng có logic riêng.

## Hướng A: Chạy chung 1 process với backend (mình đã đề xuất ở trên)

Code AI (`ai/detector.py`, `ai/fuzzy.py`, `ai/camera_worker.py`) là module Python được `import` thẳng vào FastAPI app, cùng chạy trong 1 `uvicorn main:app`.

**Ưu điểm:**

- Đơn giản nhất để dựng — 1 lệnh chạy, 1 process, không cần lo giao tiếp giữa 2 hệ thống.
- Share thẳng cache RAM, DB session, không cần serialize dữ liệu qua network.
- Đúng tinh thần "offline-first LAN" của đồ án — càng ít thành phần di chuyển, càng ít điểm lỗi khi demo.
- Phù hợp quy mô: 3 người, 1 học kỳ, 1 thiết bị IoT, 1 camera.

**Nhược điểm:**

- Camera loop (`cv2.read()` chạy liên tục ở background) và các API request (VD web đang load lịch sử cảnh báo) **dùng chung tài nguyên** (CPU, event loop nếu không cẩn thận). Nếu AI xử lý nặng (YOLO inference mỗi frame), có thể làm chậm phản hồi của các route API khác — như mình có nhắc ở câu trả lời MJPEG: phải chạy camera loop trong thread/task riêng, không block event loop chính.
- Nếu code AI crash (VD lỗi model, lỗi OpenCV), có nguy cơ kéo sập luôn cả backend nếu không xử lý exception cẩn thận.

## Hướng B: Tách thành 2 process độc lập, giao tiếp qua API nội bộ

`ai_worker.py` chạy như 1 script/service riêng (VD `python ai_worker.py`), độc lập với `uvicorn main:app`. AI worker tự đọc camera, detect, tính fuzzy, rồi **gọi HTTP POST** vào backend (`POST /events`) để ghi log, hoặc publish MQTT để backend subscribe.

**Ưu điểm:**

- Cô lập lỗi: AI worker crash không kéo sập web backend, và ngược lại.
- Có thể restart riêng AI worker (VD đổi model `.pt` version mới) mà không cần restart cả web server — tiện khi debug/train lại.
- Về mặt tài nguyên, có thể chạy AI worker trên máy khác (VD máy có GPU) tách khỏi máy chạy web — dù với scope đồ án hiện tại chưa cần.

**Nhược điểm:**

- Phức tạp hơn hẳn: cần thêm tầng giao tiếp (HTTP nội bộ hoặc MQTT), phải tự lo retry nếu gọi API lỗi, phải chạy 2 lệnh riêng biệt (`uvicorn` + `python ai_worker.py`) — dễ quên chạy 1 trong 2 lúc demo.
- Cache RAM `species_cache` phải tồn tại **riêng ở cả 2 phía** hoặc AI worker phải tự gọi API để lấy danh mục loài — vòng vo hơn so với Hướng A.
- Với đúng 1 luồng camera + 1 thiết bị IoT, độ phức tạp thêm vào không tương xứng lợi ích thu được.

## Khuyến nghị

Với scope đồ án của nhóm (3 người, 1 học kỳ, 1 camera, đã chủ động bỏ ý tưởng đa camera vì tốn kinh phí), mình nghiêng về **Hướng A (chung process)**, chỉ cần đảm bảo 1 điều quan trọng: **camera loop phải chạy trong background thread riêng**, không đụng tới main event loop của FastAPI. Cách làm cụ thể:

```python
# ai/camera_worker.py
import threading

def camera_loop():
    while True:
        success, frame = camera.read()
        if not success:
            continue
        loai_id, khoang_cach = detect_and_measure(frame)
        muc_nguy_hiem = tinh_muc_nguy_hiem(loai_id, khoang_cach)
        # ghi vào DB, publish MQTT, v.v.

# main.py, trong lifespan startup
threading.Thread(target=camera_loop, daemon=True).start()
```

Nhờ chạy trong thread riêng (`daemon=True`), vòng lặp camera hoạt động song song với các API route khác mà không chặn chúng — bạn vừa xem live cam, vừa gọi API lấy lịch sử cảnh báo cùng lúc mà không bị đơ.

Nếu sau này nhóm thấy AI worker cần cô lập hơn (VD lúc demo hay bị crash kéo sập cả web), lúc đó tách sang Hướng B cũng không phải viết lại từ đầu — logic detect/fuzzy giữ nguyên, chỉ đổi cách "gọi ai đó ghi log" từ gọi hàm trực tiếp sang gọi HTTP. Có thể ghi ý này vào "Hướng phát triển" của báo cáo, giống cách nhóm cũ đã làm với vụ đa camera.
