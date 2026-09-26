// INSTANCE CÓ XỬ LÝ BẮT LỖI 401 (GỌI NGẦM CẤP ACCESS TOKEN) KHI THẤT BẠI

// Phần lớn API của web app đều sử dụng thằng này
import axios from "axios";
import { tokenManager } from "../tokenManager";
import { authService } from '../auth';
import { navigateLogIn } from "../../utils/navigateLogIn";

const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers:{
        'Content-Type': 'application/json',
    },
    // Không cần yêu cầu trình duyệt tự gắn cookie
    // vì đa phần API này không cần dùng refresh token làm gì cả
});

// Bên Request 
axiosInstance.interceptors.request.use(
    (config) =>{
        // tự động gán access_token vào header NẾU CÓ
        if(tokenManager.get()){
            config.headers.Authorization = `Bearer ${tokenManager.get()}`;
            return config;
        }
        //  Không có thì vẫn trả về bình thường
        return config;
    },
    (error) =>{
        // Biến nó thành fail 
        // Cho phép bên jsx có thể dùng try catch và bắt được lỗi này 
        // và xử lý thích hợp (in ra màn hình lỗi).
        return Promise.reject(error);
    }
)


// Bên Response thì nếu lỗi sẽ xử lý lỗi 401 riêng ( gọi refresh, )
// Cấu trúc response xem trong file doc note error handling nhé.
axiosInstance.interceptors.response.use(
    (response) =>{
        return response.data
    },
    async (error) =>{
        // Khi request thất bại thì axios quản lý 2 thứ trong object error
        // error.config chứa thông tin cấu hình request cũ
        // error.response chứa thông tin phản hồi lỗi
        const originalRequest = error.config;
        // Bắt lỗi 401
        //  nếu như lỗi và retry khác null (undefined)
        if(error.response && error.response.status === 401 && !originalRequest._retry){
            try {
                // Gọi cấp access token ngầm 
                // New access_token được trả về ở res.access_token
                const res = await authService.refreshToken();
                
                // Cập nhật bên đối tượng (có publish hàm cập nhật trong useAuth nên nó tự cập nhật theo)
                tokenManager.setTwoSide(res.access_token);

                //  Tạo mới header key auth và gửi lại request trước
                const newHeader = `Bearer ${res.access_token}`;
                originalRequest._retry = true;
                originalRequest.headers['Authorization'] = newHeader;
                return axiosInstance(originalRequest);
            } catch (error) {
                // Lỗi khi chạy refresh thất bại (res thất bại thì mấy cái dưới mới sai theo)
                console.error(`Lỗi: Phiên đăng nhập không hợp lệ! Vui lòng đăng nhập lại. [message: <${error.message}>]`);
                // Cập nhật clear ở access_token (không có publish clear nên set bằng null vậy)
                tokenManager.setTwoSide(null);
                // Điều hướng ra Login thì bên Protected đã lo cho hết rồi. nên ở đây khỏi ik.
                navigateLogIn();
            }
        }
        // Lỗi nếu request gọi lại lần nữa bị lỗi
        return Promise.reject(error.response?.data || error);
    }
)

export default axiosInstance;