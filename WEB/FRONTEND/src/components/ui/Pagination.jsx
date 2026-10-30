import clsx from "clsx";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { animateFast, baseBorder, mutedText } from "../../utils/style";

export default function Pagination({ page, pageSize, total, onChange, disabled }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const btn = clsx(
    animateFast,
    "flex items-center gap-1.5 rounded-xl border px-4 py-2 text-base font-medium",
    "border-primary/40 text-primary",
    "hover:bg-primary hover:text-white hover:border-primary hover:shadow-md hover:shadow-primary/30",
    "disabled:opacity-40 disabled:cursor-not-allowed",
    "disabled:hover:bg-transparent disabled:hover:text-primary disabled:hover:shadow-none"
  );

  return (
    <div className="flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-6">
      {/* Cụm điều hướng — căn giữa */}
      <div className="flex items-center gap-3">
        <button
          className={btn}
          disabled={disabled || page <= 1}
          onClick={() => onChange(page - 1)}
        >
          <ChevronLeft size={18} />
          Trước
        </button>

        {/* Số trang hiện tại — nổi bật */}
        <span
          className={clsx(
            "rounded-xl bg-primary px-4 py-2 text-base font-bold text-white shadow-md shadow-primary/30 tabular-nums"
          )}
        >
          {page} <span className="font-normal opacity-80">/ {totalPages}</span>
        </span>

        <button
          className={btn}
          disabled={disabled || page >= totalPages}
          onClick={() => onChange(page + 1)}
        >
          Sau
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Ghi chú nhỏ bên dưới (mobile) / bên cạnh (desktop) */}
      <p className={clsx(mutedText, "text-sm")}>
        Trang <span className="font-semibold text-primary">{page}</span> trên {totalPages}
      </p>
    </div>
  );
}