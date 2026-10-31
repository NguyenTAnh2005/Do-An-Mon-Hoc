import manualInstance from "./config/manualConfig";

export const classificationLogService = {
  // Lấy danh sách bản ghi 
  getLogs: (params) => manualInstance.get("/classification-logs", { params }),

  // Lấy 1 bản ghi theo id
  getLogById: (id) => manualInstance.get(`/classification-logs/${id}`),

  // Đổi kết quả xác nhận: correct / incorrect / unconfirmed
  updateConfirmation: (id, confirmationResult) =>
    manualInstance.patch(`/classification-logs/${id}/confirmation`, {
      confirmation_result: confirmationResult,
    }),

  // Upload ảnh thủ công (gửi dạng multipart)
  uploadImage: (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return manualInstance.patch(
      `/classification-logs/${id}/image`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
  },

  // Xóa 1 bản ghi
  deleteLog: (id) => manualInstance.delete(`/classification-logs/${id}`),

  // Xóa nhiều bản ghi
  batchDelete: (ids) =>
    manualInstance.post("/classification-logs/batch-delete", { ids }),
};