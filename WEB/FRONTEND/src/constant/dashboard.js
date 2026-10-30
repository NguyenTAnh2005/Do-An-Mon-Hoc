// Bảng map tên loại rác (đúng như database và API) sang tiếng Việt để hiển thị
export const WASTE_TYPE_LABELS = {
    recyclable: "Tái chế",
    organic: "Hữu cơ",
    inorganic: "Vô cơ",
};

// Ngưỡng % đầy: từ WARNING là "sắp đầy", từ DANGER là "đầy"
export const FILL_WARNING_PERCENT = 60;
export const FILL_DANGER_PERCENT = 85;

// Trả về class màu thanh, dùng token màu trong tailwind.config.js
// (viết nguyên tên class đầy đủ để Tailwind quét được)
export const getFillColorClass = (percent) => {
    if (percent >= FILL_DANGER_PERCENT) {
        return "bg-danger";
    }
    if (percent >= FILL_WARNING_PERCENT) {
        return "bg-warning";
    }
    return "bg-success";
};

// Trả về chữ mô tả mức đầy, đi cùng màu ở trên
export const getFillLevelLabel = (percent) => {
    if (percent >= FILL_DANGER_PERCENT) {
        return "Đầy";
    }
    if (percent >= FILL_WARNING_PERCENT) {
        return "Sắp đầy";
    }
    return "Bình thường";
};