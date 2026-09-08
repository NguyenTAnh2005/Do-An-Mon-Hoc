Đúng rồi, `cv2.VideoCapture` đọc frame theo vòng lặp — mỗi frame là 1 ảnh (numpy array/BGR), tốc độ đọc phụ thuộc camera (webcam thường ~30fps). Vấn đề là frame đó nằm trong RAM ở phía Python, còn frontend là trình duyệt — cần "đường ống" đẩy ảnh đó ra ngoài. Có 3 cách phổ biến, xếp theo độ đơn giản tăng dần độ phức tạp:

## Cách 1: MJPEG streaming (khuyên dùng cho đồ án này)

Đây là cách cổ điển nhưng cực kỳ đơn giản và ổn định cho demo LAN. Ý tưởng: FastAPI mở 1 endpoint trả về `multipart/x-mixed-replace` — về bản chất là "stream" liên tục ảnh JPEG nối đuôi nhau, trình duyệt tự động vẽ lại mỗi khi nhận ảnh mới. Frontend chỉ cần 1 thẻ `<img>` trỏ vào endpoint đó, **không cần thư viện gì thêm** — browser hỗ trợ native.

Backend (FastAPI):

```python
import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()
camera = cv2.VideoCapture(0)  # hoặc URL app IP camera điện thoại

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        # có thể vẽ bounding box + nhãn loài lên frame ở đây trước khi encode
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame")
```

Frontend (React) — chỉ vậy thôi:

```jsx
<img src="http://<IP-laptop>:8000/video_feed" alt="live camera" />
```

Ưu điểm: đơn giản, không cần WebSocket, không cần state quản lý, hợp với setup LAN offline-first của nhóm. Nhược điểm: khó đồng bộ chính xác giữa frame video và dữ liệu detection (JSON) nếu bạn muốn vẽ overlay động bằng React thay vì vẽ cứng lên ảnh ở backend.

## Cách 2: WebSocket (nếu cần tách riêng video và dữ liệu detection)

Nếu nhóm muốn: ảnh gốc hiển thị mượt + bounding box/nhãn vẽ động bằng `<canvas>` phía React (dễ style, dễ animate hơn vẽ cứng bằng cv2), thì tách 2 luồng:

- 1 WebSocket gửi frame (base64 JPEG) liên tục
- 1 WebSocket (hoặc cùng kênh) gửi kèm JSON `{loai, khoang_cach, muc_nguy_hiem, bbox: [x,y,w,h]}`

```python
@app.websocket("/ws/video")
async def video_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        success, frame = camera.read()
        _, buffer = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(buffer).decode('utf-8')
        await websocket.send_json({"frame": b64, "detections": [...]})
        await asyncio.sleep(0.03)  # ~30fps giả lập, throttle tránh nghẽn
```

Frontend dùng `useEffect` + `WebSocket` API, decode base64 vào `<img src={"data:image/jpeg;base64," + frame}>`, vẽ bbox bằng canvas overlay đè lên.

Ưu điểm: linh hoạt, tách rõ ràng ảnh vs metadata, dễ mở rộng (nhiều client cùng xem). Nhược điểm: base64 tốn băng thông hơn ~33% so với binary thô, code phức tạp hơn (phải tự quản reconnect, buffering).

## Cách 3: WebRTC — không khuyên cho đồ án này

Độ trễ thấp nhất, đúng chuẩn "video call", nhưng setup phức tạp (STUN/TURN server, signaling, peer connection) — quá tay cho scope 1 học kỳ và không cần thiết khi chỉ chạy LAN nội bộ.

## Khuyến nghị cụ thể cho nhóm bạn

Với bối cảnh đồ án (demo LAN, đã bỏ ý tưởng đa camera, ưu tiên đơn giản-ổn định hơn là mượt tuyệt đối), mình nghĩ **Cách 1 (MJPEG)** là hợp lý nhất để bắt đầu — vẽ luôn bounding box + nhãn + mức nguy hiểm lên frame bằng `cv2.putText`/`cv2.rectangle` trước khi encode, xong. Ít code, ít điểm lỗi, dễ demo.

Nếu sau này nhóm muốn giao diện đẹp hơn (animation cảnh báo, màu sắc theo mức nguy hiểm render bằng CSS thay vì cứng trong ảnh), lúc đó nâng cấp lên Cách 2 cũng không tốn nhiều công sửa vì backend logic detect/fuzzy giữ nguyên, chỉ đổi tầng truyền tải.

Một lưu ý kỹ thuật: dù chọn cách nào, **luồng đọc camera nên chạy trong 1 thread/task riêng**, không block event loop chính của FastAPI (đặc biệt nếu bạn dùng `async def` cho các route khác như API lấy lịch sử cảnh báo) — nếu không, việc `camera.read()` liên tục có thể làm nghẽn các request khác.
