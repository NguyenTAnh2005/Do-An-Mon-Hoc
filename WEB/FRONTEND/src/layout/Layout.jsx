// src/layout/Layout.jsx
import { Outlet, Link, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useState, useEffect } from "react";
import clsx from "clsx";
import { Menu, X, Recycle } from "lucide-react";

import { ListNavItems, AppName } from "../constant/navigation";
import ThemeToggle from "../components/ui/ThemeToggle";
import {
    baseTextBg, animateSlow, animateFast, bgSurface, baseBorder, mutedText
} from "../utils/style";

export const Layout = () => {
    const location = useLocation();

    // Desktop: mở/thu gọn sidebar — luôn mặc định mở khi load lại trang
    const [expanded, setExpanded] = useState(true);
    // Mobile: sidebar dạng drawer, mặc định đóng
    const [mobileOpen, setMobileOpen] = useState(false);

    // Tự động cuộn lên đầu trang + đóng drawer mobile khi đổi route
    useEffect(() => {
        window.scroll(0, 0);
        setMobileOpen(false);
    }, [location]);

    const toggleExpanded = () => setExpanded(prev => !prev);
    const toggleMobile = () => setMobileOpen(prev => !prev);

    // Trên mobile, drawer luôn full width nên label luôn hiện khi drawer mở
    const showLabel = expanded || mobileOpen;

    return (
        <div className={clsx(baseTextBg, "flex min-h-screen")}>
            {/* TOP BAR — CHỈ HIỆN TRÊN MOBILE, cao cố định h-16 để làm mốc cho các offset khác */}
            <div className={clsx(
                bgSurface, baseBorder, animateSlow,
                "md:hidden border-b-2 flex items-center justify-between px-4 h-16",
                "fixed top-0 left-0 right-0 z-50"
            )}>
                <Link to="/" className="flex items-center gap-2">
                    <span className="bg-primary text-white p-2 rounded-md">
                        <Recycle size={20} />
                    </span>
                    <span className="text-lg font-bold">{AppName}</span>
                </Link>
                <button
                    aria-label={mobileOpen ? "Đóng menu" : "Mở menu"}
                    onClick={toggleMobile}
                    className={clsx(animateFast, mutedText, "p-2 hover:text-primary cursor-pointer")}
                >
                    {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* BACKDROP — CHỈ HIỆN KHI DRAWER MOBILE MỞ, nằm dưới topbar để không che nút X */}
            <AnimatePresence>
                {mobileOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        onClick={() => setMobileOpen(false)}
                        className="md:hidden fixed top-16 inset-x-0 bottom-0 bg-black/40 z-30"
                    />
                )}
            </AnimatePresence>

            {/* SIDEBAR — width chuyển bằng class Tailwind (animateSlow lo transition), không dùng motion cho width để tránh xung đột mobile/desktop */}
            <aside
                className={clsx(
                    bgSurface, baseBorder, animateSlow,
                    "border-r-2 flex flex-col justify-between shrink-0 overflow-hidden z-40",
                    // Desktop: sticky, chiếm chỗ trong flex row, width đổi theo expanded
                    "md:sticky md:top-0 md:h-screen md:translate-x-0",
                    expanded ? "md:w-64" : "md:w-20",
                    // Mobile: fixed, full width drawer, bắt đầu dưới topbar, trượt vào/ra theo mobileOpen
                    "fixed top-16 left-0 h-[calc(100vh-4rem)] w-64",
                    mobileOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div>
                    {/* BRAND — ẨN TRÊN MOBILE VÌ ĐÃ CÓ Ở TOP BAR */}
                    <div className="hidden md:flex items-center p-4">
                        <Link to="/" className="flex items-center gap-2 overflow-hidden">
                            <span className="shrink-0 bg-primary text-white p-2 rounded-md">
                                <Recycle size={22} />
                            </span>
                            <AnimatePresence>
                                {expanded && (
                                    <motion.span
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -10 }}
                                        transition={{ duration: 0.2 }}
                                        className="text-xl font-bold whitespace-nowrap"
                                    >
                                        {AppName}
                                    </motion.span>
                                )}
                            </AnimatePresence>
                        </Link>
                    </div>

                    {/* NÚT ĐÓNG/MỞ — CHỈ CHO DESKTOP, MOBILE DÙNG NÚT Ở TOP BAR */}
                    <div className="hidden md:block px-4 pb-2 pt-2">
                        <button
                            aria-label={expanded ? "Thu gọn sidebar" : "Mở rộng sidebar"}
                            onClick={toggleExpanded}
                            className={clsx(
                                animateFast, baseBorder, mutedText,
                                "border-2 flex items-center justify-center w-full p-2 rounded-md hover:text-primary hover:border-primary cursor-pointer"
                            )}
                        >
                            {expanded ? <X size={20} /> : <Menu size={20} />}
                        </button>
                    </div>

                    {/* NAV ITEMS */}
                    <div className="flex flex-col gap-1 px-3 mt-4">
                        {ListNavItems.map(item => (
                            <NavItem
                                key={`nav-item-${item.link}`}
                                location={location}
                                content={item.content}
                                linkTo={item.link}
                                Icon={item.icon}
                                expanded={showLabel}
                            />
                        ))}
                    </div>
                </div>

                {/* CHÂN SIDEBAR */}
                <div className="flex flex-col items-center gap-3 p-4">
                    <ThemeToggle />
                    {showLabel && (
                        <span className={clsx(mutedText, "text-xs text-center")}>
                            © 2026 {AppName}
                        </span>
                    )}
                </div>
            </aside>

            {/* NỘI DUNG CHÍNH — pt-16 khớp đúng chiều cao topbar mobile */}
            <main className="flex-1 p-6 md:p-10 pt-20 md:pt-10">
                <Outlet />
            </main>
        </div>
    );
};

const NavItem = ({ linkTo, content, location, Icon, expanded }) => {
    let isActive = false;
    if (linkTo === "/") {
        isActive = location.pathname === "/";
    } else {
        isActive = location.pathname.startsWith(linkTo);
    }

    return (
        <Link
            to={linkTo}
            className={clsx(
                animateFast, "relative flex items-center gap-3 px-3 py-2 rounded-md",
                isActive ? "bg-primary/10 text-primary font-semibold" : clsx(mutedText, "hover:text-primary")
            )}
        >
            <Icon size={22} className="shrink-0" />
            <AnimatePresence>
                {expanded && (
                    <motion.span
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.2 }}
                        className="text-base whitespace-nowrap"
                    >
                        {content}
                    </motion.span>
                )}
            </AnimatePresence>

            {isActive && (
                <motion.div
                    layoutId="sidebar-active-marker"
                    className="absolute left-0 top-0 bottom-0 w-[3px] bg-primary rounded-r-sm"
                    transition={{ type: "spring", stiffness: 550, damping: 50 }}
                />
            )}
        </Link>
    );
};

export default Layout;