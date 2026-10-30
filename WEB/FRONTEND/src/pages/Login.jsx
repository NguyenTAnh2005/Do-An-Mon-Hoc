import clsx from "clsx";
import { Mail, Lock, Recycle, Leaf, ShieldCheck, Wifi } from "lucide-react";

import { Input } from "../components/ui/Input";
import { Button } from "../components/wrapper/Button";
import { CardItem } from "../components/wrapper/CardItem";
import { AppName, AppFullName } from "../constant/navigation";
import {
    baseTextBg, sectionTitle, bodyLarge, mutedText, animateSlow
} from "../utils/style";

import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";
import { useAuth } from "../hooks/useAuth";
import { useState, useEffect } from "react";
import { toast } from 'react-toastify';

const Login = () => {
    const [email, setEmail] = useState(null);
    const [password, setPassword] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { isAuthenticated, login } = useAuth();

    useEffect(() => {
        if (isAuthenticated) navigate("/");
    }, [isAuthenticated, navigate]);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await authService.login(email, password);
            login(res.access_token);
            toast.success(res.message || "Đăng nhập thành công!");
            navigate("/");
        } catch (err) {
            console.error("[LỖI - Đăng nhập thất bại: ", err);
            toast.error(err.message || "Email hoặc mật khẩu không chính xác!");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={clsx(
            baseTextBg, animateSlow,
            "min-h-screen flex items-center justify-center px-4 py-8 relative overflow-hidden"
        )}>
            {/* Nền trang trí */}
            <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
                <div className="absolute -top-32 -left-32 h-[28rem] w-[28rem] rounded-full bg-primary/10 blur-3xl" />
                <div className="absolute -bottom-32 -right-32 h-[28rem] w-[28rem] rounded-full bg-primary/15 blur-3xl" />
            </div>

            <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 md:gap-12 items-center">
                {/* CỘT TRÁI — GIỚI THIỆU (ẩn trên mobile) */}
                <div className="hidden md:flex flex-col gap-8 p-4">
                    <div className="flex items-center gap-3">
                        <span className="bg-primary text-white p-3 rounded-xl shadow-lg shadow-primary/30">
                            <Recycle size={30} />
                        </span>
                        <div className="flex flex-col leading-tight">
                            <span className="text-2xl font-bold">{AppName}</span>
                            <span className={clsx(mutedText, "text-sm")}>{AppFullName}</span>
                        </div>
                    </div>

                    <div className="flex flex-col gap-3">
                        <h2 className={sectionTitle}>Giải pháp quản lý rác thông minh</h2>
                        <p className={clsx(mutedText, bodyLarge)}>
                            Theo dõi mức đầy, giám sát thiết bị theo thời gian thực và tối ưu
                            quy trình thu gom — tất cả trong một bảng điều khiển duy nhất.
                        </p>
                    </div>

                    <div className="flex flex-col gap-3 mt-2">
                        <FeatureRow Icon={Wifi} text="Cập nhật realtime qua WebSocket" />
                        <FeatureRow Icon={ShieldCheck} text="Bảo mật bằng JWT và tài khoản quản trị" />
                        <FeatureRow Icon={Leaf} text="Tối ưu quy trình thu gom và tái chế" />
                    </div>
                </div>

                {/* CỘT PHẢI — FORM ĐĂNG NHẬP */}
                <CardItem styleClass="w-full max-w-md mx-auto p-8 rounded-2xl">
                    <form onSubmit={handleLogin} className="flex flex-col">
                        {/* Thương hiệu — hiển thị trên mobile */}
                        <div className="flex md:hidden flex-col items-center text-center gap-2 mb-6">
                            <span className="bg-primary text-white p-3 rounded-full">
                                <Recycle size={28} />
                            </span>
                            <h1 className={sectionTitle}>{AppName}</h1>
                            <p className={clsx(mutedText, "text-sm")}>{AppFullName}</p>
                        </div>

                        {/* Tiêu đề — hiển thị trên desktop */}
                        <div className="hidden md:flex flex-col gap-1 mb-6">
                            <h2 className="text-2xl font-bold">Chào mừng trở lại 👋</h2>
                            <p className={clsx(mutedText, "text-sm")}>
                                Đăng nhập để tiếp tục quản lý hệ thống
                            </p>
                        </div>

                        <Input
                            inputType="email"
                            Icon={Mail}
                            label="Email"
                            placeHolder="admin@truong.edu.vn"
                            onChange={(e) => { setEmail(e.target.value); }}
                        />
                        <Input
                            inputType="password"
                            isPassword
                            Icon={Lock}
                            label="Mật khẩu"
                            placeHolder="Nhập mật khẩu"
                            onChange={(e) => { setPassword(e.target.value); }}
                        />

                        <Button style="w-full mt-4 py-3 rounded-md text-center cursor-pointer">
                            <button
                                type="submit"
                                disabled={loading}
                                className="font-semibold disabled:opacity-60"
                            >
                                {loading ? "Đang đăng nhập..." : "Đăng nhập"}
                            </button>
                        </Button>
                    </form>
                </CardItem>
            </div>
        </div>
    );
};

const FeatureRow = ({ Icon, text }) => (
    <div className="flex items-center gap-3">
        <span className="h-9 w-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <Icon size={18} />
        </span>
        <span className={clsx(mutedText, "text-sm")}>{text}</span>
    </div>
);

export default Login;