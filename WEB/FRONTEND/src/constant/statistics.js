// Tabs trang /stats — index route cần `end: true` để không sáng ở tab con
export const STATS_TABS = [
  { to: "/stats", label: "Tổng quan", end: true },
  { to: "by-area", label: "Theo khu vực" },
  { to: "timeline", label: "Theo ngày" },
  { to: "accuracy", label: "Độ chính xác" },
];

// Class badge icon theo tone — chỉ dùng màu có trong tailwind.config.js
export const STAT_TONE_ICON_CLASS = {
  primary: "bg-primary/15 text-primary",
  success: "bg-success/15 text-success",
  warning: "bg-warning/15 text-warning",
  danger: "bg-danger/15 text-danger",
};

// Class số liệu theo tone
export const STAT_TONE_VALUE_CLASS = {
  primary: "text-primary",
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger",
};

// Ngưỡng đánh giá độ chính xác (%)
export const ACCURACY_THRESHOLDS = {
  good: 80,   // >= 80  → success
  medium: 50, // >= 50  → warning, còn lại → danger
};

// Placeholder khi giá trị null/undefined
export const STAT_EMPTY_PLACEHOLDER = "—";

// Nhãn tiếng Việt cho 3 loại rác — dùng chung cho mọi biểu đồ
// (Nếu bên History đã có WASTE_TYPE_LABELS/WASTE_TYPE_COLORS thì gộp lại 1 file chung)
export const WASTE_TYPE_LABELS = {
  recyclable: "Rác tái chế",
  organic: "Rác hữu cơ",
  inorganic: "Rác vô cơ",
};

// Màu cho recharts — lấy hex từ tailwind.config (các màu semantic không đổi theo theme)
export const WASTE_TYPE_COLORS = {
  recyclable: "#22C55E", // success
  organic: "#F59E0B",    // warning
  inorganic: "#059669",  // primary
};

// Màu cho thanh xác nhận — segment đặc (không phải badge nền nhạt)
export const CONFIRMATION_BAR_CLASS = {
  correct: "bg-success",
  incorrect: "bg-danger",
  unconfirmed: "bg-light-muted dark:bg-dark-muted",
};

// Bộ chọn số ngày cho timeline + accuracy-timeline
export const STATS_DAYS_OPTIONS = [7, 30, 90];

// Màu cột timeline — = primary #059669 trong tailwind.config
export const TIMELINE_BAR_COLOR = "#059669";

export const ACCURACY_LINE_COLORS = {
  accuracy: "#059669",   // primary  — độ chính xác (%)
  confidence: "#F59E0B", // warning  — độ tin cậy (×100)
};