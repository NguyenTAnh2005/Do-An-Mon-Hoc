import { useEffect, useRef } from "react";
import clsx from "clsx";
import { AlertTriangle, Loader2, X } from "lucide-react";
import { animateFast, animateSlow, baseBorder, bgSurface, mutedText } from "../../utils/style";

const toneMap = {
  danger: {
    iconWrap: "bg-danger/10 text-danger",
    confirmBtn: "bg-danger hover:bg-danger/90",
  },
  primary: {
    iconWrap: "bg-primary/10 text-primary",
    confirmBtn: "bg-primary hover:bg-primary/90",
  },
};

export default function ConfirmDialog({
  open,
  title = "Xác nhận",
  description,
  confirmText = "Xác nhận",
  cancelText = "Hủy",
  tone = "danger",
  loading = false,
  onConfirm,
  onCancel,
}) {
  const cancelRef = useRef(null);

  // ESC để đóng (không cho đóng khi đang loading)
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape" && !loading) onCancel?.();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, loading, onCancel]);

  // Focus nút Hủy khi mở
  useEffect(() => {
    if (open) cancelRef.current?.focus();
  }, [open]);

  // Khóa scroll body khi mở
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  if (!open) return null;

  const t = toneMap[tone] ?? toneMap.danger;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm"
      onClick={() => !loading && onCancel?.()}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
    >
      <div
        className={clsx(
          animateSlow,
          bgSurface,
          baseBorder,
          "w-full max-w-md rounded-xl border shadow-xl"
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-3 p-5">
          <span className={clsx("rounded-full p-2", t.iconWrap)}>
            <AlertTriangle size={22} />
          </span>
          <div className="flex-1">
            <h3 id="confirm-dialog-title" className="text-base font-semibold">
              {title}
            </h3>
            {description && (
              <p className={clsx(mutedText, "mt-1 text-sm")}>{description}</p>
            )}
          </div>
          <button
            onClick={onCancel}
            disabled={loading}
            className="rounded-md p-1 opacity-60 hover:opacity-100 disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
            aria-label="Đóng"
          >
            <X size={18} />
          </button>
        </div>

        <div className={clsx(baseBorder, "flex items-center justify-end gap-2 border-t px-5 py-3")}>
          <button
            ref={cancelRef}
            onClick={onCancel}
            disabled={loading}
            className={clsx(
              animateFast,
              baseBorder,
              "rounded-lg border px-3 py-2 text-sm cursor-pointer",
              "hover:bg-black/5 dark:hover:bg-white/5",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className={clsx(
              animateFast,
              "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-white cursor-pointer",
              t.confirmBtn,
              "disabled:opacity-60 disabled:cursor-not-allowed"
            )}
          >
            {loading && <Loader2 size={14} className="animate-spin" />}
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}