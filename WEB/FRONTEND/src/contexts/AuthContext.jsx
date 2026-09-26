/* eslint-disable react-refresh/only-export-components */

import 
{ createContext, 
    useEffect, useState 
} from "react";

import { authService } from "../services/auth";
import { tokenManager } from "../services/tokenManager";
import { StatusLoading } from "../components/ui/FetchStatus";

// Tạo context Auth bằng createContext
//  Tạo provider, return context.provider + value = { đống thông tin cần lưu}
//  value cần lưu: Đang đăng nhập, token
//  ngoài ra cần lưu hàm: login, logout, clearToken

export const AuthContext = createContext();

export const AuthProvider = ({children})=>{
    const [loading, setLoading] = useState(true);
    const [accessToken, setAccessToken] = useState(null);

    useEffect(()=>{
        // Cờ báo componnet đang mount (đang được gọi render JSX)
        let isMounted = true;
        const initializeAuth = async ()=>{
            console.log("[AuthContext]: useEffect start");
            // Chạy api
            try {
                //  Api 1 yêu cầu cấp accessToken 
                const tokenResponse = await authService.refreshToken();
                console.log("[AuthContext]: calling refreshToken api");
                if(!isMounted)return;
                tokenManager.setOneSide(tokenResponse.access_token);
                setAccessToken(tokenResponse.access_token);

            } catch (error) {
                // Bị lỗi thì clear toàn bộ + bên Protected cũng xử lý đá về login vì biến isAuthenticated sẽ false
                if (!isMounted) return;
                console.error(
                "Auth initialization failed:",
                error.message
                );
                tokenManager.clear();
                setAccessToken(null);
            }
            finally{
                if(isMounted){setLoading(false);}
            }
        }
        initializeAuth();

        // Đăng ký function bên tokenManager (subcribe)
        tokenManager.subcribe(setAccessToken);

        return ()=>{
            isMounted=false;
            tokenManager.unSubcribe(setAccessToken);
            console.log("[AuthContext]: Clean up useEffect");
        }
    },[]);

    const clearToken = () =>{
        tokenManager.clear();
        setAccessToken(null);
    }

    async function login(newToken){
        // Lưu access token bên manager sau đó cập nhật state rồi gọi get admin
        tokenManager.setOneSide(newToken);
        setAccessToken(newToken);
    };

    async function logout(){ 
        // Gọi logout để backend làm việc các thứ sau đó xóa access_token
        await authService.logOut();
        clearToken();
    };

    const value = {
        accessToken,
        // (if access_token là access_token khác null)
        // Dấu ! đầu tiên: nếu !access_token -> nếu có token thì là False, không có thì là True
        // Dấu ! thứ high: biến đổi ngược lại cho đúng, Ô khê.
        isAuthenticated: !!accessToken,
        clearToken, 
        login,
        logout
    };
    
    let content;
    if (loading){content=<StatusLoading/>}
    else{
        content =(
            <AuthContext.Provider value={value}>
                {children}
            </AuthContext.Provider>
        )
    }
    return content;
}
