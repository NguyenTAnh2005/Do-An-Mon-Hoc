import { useEffect, useRef } from "react";
import clsx from "clsx";
import { ImageOff, Inbox } from "lucide-react";
import {
  WASTE_TYPE_LABELS,
  CONFIRMATION_LABELS,
  CONFIRMATION_BADGE_CLASS,
} from "../../constant/index";
import { animateSlow, baseBorder, mutedText } from "../../utils/style";
import { useNavigate } from "react-router-dom";

const formatTime = (iso) => new Date(iso).toLocaleString("vi-VN");

export default function HistoryTable({ items, selectedIds, onToggleRow, onToggleAll }) {
  const navigate = useNavigate();
  const headerCheckboxRef = useRef(null);

  const allSelected = items.length > 0 && items.every((it) => selectedIds.has(it.id));
  const someSelected = items.some((it) => selectedIds.has(it.id)) && !allSelected;

  // Set thuộc tính indeterminate (chỉ set được qua DOM, không có prop React)
  useEffect(() => {
    if (headerCheckboxRef.current) {
      headerCheckboxRef.current.indeterminate = someSelected;
    }
  }, [someSelected]);

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

  const handleToggleAll = (e) => {
    e.stopPropagation();
    if (allSelected) onToggleAll([]);
    else onToggleAll(items.map((it) => it.id));
  };

  return (
    <div className={clsx("overflow-x-auto", animateSlow)}>
      <table className="w-full text-sm">
        <thead>
          <tr className={clsx(mutedText, "text-left text-xs uppercase tracking-wider")}>
            <th className="w-10 px-4 py-3">
              <input
                ref={headerCheckboxRef}
                type="checkbox"
                checked={allSelected}
                onChange={handleToggleAll}
                className="h-4 w-4 cursor-pointer accent-danger"
                aria-label="Chọn tất cả bản ghi trên trang"
              />
            </th>
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
            const isSelected = selectedIds.has(log.id);

            return (
              <tr
                key={log.id}
                onClick={() => navigate(`/history/${log.id}`)}
                className={clsx(
                  animateSlow,
                  baseBorder,
                  "cursor-pointer border-t hover:bg-primary/5",
                  isSelected && "bg-danger/5 hover:bg-danger/10"
                )}
              >
                <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onToggleRow(log.id)}
                    className="h-4 w-4 cursor-pointer accent-danger"
                    aria-label="Chọn bản ghi"
                  />
                </td>
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