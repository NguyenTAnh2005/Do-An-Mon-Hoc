import clsx from "clsx";
import { Mail, Lock, Recycle } from "lucide-react";

import { Input } from "../components/ui/Input";
import { Button } from "../components/wrapper/Button";
import { CardItem } from "../components/wrapper/CardItem";
import { AppName, AppFullName } from "../constant/navigation";
import { baseTextBg, sectionTitle, mutedText, animateSlow } from "../utils/style";

import {useNavigate} from "react-router-dom";
import { authService } from "../services/auth";
import { useAuth } from "../hooks/useAuth";
import { useState, useEffect } from "react";
import {toast} from 'react-toastify';

const Login = () => {
    const [email, setEmail] = useState(null);
    const [password, setPassword] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const {isAuthenticated, login} = useAuth();

    useEffect(()=>{
        if(isAuthenticated) navigate("/")
    },[isAuthenticated, navigate]);

    const handleLogin = async(e) =>{
        let isMounted = true;
        e.preventDefault();
        setLoading(true);
        try {
            // Nếu đăng nhập thành công thì chuyển hướng tụ động qua index
            const res = await authService.login(email, password);
            if (!isMounted) return
            login(res.access_token);
            toast.success(res.message||"Đăng nhập thành công!");
            navigate("/");
        } catch (err) {
            if (isMounted){
                // Lỗi thì báo hiện lỗi UI
                console.error("[LỖI - Đăng nhập thất bại: ", err);
                toast.error(err.message || "Email hoặc mật khẩu không chính xác!");
            }
        }
        finally{
            if(isMounted){
                setLoading(false);
            }
        }
    }
    return (
        <div className={clsx(baseTextBg, animateSlow, "min-h-screen flex items-center justify-center px-4")}>
            <CardItem styleClass="w-full max-w-md p-8 rounded-xl">
                <form onSubmit={handleLogin}>
                    <div className="flex flex-col items-center text-center gap-2 mb-6">
                        <span className="bg-primary text-white p-3 rounded-full">
                            <Recycle size={28} />
                        </span>
                        <h1 className={sectionTitle}>{AppName}</h1>
                        <p className={clsx(mutedText, "text-sm")}>{AppFullName}</p>
                    </div>

                    <Input 
                        inputType="email" 
                        Icon={Mail} 
                        label="Email" 
                        placeHolder="admin@truong.edu.vn"
                        onChange={(e)=>{setEmail(e.target.value)}}
                    />
                    <Input 
                        inputType="password" 
                        isPassword Icon={Lock} 
                        label="Mật khẩu" 
                        placeHolder="Nhập mật khẩu" 
                        onChange={(e)=>{setPassword(e.target.value)}}
                    />

                    <Button style="w-full mt-4 py-3 rounded-md text-center cursor-pointer">
                        <button type="submit" disabled={loading}>
                            {loading ? "Đang đăng nhập ......." : " Đăng nhập"}
                        </button>
                    </Button>
                </form>
            </CardItem>
        </div>
    );
};

export default Login;