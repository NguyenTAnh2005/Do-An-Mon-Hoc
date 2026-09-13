# Danh sách phần cứng & phần mềm cần cho dự án

> **Mục đích file này:** liệt kê tất cả thiết bị phần cứng, framework/thư viện phần mềm, và công cụ hỗ trợ dùng trong dự án, kèm tác dụng của từng thứ. Dùng để tra cứu nhanh "cái này dùng để làm gì" hoặc lên danh sách mua sắm/cài đặt.

Xem thêm: [Vai trò của từng thành phần trong luồng hệ thống](./vai-tro-thanh-phan.md)

## A. Phần cứng

| Thiết bị                 | Số lượng                  | Tác dụng                                                                                 |
| ------------------------ | -------------------------- | ----------------------------------------------------------------------------------------- |
| ESP32                    | 2 (1/zone)                 | Điều khiển 3 thùng/zone: đọc cảm biến, điều khiển servo, điều khiển LED, publish/subscribe MQTT |
| Cảm biến siêu âm HC-SR04 | 6 (1/thùng)                | Đo khoảng cách `d` từ nắp đến mặt rác → gửi thô, Backend tính % đầy                       |
| Servo motor              | 6 (1/thùng)                | Mở/đóng nắp thùng — **tự động mở đúng ngăn** theo `loai_rac` nhận qua MQTT, không phụ thuộc LED |
| LED xanh                 | 2 (1/zone, **không phải 1/thùng**) | Chỉ báo hiệu "AI detect/phân loại thành công" — không gắn với thùng cụ thể nào            |
| LED đỏ                   | 2 (1/zone) — **độc lập với LED xanh, không dùng chung chân/module** | Chỉ báo hiệu "AI không đủ tự tin nhận diện" — báo người dùng tự phân loại thủ công, không gắn với thùng cụ thể nào |
| Smartphone (IP camera)   | 2 (1/zone)                 | Chạy app IP Webcam/DroidCam, cấp luồng video cho AI xử lý qua giao thức IP                |

> Lưu ý: cả 2 LED chỉ là tín hiệu "detect được hay không" cấp zone, không phải tín hiệu theo từng thùng — việc mở đúng ngăn thùng nào hoàn toàn do servo tự xử lý dựa vào `loai_rac`.

**Tổng mỗi ESP32 quản lý:** 3 HC-SR04 + 3 servo + 1 LED xanh + 1 LED đỏ = 8 chân I/O liên quan (cần lưu ý khi đi dây/chọn ESP32 đủ chân).

## B. Phần mềm / Framework / Thư viện

| Thành phần                   | Vai trò             | Tác dụng                                                                 |
| ----------------------------- | -------------------- | -------------------------------------------------------------------------- |
| YOLOv8n (fine-tuned)          | Model AI             | Nhận diện loại rác từ khung hình camera                                  |
| Roboflow Universe             | Nguồn dataset         | Cung cấp dữ liệu huấn luyện/fine-tune model                              |
| OpenCV (cv2)                  | Thư viện xử lý ảnh    | Đọc luồng camera, xử lý frame trước khi đưa vào model                    |
| Mosquitto (MQTT broker)       | Middleware            | Tầng trung gian giao tiếp giữa AI, IoT, Backend — decoupling             |
| FastAPI                       | Backend framework     | Xử lý API, subscriber MQTT, WebSocket server                             |
| PostgreSQL + ORM (Alembic)    | Database              | Lưu trữ dữ liệu khu vực, thùng rác, lịch sử phân loại; quản lý migration |
| React JS                      | Frontend framework    | Xây dựng giao diện quản lý (dashboard, lịch sử, thống kê)                |
| Cloudinary                    | Dịch vụ lưu trữ ảnh   | Lưu ảnh phân loại rác, trả về URL để Backend cập nhật DB                 |
| JWT (access + refresh token)  | Cơ chế xác thực       | Bảo mật đăng nhập, phân quyền truy cập hệ thống                          |

## C. Công cụ hỗ trợ phát triển

| Công cụ            | Tác dụng                                   |
| -------------------- | --------------------------------------------- |
| Git + GitHub        | Quản lý mã nguồn, làm việc nhóm qua branch    |
| MQTTX               | Debug MQTT thủ công — xem [chi tiết](../06-mqtt/debug-voi-mqttx.md) |
| Claude, Gemini Pro  | Hỗ trợ lập trình, tư duy kiến trúc            |
