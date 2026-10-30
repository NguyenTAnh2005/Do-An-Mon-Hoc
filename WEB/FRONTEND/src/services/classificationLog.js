import manualInstance from "./config/manualConfig"; // sửa dòng này giống dashboard.js

export const classificationLogService = {
  getLogs: (params) => manualInstance.get("/classification-logs", { params }),
};