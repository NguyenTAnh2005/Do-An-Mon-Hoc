```bash
├── 📁 BACKEND
│   ├── 📁 alembic
│   ├── 📁 app                    # Web thuần: routes, CRUD, auth, schemas
│   │   ├── 📁 core
│   │   ├── 📁 crud
│   │   ├── 📁 models
│   │   ├── 📁 routers
│   │   ├── 📁 schemas
│   │   ├── 📁 service
│   │   └── 🐍 db_connection.py
│   │
│   ├── 📁 ai_engine               # ← Module CNN + Fuzzy Logic
│   │   ├── 📁 detector             # load YOLOv8, hàm predict(frame)
│   │   │   ├── 🐍 model_loader.py
│   │   │   └── 🐍 infer.py
│   │   ├── 📁 fuzzy                # logic mờ Mamdani
│   │   │   └── 🐍 fuzzy_engine.py
│   │   ├── 📁 weights               # lưu file .pt (hoặc chỉ path, file thật để .gitignore)
│   │   ├── 🐍 species_cache.py     # cache RAM (mục đã bàn)
│   │   └── 🐍 camera_worker.py     # vòng lặp cv2.read() + gọi detector + fuzzy
│   │
│   ├── 📁 iot                     # ← Module phần cứng + MQTT
│   │   ├── 🐍 mqtt_client.py       # paho-mqtt: connect, publish, subscribe
│   │   ├── 🐍 topics.py            # định nghĩa hằng số topic (tránh hard-code rải rác)
│   │   ├── 🐍 lwt_handler.py       # xử lý Last Will and Testament, update trang_thai
│   │   └── 🐍 handlers.py          # callback khi nhận message MQTT (VD ghi SU_KIEN)
│   │
│   ├── 📁 analytics               # ← Module phân tích/phân cụm KHDL
│   │   ├── 🐍 kmeans_pipeline.py
│   │   ├── 🐍 simulate_data.py     # script giả lập dữ liệu 1 tháng (mục 5 đã bàn)
│   │   └── 🐍 aggregations.py      # tính toán thống kê tần suất cho web
│   │
│   ├── 📝 README.md
│   ├── 🐍 main.py                 # nơi "lắp ráp" tất cả: import app, ai_engine, iot
│   ├── 📄 requirements.txt
```
