# Ghi chú đồ án môn học — Hệ thống cảnh báo động vật nguy hiểm (Nông thôn/Trang trại VN)

## 1. Thông tin nhóm

- 3 thành viên:
- Các môn học nền tảng đã học kèm dự án liên quan:
  - **Lập trình web** (FE + BE)
  - **Nhập môn KHDL**: thu thập dataset Kaggle, làm sạch, giảm chiều, phân cụm K-means, huấn luyện AI dự đoán (kết quả không ổn vì dataset hạn chế)
  - **Hệ thống thông minh**: CNN nhận diện (qua camera điện thoại) + logic mờ xử lý + truyền tín hiệu MQTT tới sensor/cảnh báo (nhận diện động vật + cảm biến khoảng cách → mờ → mức nguy hiểm → cảnh báo). Dữ liệu ảnh lấy từ RoboFlow.

## 2. Đề tài cũ làm nền tảng (đọc từ báo cáo môn Hệ thống thông minh)

- **Tên đề tài cũ**: Hệ thống nhận diện mức độ nguy hiểm của động vật
- **CNN**: YOLOv8n, 8 loài, ~8064 ảnh (Roboflow), input 224×224, augmentation, split 87/9/4 (do augmentation chỉ áp lên tập train)
  - Kết quả: Precision 85.8%, Recall 73.3%, mAP50 0.81, mAP50-95 0.57 (chênh lệch lớn — nghi ngờ do resize 224×224 quá nhỏ)
- **Fuzzy Logic**: Mamdani MISO, 2 input (khoảng cách 0-40, độ hung dữ 1-10) → 1 output (báo động 0-100%), 9 luật, 4 mức output (An toàn/Vàng/Đỏ/Tử thần)
- **IoT**: ESP32-CAM + HC-SR04 (đo khoảng cách) + đèn/còi, giao tiếp qua MQTT broker công cộng `broker.emqx.io`
- **Quản lý dữ liệu**: DVC + Dagshub — bị lỗi, dvc pull không hoạt động (Dagshub chỉ dùng lưu ảnh đã bounding box từ YOLO, không phải nơi lưu dữ liệu vận hành)
- **3 hạn chế nhóm cũ tự nhận**:
  1. Chưa có nền tảng quản lý (chỉ chạy local, không lưu lịch sử)
  2. Đo khoảng cách phụ thuộc 1 cảm biến siêu âm, giới hạn <4m, phải quy đổi tỷ lệ giả (1:10)
  3. Chỉ 8 loài, dataset nhỏ, khoảng cách an toàn chưa phân biệt theo loài

## 3. Quyết định phạm vi đề tài mới

**Hướng đã chọn**: Mở rộng đồ án IoT+CNN+Fuzzy cũ thành sản phẩm hoàn chỉnh có nền tảng web quản lý, khoanh bối cảnh **Nông thôn/Trang trại VN**.

**Tên đề tài đề xuất**:

> "Xây dựng hệ thống IoT cảnh báo động vật nguy hiểm khu vực nông thôn ứng dụng CNN và logic mờ thích nghi theo loài, tích hợp nền tảng web giám sát thời gian thực"

**Phạm vi loài (7 loài)** — có cả loài nguy hiểm và loài an toàn để fuzzy logic có đối chiếu rõ (tham khảo):

| Loài     | Vai trò                   | Khoảng cách an toàn (m) | Độ hung dữ (1-10) |
| -------- | ------------------------- | ----------------------- | ----------------- |
| Rắn độc  | Nguy hiểm cao             | 2                       | 8                 |
| Lợn rừng | Nguy hiểm cao             | 8                       | 8                 |
| Trâu/Bò  | Nguy hiểm trung bình-cao  | 5                       | 7                 |
| Chó      | Nguy hiểm trung bình      | 3                       | 6                 |
| Khỉ      | Nguy hiểm thấp-trung bình | 3                       | 5                 |
| Mèo      | An toàn (baseline)        | 1                       | 2                 |
| Gà/Vịt   | An toàn (baseline)        | 0.5                     | 1                 |

**Dataset**: fork Roboflow Universe có sẵn dataset.

## 4. Các cải tiến kỹ thuật đã thống nhất

### 4.1 CNN

