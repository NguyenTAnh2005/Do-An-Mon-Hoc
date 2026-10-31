import manualInstance from "./config/manualConfig";

// Lấy số liệu tổng quan: tổng lượt, theo loại rác, xác nhận, độ chính xác...
export const getOverview = async () => {
  const response = await manualInstance.get("/statistics/overview");
  return response;
};

// Thống kê theo từng khu vực
export const getByArea = async () => {
  const response = await manualInstance.get("/statistics/by-area");
  return response;
};

// Số lượt phân loại theo ngày trong N ngày gần nhất
export const getTimeline = async (days = 7) => {
  const response = await manualInstance.get("/statistics/timeline", {
    params: { days },
  });
  return response;
};

// Độ chính xác + độ tin cậy trung bình theo ngày
export const getAccuracyTimeline = async (days = 7) => {
  const response = await manualInstance.get("/statistics/accuracy-timeline", {
    params: { days },
  });
  return response;
};


// Bộ chọn số ngày cho timeline + accuracy-timeline
export const STATS_DAYS_OPTIONS = [7, 30, 90];

// Màu cột timeline — = primary #059669 trong tailwind.config
export const TIMELINE_BAR_COLOR = "#059669";