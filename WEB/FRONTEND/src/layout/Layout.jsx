// src/layout/Layout.jsx
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useState, useEffect } from "react";
import clsx from "clsx";
import {
    Menu, X, Recycle, LogOut, Loader2, ChevronLeft, ChevronRight
} from "lucide-react";
import { toast } from "react-toastify";

import { ListNavItems, AppName } from "../constant/navigation";
import ThemeToggle from "../components/ui/ThemeToggle";
import { authService } from "../services/auth";
import { useAuth } from "../hooks/useAuth";
import {
    baseTextBg, animateSlow, animateBase, animateFast,
    bgSurface, baseBorder, mutedText
} from "../utils/style";

export const Layout = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { logout } = useAuth();

    // Desktop: mở/thu gọn sidebar — luôn mặc định mở khi load lại trang
    const [expanded, setExpanded] = useState(true);
    // Mobile: sidebar dạng drawer, mặc định đóng
    const [mobileOpen, setMobileOpen] = useState(false);

    // Thông tin tài khoản hiện tại — KHÔNG tích hợp vào useAuth, tự gọi getMe ở đây
    const [account, setAccount] = useState(null);
    const [loadingAccount, setLoadingAccount] = useState(true);

    // Tự động cuộn lên đầu trang + đóng drawer mobile khi đổi route
    useEffect(() => {
        window.scroll(0, 0);
        setMobileOpen(false);
    }, [location]);

    // Gọi getMe 1 lần khi Layout mount
    useEffect(() => {
        let isMounted = true;
        const fetchMe = async () => {
            try {
                const res = await authService.getMe();
                if (isMounted) setAccount(res.data);
            } catch (error) {
                console.error("[Layout]: getMe thất bại:", error);
            } finally {
                if (isMounted) setLoadingAccount(false);
            }
        };
        fetchMe();
        return () => { isMounted = false; };
    }, []);

    const toggleExpanded = () => setExpanded(prev => !prev);
    const toggleMobile = () => setMobileOpen(prev => !prev);

    const handleLogout = async () => {
        try {
            await logout();
            toast.success("🎉 Đăng xuất thành công!");
            navigate("/log-in");
        } catch (error) {
            console.error("[Layout]: logout thất bại:", error);
            toast.error("Đăng xuất thất bại, vui lòng thử lại.");
        }
    };

    const showLabel = expanded || mobileOpen;

    return (
        <div className={clsx(baseTextBg, "flex min-h-screen")}>
            {/* TOP BAR — CHỈ HIỆN TRÊN MOBILE */}
            <div className={clsx(
                bgSurface, baseBorder, animateSlow,
                "md:hidden border-b-2 flex items-center justify-between px-4 h-16",
                "fixed top-0 left-0 right-0 z-50"
            )}>
                <Link to="/" className="flex items-center gap-2">
                    <span className="bg-primary text-white p-2 rounded-lg shadow-sm shadow-primary/30">
                        <Recycle size={20} />
                    </span>
                    <span className="text-lg font-bold">{AppName}</span>
                </Link>
                <div className="flex items-center gap-1">
                    <ThemeToggle />
                    <button
                        aria-label={mobileOpen ? "Đóng menu" : "Mở menu"}
                        onClick={toggleMobile}
                        className={clsx(
                            animateFast, mutedText,
                            "p-2 rounded-md hover:text-primary hover:bg-primary/10 cursor-pointer",
                            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                        )}
                    >
                        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>
            </div>

            {/* BACKDROP — CHỈ HIỆN KHI DRAWER MOBILE MỞ */}
            <AnimatePresence>
                {mobileOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        onClick={() => setMobileOpen(false)}
                        className="md:hidden fixed top-16 inset-x-0 bottom-0 bg-black/40 backdrop-blur-sm z-30"
                    />
                )}
            </AnimatePresence>

            {/* SIDEBAR */}
            <aside
                className={clsx(
                    bgSurface, baseBorder, animateBase,
                    "border-r-2 flex flex-col justify-between shrink-0 z-40",
                    "md:sticky md:top-0 md:h-screen md:translate-x-0",
                    expanded ? "md:w-64" : "md:w-20",
                    "fixed top-16 left-0 h-[calc(100vh-4rem)] w-64",
                    mobileOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                {/* TOGGLE — FLOATING PILL, DESKTOP ONLY */}
                <button
                    aria-label={expanded ? "Thu gọn sidebar" : "Mở rộng sidebar"}
                    onClick={toggleExpanded}
                    className={clsx(
                        "hidden md:flex absolute -right-3 top-5 z-50",
                        animateFast,
                        "h-7 w-7 items-center justify-center rounded-full border-2",
                        baseBorder, bgSurface,
                        "text-light-muted dark:text-dark-muted",
                        "hover:text-primary hover:border-primary cursor-pointer",
                        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                    )}
                >
                    {expanded ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
                </button>

                <div className="overflow-hidden">
                    {/* BRAND — ẨN TRÊN MOBILE VÌ ĐÃ CÓ Ở TOP BAR */}
                    <div className="hidden md:flex items-center p-4">
                        <Link to="/" className="flex items-center gap-2 overflow-hidden">
                            <span className="shrink-0 bg-primary text-white p-2 rounded-lg shadow-md shadow-primary/30">
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

                    {/* NAV ITEMS */}
                    <nav
                        aria-label="Điều hướng chính"
                        className="flex flex-col gap-1 px-3 mt-4"
                    >
                        {expanded && (
                            <span className={clsx(
                                mutedText,
                                "hidden md:block px-3 mb-1 text-xs font-semibold uppercase tracking-wider"
                            )}>
                                Menu
                            </span>
                        )}
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
                    </nav>
                </div>

                {/* CHÂN SIDEBAR — User info -> Logout -> Theme toggle -> Copyright */}
                <div className={clsx(baseBorder, "border-t-2 flex flex-col gap-3 p-4 overflow-hidden")}>
                    {/* USER INFO CARD */}
                    {loadingAccount ? (
                        <div className={clsx(mutedText, "flex items-center gap-3 px-1")}>
                            <Loader2 size={18} className="animate-spin shrink-0" />
                            {showLabel && <span className="text-xs">Đang tải tài khoản...</span>}
                        </div>
                    ) : account && (
                        <div className={clsx(
                            animateSlow, "flex items-center gap-3 rounded-lg bg-primary/5 overflow-hidden",
                            showLabel ? "p-2" : "justify-center p-1.5"
                        )}>
                            <div className="shrink-0 h-9 w-9 rounded-full bg-primary/15 text-primary flex items-center justify-center font-semibold uppercase">
                                {account.username?.charAt(0) || "?"}
                            </div>
                            <AnimatePresence>
                                {showLabel && (
                                    <motion.div
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -10 }}
                                        transition={{ duration: 0.2 }}
                                        className="overflow-hidden min-w-0"
                                    >
                                        <p className="text-sm font-semibold truncate">{account.username}</p>
                                        <p className={clsx(mutedText, "text-xs truncate")}>{account.email}</p>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    )}

                    {/* LOGOUT */}
                    <button
                        aria-label="Đăng xuất"
                        onClick={handleLogout}
                        title={!showLabel ? "Đăng xuất" : undefined}
                        className={clsx(
                            animateFast,
                            "flex items-center gap-2 rounded-md border-2 border-red-500/40 px-3 py-2 text-red-500",
                            "hover:bg-red-500 hover:text-white hover:border-red-500 cursor-pointer",
                            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500",
                            showLabel ? "justify-start" : "justify-center"
                        )}
                    >
                        <LogOut size={18} className="shrink-0" />
                        {showLabel && <span className="text-sm font-medium">Đăng xuất</span>}
                    </button>

                    {/* THEME TOGGLE */}
                    <div className="flex items-center justify-center">
                        <ThemeToggle />
                    </div>

                    {showLabel && (
                        <span className={clsx(mutedText, "text-xs text-center")}>
                            © 2026 {AppName}
                        </span>
                    )}
                </div>
            </aside>

            {/* NỘI DUNG CHÍNH */}
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
            title={!expanded ? content : undefined}
            aria-current={isActive ? "page" : undefined}
            className={clsx(
                animateFast, "relative flex items-center gap-3 px-3 py-2 rounded-md",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary",
                isActive
                    ? "bg-primary/10 text-primary font-semibold"
                    : clsx(mutedText, "hover:bg-primary/5 hover:text-primary")
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