- Thử nghiệm train lại ở input **640×640** (mặc định YOLOv8) thay vì 224×224 — so sánh hiệu năng, đặc biệt kỳ vọng cải thiện mAP50-95 đang thấp.
- Khi tải ảnh về nên dùng script đổi tên theo index cho gọn hơn.
- Khi thêm loài mới:
  - Sử dụng roboflow bình thường, nếu khác dự án thì khê 1 chút, còn giống thì bước dưới sẽ không bị đụng
  - Vì khác folder dự án nên khi tải về các thông số bị lệch. Cần tổng hợp lại một thư mục data, ảnh bỏ chung, tuy nhiên file lablel thường sẽ chứa số class của vật theo số thứ tự nên cần viết 1 script chạy duyệt từng file và sửa trước khi gộp. VD: có 7 loài rồi, h thêm loài mới, khi tải về cần duyệt yaml chỉ số class loài đó từ 0 -> 7. Bản cũ 7 loài thì dùng từ 0->6 hết rồi nên bản mới muốn gộp vào thì cần chỉnh này trước. Sau đó gộp ảnh, label_file, chỉnh cái yaml mới cho khớp, có thể bỏ phần đoạn roboflow vì khi train chả đụng vào đó.
  - Khi train model mới, thay vì sử dụng model yolov8n.pt - mặc định thì dùng chính model v1 cũ, giúp tiết kiệm tg khi train cho những cái đã học qua rồi. Chỉ mất nhiều TG ở loài mới.

### 4.2 Fuzzy Logic

- Giữ nguyên kiến trúc 2-input hiện tại
- Cải tiến: **chuẩn hóa input "khoảng cách" theo tỷ lệ so với khoảng cách an toàn của từng loài** (khoảng cách đo được / khoảng cách an toàn loài đó) thay vì dùng số tuyệt đối chung cho mọi loài — giải quyết vấn đề "100m với báo/sư tử khác hoàn toàn 100m với mèo/bò"
- Bảng khoảng cách an toàn + độ hung dữ theo loài lưu trong DB (không phải hard-code), heuristic/ước lượng chuyên gia là cách làm chuẩn mực trong fuzzy logic, không bắt buộc phải suy ra từ big data

### 4.3 IoT & MQTT

- Đổi phần cứng: **ESP8266** - MQTT client điều khiển đèn/còi + đọc cảm biến khoảng cách, camera là điện thoại/webcam qua `cv2`.
- Đổi broker: từ `broker.emqx.io` (public, cần Internet) sang **Mosquitto** cài trên laptop (chạy LAN nội bộ, không cần Internet)
  - MQTT là giao thức (protocol/luật chơi publish-subscribe); Broker là vai trò trung gian; Mosquitto là 1 phần mềm cụ thể đóng vai trò broker (khác EMQX/HiveMQ nhưng cùng nói chung 1 "ngôn ngữ" MQTT)
- Cấu trúc topic đề xuất: `nhom/esp01/khoangcach`, `nhom/esp01/mucdo_nguyhiem`, `nhom/esp01/canhbao_den`, `nhom/esp01/canhbao_coi`, `nhom/esp01/status`
- **bỏ ý tưởng đa camera** — do phải nhân đôi toàn bộ thiết bị IoT. Hướng phát triển nếu cho sau này.

## Tìm hiểu thêm

[`here`](./lwt-qos.md)

- Thêm **LWT (Last Will and Testament)**: Giúp kiểm tra trạng thái thiết bị có đang on hay off hay không.

- QoS: lưu ý khi dùng publish hoặc subscribe một message.

### 4.4 Chế độ Offline / mạng LAN

- Phân biệt 3 loại "offline": AI/laptop (không cần Internet, model đã tải về máy), MQTT broker (cần Mosquitto local thay vì broker công cộng), Web (chạy local trên LAN thay vì deploy cloud).
- Setup LAN nội bộ: laptop + ESP8266 + điện thoại xem demo cùng nối 1 WiFi (router thường hoặc hotspot điện thoại — tắt 4G/5G để test offline thật)
- Các bước kỹ thuật:
  1. Web server phải lắng nghe trên `0.0.0.0` (không chỉ `localhost`) — VD `app.listen(3000, '0.0.0.0')` hoặc Flask `app.run(host='0.0.0.0')`
  2. Tìm IP nội bộ laptop bằng `ipconfig` (Windows) / `ifconfig` (Mac/Linux)
  3. Truy cập từ thiết bị khác cùng mạng qua `http://<IP-laptop>:<port>`
  4. Kiểm tra Windows Defender Firewall nếu không kết nối được (Allow an app through firewall)
  5. ESP8266 khai báo địa chỉ broker MQTT chính là IP laptop, port `1883` (mặc định Mosquitto)
