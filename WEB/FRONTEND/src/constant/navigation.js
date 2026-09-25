import { LayoutDashboard, History as HistoryIcon, ChartColumn } from "lucide-react";

// Tên hệ thống dùng chung cho Sidebar + trang Đăng nhập
export const AppName = "VTA-trash";
export const AppFullName = "Hệ thống Phân loại Rác Thông minh";

// Các nav điều hướng — mỗi item có icon riêng để hiển thị ở Sidebar
export const ListNavItems = [
    { link: "/", content: "Dashboard", icon: LayoutDashboard },
    { link: "/history", content: "Lịch sử", icon: HistoryIcon },
    { link: "/stats", content: "Thống kê", icon: ChartColumn },
];