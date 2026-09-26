// src/pages/ClassificationHistory.jsx
import clsx from "clsx";
import { sectionTitle, mutedText } from "../utils/style";

const ClassificationHistory = () => {
    return (
        <div className="flex flex-col items-start gap-2">
            <h1 className={sectionTitle}>Lịch sử phân loại</h1>
            <p className={clsx(mutedText, "text-base")}>
                Danh sách log kèm ảnh, filter, xác nhận đúng/sai thủ công, batch delete cho dòng thiếu ảnh
            </p>
        </div>
    );
};

export default ClassificationHistory;