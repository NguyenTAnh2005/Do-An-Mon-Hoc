// src/components/ui/ConfirmBar.jsx
import clsx from "clsx";

import { bgSurface, baseBorder, cardTitle, mutedText } from "../../utils/style";
import { CONFIRMATION_LABELS } from "../../constant/classificationHistory";
import { CONFIRMATION_BAR_CLASS } from "../../constant/statistics";

export const ConfirmBar = ({ correct, incorrect, unconfirmed }) => {
  const total = correct + incorrect + unconfirmed;

  if (total === 0) {
    return (
      <section
        className={clsx(bgSurface, baseBorder, "rounded-xl border p-4 shadow-sm")}
      >
        <h3 className={clsx(cardTitle, "mb-3")}>Trạng thái xác nhận</h3>
        <p className={clsx(mutedText, "py-8 text-center text-sm")}>
          Chưa có dữ liệu
        </p>
      </section>
    );
  }

  // 3 đoạn — dùng chung để render thanh + legend
  const segments = [
    {
      key: "correct",
      label: CONFIRMATION_LABELS.correct,
      value: correct,
      colorClass: CONFIRMATION_BAR_CLASS.correct,
    },
    {
      key: "incorrect",
      label: CONFIRMATION_LABELS.incorrect,
      value: incorrect,
      colorClass: CONFIRMATION_BAR_CLASS.incorrect,
    },
    {
      key: "unconfirmed",
      label: CONFIRMATION_LABELS.unconfirmed,
      value: unconfirmed,
      colorClass: CONFIRMATION_BAR_CLASS.unconfirmed,
    },
  ];

  return (
    <section
      className={clsx(bgSurface, baseBorder, "rounded-xl border p-4 shadow-sm")}
    >
      <h3 className={clsx(cardTitle, "mb-3")}>Trạng thái xác nhận</h3>

      {/* Thanh ngang chia 3 đoạn */}
      <div className="flex h-4 overflow-hidden rounded-full">
        {segments.map((seg) => {
          if (seg.value === 0) {
            return null;
          }
          const widthPercent = (seg.value / total) * 100;
          return (
            <div
              key={seg.key}
              className={seg.colorClass}
              style={{ width: `${widthPercent}%` }}
              title={`${seg.label}: ${seg.value}`}
            />
          );
        })}
      </div>

      {/* Legend dưới thanh */}
      <ul className="mt-4 space-y-2">
        {segments.map((seg) => {
          const percent = Math.round((seg.value / total) * 1000) / 10;
          return (
            <li key={seg.key} className="flex items-center gap-2 text-sm">
              <span
                className={clsx("inline-block h-3 w-3 rounded-sm", seg.colorClass)}
              />
              <span className="flex-1">{seg.label}</span>
              <span className={mutedText}>
                {seg.value} · {percent}%
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
};