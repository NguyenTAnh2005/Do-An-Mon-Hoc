// src/constant/index.js
import { LayoutDashboard, History as HistoryIcon, ChartColumn } from "lucide-react";

// ============ NAVIGATION ============
export const AppName = "VTA-trash";
export const AppFullName = "Hệ thống Phân loại Rác Thông minh";

export const ListNavItems = [
    { link: "/", content: "Dashboard", icon: LayoutDashboard },
    { link: "/history", content: "Lịch sử", icon: HistoryIcon },
    { link: "/stats", content: "Thống kê", icon: ChartColumn },
];

// ============ WASTE TYPE ============
// Nhãn chuẩn dùng chung toàn app — KHÔNG khai báo lại ở file khác
export const WASTE_TYPE_LABELS = {
    recyclable: "Tái chế",
    organic: "Hữu cơ",
    inorganic: "Vô cơ",
};

// Màu cho recharts — lấy hex từ tailwind.config (semantic, không đổi theo theme)
export const WASTE_TYPE_COLORS = {
    recyclable: "#22C55E", // success
    organic: "#F59E0B",    // warning
    inorganic: "#059669",  // primary
};

// ============ FILL LEVEL ============
export const FILL_WARNING_PERCENT = 60;
export const FILL_DANGER_PERCENT = 85;

export const getFillColorClass = (percent) => {
    if (percent >= FILL_DANGER_PERCENT) return "bg-danger";
    if (percent >= FILL_WARNING_PERCENT) return "bg-warning";
    return "bg-success";
};

export const getFillLevelLabel = (percent) => {
    if (percent >= FILL_DANGER_PERCENT) return "Đầy";
    if (percent >= FILL_WARNING_PERCENT) return "Sắp đầy";
    return "Bình thường";
};

// ============ CONFIRMATION ============
export const CONFIRMATION_LABELS = {
    unconfirmed: "Chưa xác nhận",
    correct: "Đúng",
    incorrect: "Sai",
};

export const CONFIRMATION_BADGE_CLASS = {
    unconfirmed: "bg-gray-500/15 text-gray-500",
    correct: "bg-success/15 text-success",
    incorrect: "bg-danger/15 text-danger",
};