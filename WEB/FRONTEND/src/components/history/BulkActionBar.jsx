import clsx from "clsx";
import { Trash2, X } from "lucide-react";
import { animateFast, animateSlow } from "../../utils/style";

export default function BulkActionBar({ count, onClear, onDelete, disabled = false }) {
  if (count === 0) return null;

  return (
    <div
      className={clsx(
        animateSlow,
        "flex flex-wrap items-center justify-between gap-3 rounded-lg border px-3 py-2",
        "border-danger/30 bg-danger/5 dark:bg-danger/10"
      )}
    >
      <div className="flex items-center gap-2 text-sm">
        <span className="inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-danger px-2 text-xs font-bold text-white">
          {count}
        </span>
        <span className="font-medium text-danger">bản ghi đã chọn</span>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onClear}
          disabled={disabled}
          className={clsx(
            animateFast,
            "flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium cursor-pointer",
            "border-danger/30 text-danger hover:bg-danger/10",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <X size={14} /> Bỏ chọn
        </button>
        <button
          onClick={onDelete}
          disabled={disabled}
          className={clsx(
            animateFast,
            "flex items-center gap-1.5 rounded-lg bg-danger px-2.5 py-1.5 text-xs font-medium text-white cursor-pointer",
            "hover:bg-danger/90",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <Trash2 size={14} /> Xóa {count} mục
        </button>
      </div>
    </div>
  );
}