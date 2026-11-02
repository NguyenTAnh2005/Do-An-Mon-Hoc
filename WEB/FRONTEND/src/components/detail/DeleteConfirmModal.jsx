import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import clsx from "clsx";
import { AlertTriangle, Loader2, X } from "lucide-react";
import { bgSurface, baseBorder, mutedText, animateFast } from "../../utils/style";

export default function DeleteConfirmModal({
  open,
  onClose,
  onConfirm,
  loading = false,
  title = "Xóa bản ghi này?",
  description = "Hành động này không thể hoàn tác.",
}) {
  // Escape để đóng (trừ khi đang xóa)
  useEffect(() => {
    if (!open) return;
    const handler = (e) => e.key === "Escape" && !loading && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, loading, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={() => !loading && onClose()}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 12 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            onClick={(e) => e.stopPropagation()}
            className={clsx(
              bgSurface, baseBorder,
              "w-full max-w-md overflow-hidden rounded-2xl border shadow-2xl"
            )}
          >
            <div className="flex items-start gap-3 p-5">
              <span className="shrink-0 rounded-full bg-danger/10 p-2.5 text-danger">
                <AlertTriangle size={20} />
              </span>
              <div className="min-w-0 flex-1">
                <h2 className="text-lg font-bold">{title}</h2>
                <p className={clsx(mutedText, "mt-1 text-sm")}>{description}</p>
              </div>
              <button
                onClick={onClose}
                disabled={loading}
                aria-label="Đóng"
                className={clsx(
                  animateFast, mutedText,
                  "shrink-0 cursor-pointer rounded-lg p-1 hover:text-primary disabled:opacity-40"
                )}
              >
                <X size={18} />
              </button>
            </div>

            <div className={clsx(baseBorder, "flex justify-end gap-2 border-t px-5 py-3")}>
              <button
                onClick={onClose}
                disabled={loading}
                className={clsx(
                  animateFast, baseBorder,
                  "cursor-pointer rounded-lg border px-3 py-1.5 text-sm hover:bg-primary/5",
                  "disabled:cursor-not-allowed disabled:opacity-40"
                )}
              >
                Hủy
              </button>
              <button
                onClick={onConfirm}
                disabled={loading}
                className={clsx(
                  animateFast,
                  "flex cursor-pointer items-center gap-2 rounded-lg bg-danger px-3 py-1.5 text-sm font-medium text-white",
                  "hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
                )}
              >
                {loading && <Loader2 size={14} className="animate-spin" />}
                {loading ? "Đang xóa..." : "Xóa"}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}