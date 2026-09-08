# Ghi chú đồ án môn học — Hệ thống cảnh báo động vật nguy hiểm (Nông thôn/Trang trại VN)

## 1. Thông tin nhóm

- 3 thành viên:
  - Bạn (người 1) + người 2: code web (FE + BE)
  - Người 3: thiên về lắp ráp IoT
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
- **Hướng phát triển nhóm cũ đề xuất**: nhận diện offline, cải tiến đo khoảng cách, khoảng cách an toàn phụ thuộc loài + vận tốc, **triển khai Platform quản lý tốt hơn** ← đây là cơ sở cho hướng đề tài mới

## 3. Quyết định phạm vi đề tài mới

**Hướng đã chọn**: Mở rộng đồ án IoT+CNN+Fuzzy cũ thành sản phẩm hoàn chỉnh có nền tảng web quản lý, khoanh bối cảnh **Nông thôn/Trang trại VN**.

**Tên đề tài đề xuất**:

> "Xây dựng hệ thống IoT cảnh báo động vật nguy hiểm khu vực nông thôn ứng dụng CNN và logic mờ thích nghi theo loài, tích hợp nền tảng web giám sát thời gian thực"

**Phạm vi loài (7 loài)** — có cả loài nguy hiểm và loài an toàn để fuzzy logic có đối chiếu rõ:

| Loài         | Vai trò                   | Khoảng cách an toàn (m) | Độ hung dữ (1-10) |
| ------------ | ------------------------- | ----------------------- | ----------------- |
| Rắn độc      | Nguy hiểm cao             | 2                       | 8                 |
| Lợn rừng     | Nguy hiểm cao             | 8                       | 8                 |
| Trâu/Bò      | Nguy hiểm trung bình-cao  | 5                       | 7                 |
| Chó thả rông | Nguy hiểm trung bình      | 3                       | 6                 |
| Khỉ          | Nguy hiểm thấp-trung bình | 3                       | 5                 |
| Mèo          | An toàn (baseline)        | 1                       | 2                 |
| Gà/Vịt       | An toàn (baseline)        | 0.5                     | 1                 |

> **Lưu ý quan trọng đã chốt**: bỏ ý tưởng "chó dại" — CNN không thể nhận diện bệnh dại qua hình ảnh (dại là biểu hiện hành vi/sinh lý, không phải đặc điểm ngoại hình). Đổi thành "chó thả rông/chó lạ" — CNN chỉ detect "chó", còn mức nguy hiểm do fuzzy logic tính dựa trên khoảng cách + độ hung dữ mặc định của loài.

**Dataset**: kiểm tra nhanh xác nhận Roboflow Universe có sẵn dataset cho rắn, chó, trâu/bò, khỉ (phổ biến); lợn rừng có nhưng ít hơn — có thể fork gộp nhiều nguồn nhỏ như cách nhóm cũ đã làm. Chấp nhận ảnh Roboflow không khớp hoàn toàn bối cảnh nông thôn VN, ghi vào phần hạn chế báo cáo.

## 4. Các cải tiến kỹ thuật đã thống nhất

### 4.1 CNN

- Thử nghiệm train lại ở input **640×640** (mặc định YOLOv8) thay vì 224×224 — so sánh hiệu năng, đặc biệt kỳ vọng cải thiện mAP50-95 đang thấp
- Khi thêm loài mới: **fine-tune từ checkpoint cũ** (`yolo train model=best_v1.pt data=data_v2.yaml`), không train từ đầu — model kế thừa trọng số cũ, nhanh hơn. Kết quả là 1 file `.pt` mới chứa đủ các loài (cũ + mới), đặt tên version rõ ràng (`best_v1.pt`, `best_v2.pt`...), lưu trên GitHub Release/Google Drive (thay Dagshub)

### 4.2 Fuzzy Logic

- Giữ nguyên kiến trúc 2-input hiện tại
- Cải tiến: **chuẩn hóa input "khoảng cách" theo tỷ lệ so với khoảng cách an toàn của từng loài** (khoảng cách đo được / khoảng cách an toàn loài đó) thay vì dùng số tuyệt đối chung cho mọi loài — giải quyết vấn đề "100m với báo/sư tử khác hoàn toàn 100m với mèo/bò"
- Bảng khoảng cách an toàn + độ hung dữ theo loài lưu trong DB (không phải hard-code), heuristic/ước lượng chuyên gia là cách làm chuẩn mực trong fuzzy logic, không bắt buộc phải suy ra từ big data

### 4.3 IoT & MQTT

- Đổi phần cứng: **ESP8266** (rẻ hơn ESP32-CAM, không cần dùng camera trên chip vì camera là điện thoại/webcam qua `cv2`, ESP8266 chỉ làm MQTT client điều khiển đèn/còi + đọc cảm biến khoảng cách)
- Đổi broker: từ `broker.emqx.io` (public, cần Internet) sang **Mosquitto** cài trên laptop (chạy LAN nội bộ, không cần Internet)
  - MQTT là giao thức (protocol/luật chơi publish-subscribe); Broker là vai trò trung gian; Mosquitto là 1 phần mềm cụ thể đóng vai trò broker (khác EMQX/HiveMQ nhưng cùng nói chung 1 "ngôn ngữ" MQTT)
