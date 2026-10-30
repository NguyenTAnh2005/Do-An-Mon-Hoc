import clsx from "clsx";
import { ImageOff, Inbox } from "lucide-react";
import { WASTE_TYPE_LABELS } from "../../constant/dashboard";
import {
  CONFIRMATION_LABELS,
  CONFIRMATION_BADGE_CLASS,
} from "../../constant/classificationHistory";
import { animateFast, animateSlow, baseBorder, mutedText } from "../../utils/style";

const formatTime = (iso) => new Date(iso).toLocaleString("vi-VN");

export default function HistoryTable({ items }) {
  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16">
        <span className="rounded-full bg-primary/10 p-4 text-primary">
          <Inbox size={26} />
        </span>
        <p className={clsx(mutedText, "text-sm")}>Chưa có bản ghi nào</p>
      </div>
    );
  }

  return (
    <div className={clsx("overflow-x-auto", animateSlow)}>
      <table className="w-full text-sm">
        <thead>
          <tr className={clsx(mutedText, "text-left text-xs uppercase tracking-wider")}>
            <th className="px-4 py-3 font-medium">Ảnh</th>
            <th className="px-4 py-3 font-medium">Thời gian</th>
            <th className="px-4 py-3 font-medium">Khu vực</th>
            <th className="px-4 py-3 font-medium">Loại rác</th>
            <th className="px-4 py-3 font-medium">Độ tin cậy</th>
            <th className="px-4 py-3 font-medium">Xác nhận</th>
          </tr>
        </thead>
        <tbody>
          {items.map((log) => {
            const percent = Math.round(log.confidence * 100);
            return (
              <tr
                key={log.id}
                className={clsx(animateSlow, baseBorder, "border-t hover:bg-primary/5")}
              >
                <td className="px-4 py-3">
                  {log.image_url ? (
                    <img
                      src={log.image_url}
                      alt="Ảnh rác"
                      loading="lazy"
                      className="h-12 w-12 rounded-lg object-cover ring-1 ring-black/5 dark:ring-white/10"
                    />
                  ) : (
                    <div
                      className={clsx(
                        mutedText,
                        "flex h-12 w-12 items-center justify-center rounded-lg bg-black/5 dark:bg-white/5"
                      )}
                    >
                      <ImageOff size={16} />
                    </div>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">{formatTime(log.created_at)}</td>
                <td className="px-4 py-3 font-medium">{log.area_name}</td>
                <td className="px-4 py-3">{WASTE_TYPE_LABELS[log.detected_waste_type]}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium tabular-nums">{percent}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={clsx(
                      "inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium",
                      CONFIRMATION_BADGE_CLASS[log.confirmation_result]
                    )}
                  >
                    {CONFIRMATION_LABELS[log.confirmation_result]}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}