  export const STATS_TABS = [
    { to: "/stats", label: "Tổng quan", end: true },
    { to: "by-area", label: "Theo khu vực" },
    { to: "timeline", label: "Theo ngày" },
    { to: "accuracy", label: "Độ chính xác" },
  ];

  export const STAT_TONE_ICON_CLASS = {
    primary: "bg-primary/15 text-primary",
    success: "bg-success/15 text-success",
    warning: "bg-warning/15 text-warning",
    danger: "bg-danger/15 text-danger",
  };

  export const STAT_TONE_VALUE_CLASS = {
    primary: "text-primary",
    success: "text-success",
    warning: "text-warning",
    danger: "text-danger",
  };

  export const ACCURACY_THRESHOLDS = {
    good: 80,
    medium: 50,
  };

  export const STAT_EMPTY_PLACEHOLDER = "—";


  // Màu cho thanh xác nhận — segment đặc (không phải badge nền nhạt)
  export const CONFIRMATION_BAR_CLASS = {
    correct: "bg-success",
    incorrect: "bg-danger",
    unconfirmed: "bg-light-muted dark:bg-dark-muted",
  };

  export const STATS_DAYS_OPTIONS = [7, 30, 90];

  export const TIMELINE_BAR_COLOR = "#059669";

  export const ACCURACY_LINE_COLORS = {
    accuracy: "#059669",
    confidence: "#F59E0B",
  };