import { useRef, useState } from "react";
import clsx from "clsx";
import {
  Image as ImageIcon, ImageOff, Loader2, Upload, Lock, Info, Check,
} from "lucide-react";
import { toast } from "react-toastify";
import { classificationLogService } from "../../services/classificationLog";
import { bgSurface, baseBorder, mutedText, animateFast, animateSlow } from "../../utils/style";

const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

export default function DetailImagePanel({ log, onUpdated }) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const hasImage = !!log.image_url;

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast.error("Vui lòng chọn file ảnh.");
      return;
    }
    if (file.size > MAX_IMAGE_SIZE) {
      toast.error("Ảnh vượt quá 5MB.");
      return;
    }

    setUploading(true);
    try {
      const res = await classificationLogService.uploadImage(log.id, file);
      onUpdated(res.data);
      toast.success("Đã tải ảnh lên");
    } catch (err) {
      toast.error("Tải ảnh thất bại, vui lòng thử lại.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className={clsx(
      bgSurface, baseBorder, animateSlow,
      "flex flex-col overflow-hidden rounded-xl border shadow-sm"
    )}>
      {/* Header bar */}
      <header className={clsx(baseBorder, "flex items-center justify-between border-b px-4 py-3")}>
        <div className="flex items-center gap-2">
          <ImageIcon size={16} className="text-primary" />
          <span className="text-sm font-semibold">Ảnh phân loại</span>
        </div>
        {hasImage && (
          <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
            <Check size={11} />
            Đã gán
          </span>
        )}
      </header>

      {/* Body */}
      <div className="flex flex-1 items-center justify-center p-4">
        {hasImage ? (
          <img
            src={log.image_url}
            alt="Ảnh rác"
            className="max-h-[480px] max-w-full rounded-lg object-contain"
          />
        ) : (
          <div className={clsx(mutedText, "flex min-h-[300px] flex-col items-center justify-center gap-3 p-6 text-center")}>
            <span className="rounded-full bg-primary/10 p-4 text-primary">
              <ImageOff size={28} />
            </span>
            <p className="text-sm">Chưa có ảnh cho bản ghi này</p>

            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
            <button
              onClick={() => inputRef.current.click()}
              disabled={uploading}
              className={clsx(
                animateFast,
                "flex cursor-pointer items-center gap-2 rounded-lg border border-primary/40 px-3 py-1.5 text-sm font-medium text-primary",
                "hover:bg-primary hover:text-white",
                "disabled:cursor-not-allowed disabled:opacity-40"
              )}
            >
              {uploading ? <Loader2 size={15} className="animate-spin" /> : <Upload size={15} />}
              {uploading ? "Đang tải lên..." : "Tải ảnh lên"}
            </button>
          </div>
        )}
      </div>

      {/* Footer note */}
      <footer className={clsx(baseBorder, "flex items-start gap-2 border-t px-4 py-3")}>
        {hasImage ? (
          <>
            <Lock size={14} className="mt-0.5 shrink-0 text-warning" />
            <p className={clsx(mutedText, "text-xs leading-relaxed")}>
              Ảnh đã được gán và <strong className="font-semibold">không thể thay đổi</strong>.
            </p>
          </>
        ) : (
          <>
            <Info size={14} className="mt-0.5 shrink-0 text-primary" />
            <p className={clsx(mutedText, "text-xs leading-relaxed")}>
              Ảnh chỉ có thể tải lên <strong className="font-semibold">một lần</strong>. Vui lòng kiểm tra kỹ trước khi tải lên.
            </p>
          </>
        )}
      </footer>
    </section>
  );
}