- Cấu trúc topic đề xuất: `nhom/esp01/khoangcach`, `nhom/esp01/mucdo_nguyhiem`, `nhom/esp01/canhbao_den`, `nhom/esp01/canhbao_coi`, `nhom/esp01/status`
- Thêm **LWT (Last Will and Testament)**: ESP8266 dặn trước broker tự động báo "offline" lên topic `status` nếu mất kết nối đột ngột — web biết ngay thiết bị có sống hay không
- QoS: 0 cho dữ liệu cảm biến liên tục (mất 1 gói không sao), QoS 1 cho lệnh cảnh báo (phải đảm bảo tới nơi)
- Đã cân nhắc và **bỏ ý tưởng đa camera** — do phải nhân đôi toàn bộ thiết bị IoT (ESP8266 + cảm biến + đèn/còi) cho mỗi camera thêm, tốn kinh phí/công lắp ráp không cần thiết cho scope 1 học kỳ. Có thể ghi vào "Hướng phát triển" của báo cáo.

### 4.4 Chế độ Offline / mạng LAN

- Phân biệt 3 loại "offline": AI/laptop (không cần Internet, model đã tải về máy), MQTT broker (cần Mosquitto local thay vì broker công cộng), Web (chạy local trên LAN thay vì deploy cloud)
- Setup LAN nội bộ: laptop + ESP8266 + điện thoại xem demo cùng nối 1 WiFi (router thường hoặc hotspot điện thoại — tắt 4G/5G để test offline thật)
- Các bước kỹ thuật:
  1. Web server phải lắng nghe trên `0.0.0.0` (không chỉ `localhost`) — VD `app.listen(3000, '0.0.0.0')` hoặc Flask `app.run(host='0.0.0.0')`
  2. Tìm IP nội bộ laptop bằng `ipconfig` (Windows) / `ifconfig` (Mac/Linux)
  3. Truy cập từ thiết bị khác cùng mạng qua `http://<IP-laptop>:<port>`
  4. Kiểm tra Windows Defender Firewall nếu không kết nối được (Allow an app through firewall)
  5. ESP8266 khai báo địa chỉ broker MQTT chính là IP laptop, port `1883` (mặc định Mosquitto)
- **Không dùng** VS Code Port Forwarding/Dev Tunnels hay ngrok cho demo offline — các công cụ này tạo tunnel qua server ngoài, vẫn cần Internet, chỉ phù hợp khi cần truy cập từ mạng khác (không cùng LAN)

### 4.5 Ảnh bằng chứng & lưu trữ (thay thế Dagshub)

- Bỏ Dagshub hoàn toàn — chỉ cần lưu ảnh gọn theo "sự kiện", không lưu mọi frame:
  - Debounce: cùng 1 loài detect liên tục → chỉ lưu 1 ảnh đại diện, bỏ qua đến khi loài đó biến mất khỏi khung hình quá X giây mới cho lưu ảnh mới
  - Chỉ lưu ảnh khi mức nguy hiểm vượt ngưỡng (VD >50%) — loài an toàn không cần lưu bằng chứng
  - Có thể set TTL tự xoá ảnh cũ (VD sau 30 ngày)
- Dùng lại code Python upload/xóa ảnh Cloudinary đã có sẵn từ dự án khác
- **Thiết kế offline-first / fault-tolerant** cho upload:
  1. Ảnh confidence cao nhất luôn lưu vào ổ cứng local trước (luôn thành công, không cần Internet)
  2. Ghi DB với `trang_thai_anh = "pending"`
  3. Bọc lệnh gọi Cloudinary trong `try/except` — lỗi không crash hệ thống, giữ nguyên `pending`
  4. **Background job** (VD dùng APScheduler trong Python) chạy định kỳ (VD mỗi 5 phút), quét các bản ghi `pending`, thử upload lại — khi có Internet trở lại thì tự đồng bộ hết, không cần can thiệp tay
  5. Chỉ **xóa file local sau khi xác nhận upload thành công** (trong khối `try`, sau dòng upload) — tránh mất bằng chứng nếu upload lỗi
- Model `.pt` không lưu Cloudinary — lưu GitHub Release hoặc Google Drive theo version

## 5. Vấn đề dữ liệu cho phân tích/phân cụm (KHDL) — điểm mấu chốt đã giải quyết

- **Tách rõ 2 loại dữ liệu khác nhau**:
  | Loại dữ liệu | Dùng để làm gì | Nguồn |
  |---|---|---|
  | Dataset ảnh huấn luyện CNN | Train model nhận diện loài | Roboflow (có sẵn) |
  | Dữ liệu vận hành (operational log) | Phân tích/phân cụm/trực quan hóa trên web | **Hệ thống tự sinh ra khi chạy** |
