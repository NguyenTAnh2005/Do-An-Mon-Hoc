import { useState, useEffect } from "react";
import { Moon, Sun } from 'lucide-react';
import { motion } from "framer-motion";
import { Button } from "../wrapper/Button";
function ThemeToggle() {
    // 1. KHỞI TẠO BỘ NHỚ (State + LocalStorage)
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('theme') || 'light';
    });

    // 2. ĐỒNG BỘ HÓA GIAO DIỆN (Side Effect)
    useEffect(() => {
        const htmlElement = document.documentElement; // Tóm lấy thẻ <html> cao nhất

        if (theme === 'dark') {
            htmlElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [theme]); // <-- Chỉ kích hoạt khi 'theme' có sự thay đổi

    // Dùng prevTheme (giá trị trước đó) để lật ngược trạng thái an toàn tuyệt đối
    const toggleTheme = () => {
        setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
    };

    return (
        <Button style={"rounded-md "}>
            <div
                onClick={toggleTheme} 
                className="  flex items-center justify-center w-12 h-12 transition-all ease-linear duration-500"
            >
                {theme === 'light' ? (
                    <motion.div
                        key={"light"}
                        initial={{opacity:0, x:-25, rotate:-90}}
                        animate={{opacity:1, x: 0, rotate:0}}
                        exit={{opacity:0, x:-25, rotate:-90}}
                        transition={{duration:0.5, ease:"easeInOut"}}

                    >
                        <Sun size={28} />
                    </motion.div>
                ) : (
                    <motion.div
                        key={"dark"}
                        initial={{opacity:0, x:25, rotate:90}}
                        animate={{opacity:1, x:0, rotate:0}}
                        exit={{opacity:0, x:25, rotate:90}}
                        transition={{duration:0.5, ease:"easeInOut"}}
                    >
                        <Moon size={28} />
                    </motion.div>
                )}
            </div>
        </Button>
    );
}

export default ThemeToggle;