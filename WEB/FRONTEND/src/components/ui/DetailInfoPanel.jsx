import { useState } from "react";
import clsx from "clsx";
import { Check, ClipboardList, HelpCircle, X } from "lucide-react";
import { toast } from "react-toastify";
import { classificationLogService } from "../../services/classificationLog";
import { WASTE_TYPE_LABELS } from "../../constant/dashboard";
import { CONFIRMATION_LABELS } from "../../constant/classificationHistory";
import { bgSurface, baseBorder, mutedText, animateFast, animateSlow } from "../../utils/style";

const formatTime = (iso) => new Date(iso).toLocaleString("vi-VN");

// Semantic tone + icon cho từng trạng thái xác nhận
const CONFIRMATION_META = {
  unconfirmed: {
    Icon: HelpCircle,
    active: "border-primary bg-primary text-white shadow-sm shadow-primary/20",
    idle: "border-primary/40 text-primary hover:border-primary hover:bg-primary/5",
  },
  correct: {
    Icon: Check,
    active: "border-success bg-success text-white shadow-sm shadow-success/20",
    idle: "border-success/40 text-success hover:border-success hover:bg-success/5",
  },
  incorrect: {
    Icon: X,
    active: "border-danger bg-danger text-white shadow-sm shadow-danger/20",
    idle: "border-danger/40 text-danger hover:border-danger hover:bg-danger/5",
  },
};

// Màu thanh confidence theo mức — thấp = cảnh báo (AI không chắc)
const getConfidenceBarClass = (pct) => {
  if (pct >= 80) return "bg-success";
  if (pct >= 60) return "bg-warning";
  return "bg-danger";
};

function InfoRow({ label, children }) {
  return (
    <div className={clsx(baseBorder, "flex items-center justify-between gap-4 border-b py-3 last:border-b-0")}>
      <span className={clsx(mutedText, "text-sm")}>{label}</span>
      <div className="text-sm font-medium">{children}</div>
    </div>
  );
}

export default function DetailInfoPanel({ log, onUpdated }) {
  const [updating, setUpdating] = useState(false);
  const percent = Math.round(log.confidence * 100);

  const handleConfirm = async (value) => {
    if (value === log.confirmation_result) return;

    setUpdating(true);
    try {
      const res = await classificationLogService.updateConfirmation(log.id, value);
      onUpdated(res.data);
      toast.success("Đã cập nhật kết quả xác nhận");
    } catch (err) {
      toast.error("Cập nhật thất bại, vui lòng thử lại.");
    } finally {
      setUpdating(false);
    }
  };

  return (
    <section className={clsx(
      bgSurface, baseBorder, animateSlow,
      "flex flex-col overflow-hidden rounded-xl border shadow-sm"
    )}>
      {/* Header bar */}
      <header className={clsx(baseBorder, "flex items-center gap-2 border-b px-4 py-3")}>
        <ClipboardList size={16} className="text-primary" />
        <span className="text-sm font-semibold">Thông tin phân loại</span>
      </header>

      {/* Info rows */}
      <div className="px-4">
        <InfoRow label="Thời gian">{formatTime(log.created_at)}</InfoRow>
        <InfoRow label="Khu vực">{log.area_name}</InfoRow>
        <InfoRow label="Loại rác">{WASTE_TYPE_LABELS[log.detected_waste_type]}</InfoRow>
        <InfoRow label="Độ tin cậy">
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-24 overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
              <div
                className={clsx("h-full rounded-full transition-all", getConfidenceBarClass(percent))}
                style={{ width: `${percent}%` }}
              />
            </div>
            <span className="tabular-nums">{percent}%</span>
          </div>
        </InfoRow>
      </div>

      {/* Confirmation — radio-card style, tự làm nổi bật trạng thái hiện tại */}
      <div className={clsx(baseBorder, "mt-auto border-t px-4 py-4")}>
        <p className={clsx(mutedText, "mb-3 text-sm font-medium")}>Kết quả xác nhận</p>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {Object.entries(CONFIRMATION_LABELS).map(([value, label]) => {
            const { Icon, active, idle } = CONFIRMATION_META[value];
            const isCurrent = value === log.confirmation_result;
            return (
              <button
                key={value}
                onClick={() => handleConfirm(value)}
                disabled={updating || isCurrent}
                className={clsx(
                  animateFast,
                  "flex flex-col items-center justify-center gap-1.5 rounded-xl border-2 p-3 text-sm font-medium",
                  "cursor-pointer",
                  isCurrent ? active : idle,
                  "disabled:cursor-not-allowed",
                  !isCurrent && "disabled:opacity-40"
                )}
              >
                <Icon size={18} />
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}