- Nỗi lo "dataset ngoài khó tìm, tự thu thập thì lâu" chỉ áp dụng cho loại 1 — loại 2 không phụ thuộc nguồn ngoài, tự lớn dần theo số lần hệ thống chạy
- **Giải pháp cho demo trong thời gian ngắn**: giả lập dữ liệu vận hành 1 tháng bằng script (random timestamp trải dài, random loài theo xác suất hợp lý, random khoảng cách) — nhưng **mức nguy hiểm phải tính bằng đúng hàm fuzzy thật** của hệ thống, không random luôn kết quả. Đây là cách làm phổ biến, chấp nhận được trong đồ án môn học, miễn ghi rõ trong báo cáo: _"Do thời gian đồ án hạn chế, nhóm sử dụng dữ liệu vận hành mô phỏng để minh họa chức năng thống kê/trực quan hóa; hệ thống được thiết kế để hoạt động với dữ liệu thực khi triển khai lâu dài."_
- Có thể áp K-means lên (giờ xuất hiện, loài, mức nguy hiểm, khoảng cách) để tìm pattern (khung giờ nguy hiểm nhất, loài hay xuất hiện...)

## 6. Web sẽ làm gì

- **Live view**: xem camera + trạng thái nhận diện real-time
- **Lịch sử cảnh báo**: bảng log (thời gian, loài, khoảng cách, mức báo động)
- **Thống kê tần suất**: biểu đồ theo ngày/giờ/loài
- **Trạng thái thiết bị IoT**: online/offline (nhờ LWT)
- **Quản lý danh mục loài**: thêm/sửa loài, khoảng cách an toàn, độ hung dữ (admin)
- **Phân quyền**:
  - Khách: không cần đăng nhập, chỉ xem camera trực tiếp
  - Admin: đăng nhập, truy cập toàn bộ dashboard quản trị
  - Triển khai bằng session/JWT + middleware kiểm tra `vai_tro`, dùng thư viện có sẵn (Flask-Login / express-session / jsonwebtoken)

## 7. Thiết kế cơ sở dữ liệu (đã chốt, có sơ đồ ERD trong hội thoại)

4 bảng chính:

- **LOAI_DONG_VAT**: id (PK), ten_lop, khoang_cach_an_toan, do_hung_du, mo_ta
- **THIET_BI**: id (PK), ten_khu_vuc, mqtt_topic, trang_thai
- **SU_KIEN** (log): id (PK), loai_id (FK), thiet_bi_id (FK), thoi_gian, khoang_cach_do, muc_nguy_hiem, trang_thai_anh (pending/uploaded), duong_dan_local, cloud_id, cloud_url, ghi_chu
- **NGUOI_DUNG**: id (PK), username, password_hash, vai_tro

**Về câu hỏi CSV vs DB**: chốt dùng chung 1 DB cho mọi bảng (kể cả bảng loài động vật, ít thay đổi) — không cần tách riêng CSV. Nỗi lo "trễ" không phụ thuộc CSV hay DB mà phụ thuộc có tra cứu mỗi frame hay không. Giải pháp: **load bảng LOAI_DONG_VAT vào cache RAM (dictionary) lúc khởi động chương trình**, tra cứu từ RAM thay vì query DB mỗi lần detect — chỉ nạp lại cache khi admin sửa dữ liệu qua web.

## 8. Câu hỏi đang mở — CHƯA trả lời xong trong hội thoại

1. **"Chạy khởi động" (cache lúc startup) là gì, cơ chế cụ thể ra sao** — user chưa rõ, cần giải thích lại dễ hiểu hơn (có thể dùng ví dụ cụ thể theo đúng stack code nhóm dùng)
2. **Code web có tách biệt thư mục với code thực thi AI hay không** — cần làm rõ kiến trúc thư mục dự án (mono-repo hay tách repo, cách 2 phần giao tiếp với nhau — có thể qua API nội bộ hoặc cùng chung 1 server)
3. **Camera gắn trên web là loại cam nào**: dùng cam qua `cv2` (webcam thường) hay dùng chính camera điện thoại quay (do hạn chế kinh phí, không mua thêm thiết bị cam riêng) — cần chốt phương án và nêu rõ cách camera điện thoại truyền hình ảnh vào code xử lý (qua app IP camera như nhóm cũ đã dùng)

## 9. Việc cần làm tiếp theo

- Trả lời 3 câu hỏi mở ở mục 8
- Sau khi thống nhất xong các câu hỏi mở, gom toàn bộ nội dung thành **đề cương sơ bộ**: tên đề tài chính thức, mục tiêu đo lường được, phạm vi, đánh giá tính khả thi, kế hoạch thực hiện theo tuần, phân công RACI theo 3 thành viên