- VS Code Port Forwarding — tạo tunnel qua server ngoài, vẫn cần Internet, chỉ phù hợp khi cần truy cập từ mạng khác (không cùng LAN).

### 4.5 Ảnh bằng chứng & lưu trữ

- Lưu ảnh gọn theo "sự kiện", không lưu mọi frame:
  - Debounce: cùng 1 loài detect liên tục → chỉ lưu 1 ảnh đại diện, bỏ qua đến khi loài đó biến mất khỏi khung hình quá X giây mới cho lưu ảnh mới
  - Chỉ lưu ảnh khi mức nguy hiểm vượt ngưỡng (VD >50%) — loài an toàn không cần lưu bằng chứng
- Dùng code Python upload/xóa ảnh Cloudinary.
- Thiết kế lưu ảnh cho local code nếu như ko có internet bên ngoài (gọi http), sau đó xử lý khi có internet trở lại.
  (quyết định trước khi tải lên nếu mất kn thì lưu trong thư mục code sẵn sau đó admin tự cập nhật trên trình quản lý, thêm ảnh - xóa ở thư mục code. Tự động hóa được coi là cái hướng phát triển.)

## 5. Vấn đề dữ liệu cho phân tích/phân cụm (KHDL) — điểm mấu chốt đã giải quyết

- **Giải pháp cho demo trong thời gian ngắn**: giả lập dữ liệu vận hành 1 tháng bằng script (random timestamp trải dài, random loài theo xác suất hợp lý, random khoảng cách) — nhưng **mức nguy hiểm phải tính bằng đúng hàm fuzzy thật** của hệ thống, không random luôn kết quả. Đây là cách làm phổ biến, chấp nhận được trong đồ án môn học, miễn ghi rõ trong báo cáo: _"Do thời gian đồ án hạn chế, nhóm sử dụng dữ liệu vận hành mô phỏng để minh họa chức năng thống kê/trực quan hóa; hệ thống được thiết kế để hoạt động với dữ liệu thực khi triển khai lâu dài."_
- Có thể áp K-means lên (giờ xuất hiện, loài, mức nguy hiểm, khoảng cách) để tìm pattern (khung giờ nguy hiểm nhất, loài hay xuất hiện...)

## 6. Web sẽ làm gì

- **Live view**: xem camera + trạng thái nhận diện real-time [`here`](./stream-cam-to-web.md)
- **Lịch sử cảnh báo**: bảng log (thời gian, loài, khoảng cách, mức báo động)
- **Thống kê tần suất**: biểu đồ theo ngày/giờ/loài
- **Trạng thái thiết bị IoT**: online/offline (nhờ LWT)
- **Quản lý danh mục loài**: thêm/sửa loài, khoảng cách an toàn, độ hung dữ (admin)
- **Phân quyền**:
  - Khách: không cần đăng nhập, chỉ xem camera trực tiếp
  - Admin: đăng nhập, truy cập toàn bộ dashboard quản trị
  - Triển khai hệ thống jwt kết hợp refresh token lưu cookie.

## 7. Thiết kế cơ sở dữ liệu

- **LOAI_DONG_VAT**: id (PK), ten_lop, khoang_cach_an_toan, do_hung_du, mo_ta

- **THIET_BI** [`note`](./note-db-thietbi.md): id (PK), ten_khu_vuc, mqtt_topic, trang_thai

- **SU_KIEN** (log): id (PK), loai_id (FK), thiet_bi_id (FK), thoi_gian, khoang_cach_do, muc_nguy_hiem, trang_thai_anh (pending/uploaded), duong_dan_local, cloud_id, cloud_url, ghi_chu

- **NGUOI_DUNG**: id (PK), username, password_hash, vai_tro

- **Bảng lưu db refresh token.**

## 8 Một số thắc mắc

- nên để luồng chạy phân tích ai chạy chung với luồng chạy backend hay nên để chung [`HERE`](./note-chay-app.md)
- Cấu trúc thư mục: [`HERE`](./cau-truc-thu-muc.md)
