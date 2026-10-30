import { tokenManager } from "./tokenManager";
export const buildDashBoardSocketURL = () =>{
    // Lấy access token
    const token = tokenManager.get()
    // Lấy URL Backend
    const baseApiURL = import.meta.env.VITE_API_BASE_URL;
    // Biến đổi chuỗi link https -> wss
    const wsBaseURL = baseApiURL.replace("https", "wss");
    // Trả về url để kết nối web socket
    return `${wsBaseURL}/ws/dashboard?token=${token}`;
}