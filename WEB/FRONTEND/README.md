# 🤖 FRONTEND

Thực hiện code frontend, còn rất nhiều thứ để học hỏi nhưng sẽ cố gắng.

# 🗿 Các thư viện sử dụng để hỗ trợ

### 1. Nhóm cơ bản

- React & React-DOM: Có sẵn khi khởi tạo dự án
- Vite: Công cụ hỗ trợ build code nhanh
- Tailwind CSS: Thư viện CSS đa dạng với các class tiện, đi kèm là các thư viện nhỏ giúp tương thích ở nhiều trình duyệt

### 2. Nhóm Điều hướng & Dữ liệu (Routing & Data)

- react-router-dom: Xử lý việc chuyển trang của REACT.
- axios: Thư viện dùng để gọi API (HTTP Client). Nó sẽ nói chuyện với Backend FastAPI để gọi EndPoint.

### 3. Nhóm Trang trí & Hiệu ứng (UI Assets)

- clsx: Giúp viết điều kiện logic cho class (ví dụ: nếu lỗi thì hiện màu đỏ).
- lucide-react: Kho Icon React hiện đại, tính đồng nhất cao.
- react-icons: kho thư viện icon rất lớn, chủ yếu sẽ bổ sung các dạng icon còn thiếu của Lucide
- framer-motion: Thư viện làm Animation. Dùng để làm các hiệu ứng như: nội dung từ từ mờ dần hiện lên khi cuộn chuột, ảnh nảy lên khi hover...
- antd (Ant Design): Thư viện UI Component.
- react-toastify: Thư viện thông báo alert.
- react-icons: Thư viện icon đa dạng hơn lucide ( Chủ yếu dùng để import logo Brand)

# 💻 Lệnh cài đặt các thư viện trên

### Kiểm tra file packeage.json để xác minh

```bash
# Lệnh Cài tailwind CSS
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p

# Lệnh cài tổng hợp các thư viện
npm install react-router-dom axios
npm install lucide-react react-icons framer-motion
npm install antd clsx
npm install react-toastify
```

## Setup dự án

### 1. Setup Tailwind

Sau khỉ tải xong thì chỉnh các file cần thiết:

- tailwind.config.js

```js
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

- trong file index.css import các đoạn code này, sau đó import file index.css vào main.jsx

```bash
@tailwind base;
@tailwind components;
@tailwind utilities;
```
