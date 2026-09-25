import clsx from "clsx";
import { Mail, Lock, Recycle } from "lucide-react";

import { Input } from "../components/ui/Input";
import { Button } from "../components/wrapper/Button";
import { CardItem } from "../components/wrapper/CardItem";
import { AppName, AppFullName } from "../constant/navigation";
import { baseTextBg, sectionTitle, mutedText, animateSlow } from "../utils/style";

const Login = () => {
    return (
        <div className={clsx(baseTextBg, animateSlow, "min-h-screen flex items-center justify-center px-4")}>
            <CardItem styleClass="w-full max-w-md p-8 rounded-xl">
                <div className="flex flex-col items-center text-center gap-2 mb-6">
                    <span className="bg-primary text-white p-3 rounded-full">
                        <Recycle size={28} />
                    </span>
                    <h1 className={sectionTitle}>{AppName}</h1>
                    <p className={clsx(mutedText, "text-sm")}>{AppFullName}</p>
                </div>

                <Input inputType="email" Icon={Mail} label="Email" placeHolder="admin@truong.edu.vn" />
                <Input inputType="password" isPassword Icon={Lock} label="Mật khẩu" placeHolder="Nhập mật khẩu" />

                <Button style="w-full mt-4 py-3 rounded-md text-center cursor-pointer">
                    Đăng nhập
                </Button>
            </CardItem>
        </div>
    );
};

export default Login;