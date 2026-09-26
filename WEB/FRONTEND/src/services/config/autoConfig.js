// INSTANCE KHÔNG XỬ LÝ BẮT LỖI 401 (GỌI NGẦM CẤP ACCESS TOKEN) KHI THẤT BẠI

// 3 API đầu tiên của auth bên backend dùng thằng này
import axios from "axios";

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{
        'Content-Type': 'application/json',
    },
    // bật true để bắt buộc trình duyệt tự động đính kèm cookie vào request để gọi API.
    withCredentials:true
});

// Bên Request hiện tại chưa cần config gửi access_token vào header

// Bên Response thì nếu lỗi sẽ trả về lỗi chứ chưa cần xử lý nhiều
// Cấu trúc response xem trong file doc note error handling nhé.
axiosInstance.interceptors.response.use(
    (response) =>{
        return response.data
    },
    (error) =>{
        // Biến lỗi thành fail dưới dạng Promise
        // Cái lỗi này sẽ được lấy ra khi bên JSX sử dụng 
        // try catch để làm việc với Instance này
        console.error("AUTO AXIOS ERROR:", {
            status: error.response?.status,
            data: error.response?.data,
            url: error.config?.url,
        });
        return Promise.reject(error.response?.data || error);
    }
)

export default axiosInstance;