// src/pages/Statistics.jsx
import clsx from "clsx";
import { sectionTitle, mutedText } from "../utils/style";

const Statistics = () => {
    return (
        <div className="flex flex-col items-start gap-2">
            <h1 className={sectionTitle}>Thống kê</h1>
            <p className={clsx(mutedText, "text-base")}>
                Thống kê theo loại rác / khu vực / thời gian, và độ chính xác model theo ngày
            </p>
        </div>
    );
};

export default Statistics;