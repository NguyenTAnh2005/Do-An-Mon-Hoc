import clsx from "clsx";
import {
    bgSurface, baseBorder, mutedText, cardTitle, metaLabel, animateSlow, hoverShadow
} from "../../utils/style";
import {
    WASTE_TYPE_LABELS, getFillColorClass, getFillLevelLabel
} from "../../constant/dashboard";

export const TrashBinCard = ({ wasteType, percent }) => {
    // Tên tiếng Việt, loại lạ chưa có trong bảng thì hiện tên gốc
    const label = WASTE_TYPE_LABELS[wasteType] || wasteType;

    // Chưa có số liệu thì coi như 0% để thanh không bị lỗi
    let safePercent = percent;
    if (safePercent === null || safePercent === undefined) {
        safePercent = 0;
    }

    const colorClass = getFillColorClass(safePercent);
    const levelLabel = getFillLevelLabel(safePercent);

    return (
        <div className={clsx(
            bgSurface, baseBorder, animateSlow, hoverShadow,
            "border-2 rounded-lg p-4 flex flex-col gap-3"
        )}>
            <div className="flex items-center justify-between">
                <span className={cardTitle}>{label}</span>
                <span className={clsx(mutedText)}>{levelLabel}</span>
            </div>

            <span className="text-3xl font-bold">{safePercent}%</span>

            {/* Nền của thanh */}
            <div className={clsx(
                animateSlow,
                "h-3 w-full rounded-full bg-light-text/10 dark:bg-dark-text/10 overflow-hidden"
            )}>
                {/* Phần đã đầy: chiều rộng và màu đổi theo % */}
                <div
                    className={clsx(colorClass, animateSlow, "h-full rounded-full")}
                    style={{ width: `${safePercent}%` }}
                />
            </div>
        </div>
    );
};