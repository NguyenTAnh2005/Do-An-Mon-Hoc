import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import clsx from "clsx";
import {
  AlertCircle, ArrowLeft, Check, Copy, FileText, Loader2, Trash2,
} from "lucide-react";
import { toast } from "react-toastify";
import { classificationLogService } from "../services/classificationLog";
import DetailImagePanel from "../components/detail/DetailImagePanel";
import DetailInfoPanel from "../components/detail/DetailInfoPanel";
import DeleteConfirmModal from "../components/detail/DeleteConfirmModal";
import {
  animateFast, animateSlow, bodyLarge, mutedText, sectionTitle,
} from "../utils/style";

export default function ClassificationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [log, setLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const fetchLog = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await classificationLogService.getLogById(id);
        if (!cancelled) setLog(res.data);
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchLog();
    return () => { cancelled = true; };
  }, [id]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await classificationLogService.deleteLog(id);
      toast.success("Đã xóa bản ghi");
      navigate("/history");
    } catch (err) {
      toast.error("Xóa thất bại, vui lòng thử lại.");
      setShowConfirm(false);
      setDeleting(false);
    }
  };

  const handleCopyId = async () => {
    if (!log?.log_id) return;
    try {
      await navigator.clipboard.writeText(String(log.log_id));
      setCopied(true);
      toast.success("Đã sao chép Log ID");
      setTimeout(() => setCopied(false), 1500);
    } catch {
      toast.error("Không thể sao chép Log ID");
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-20">
        <Loader2 size={34} className="animate-spin text-primary" />
        <p className={clsx(mutedText, "text-sm")}>Đang tải dữ liệu...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-20">
        <span className="rounded-full bg-danger/10 p-3 text-danger">
          <AlertCircle size={30} />
        </span>
        <p className="text-sm text-danger">Lỗi: {String(error.message || error)}</p>
        <Link to="/history" className="text-sm text-primary hover:underline">
          Quay lại lịch sử
        </Link>
      </div>
    );
  }

  return (
    <div className={clsx("space-y-5", animateSlow)}>
      {/* Back button — pill style, hover đổ nền primary + mũi tên trượt nhẹ */}
      <Link
        to="/history"
        className={clsx(
          animateFast,
          "group inline-flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-3 py-1.5",
          "text-sm font-medium text-primary cursor-pointer",
          "hover:border-primary hover:bg-primary hover:text-white hover:shadow-sm hover:shadow-primary/20"
        )}
      >
        <ArrowLeft
          size={15}
          className="transition-transform group-hover:-translate-x-0.5"
        />
        Quay lại lịch sử
      </Link>

      {/* Header row */}
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="rounded-xl bg-primary/15 p-2.5 text-primary">
            <FileText size={22} />
          </span>
          <div>
            <h1 className={sectionTitle}>Chi tiết bản ghi</h1>
            <p className={clsx(mutedText, bodyLarge)}>
              Xem và chỉnh sửa thông tin phân loại
            </p>

            {/* Log ID textbox */}
            <div
              className={clsx(
                "mt-2 inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 px-2.5 py-1.5"
              )}
            >
              <span className="text-[11px] font-bold uppercase tracking-wider text-primary/60">
                Log ID
              </span>
              <code className="font-mono text-xs font-semibold text-primary">
                {log.log_id}
              </code>
              <button
                type="button"
                onClick={handleCopyId}
                title="Sao chép ID"
                className={clsx(
                  animateFast,
                  "cursor-pointer rounded p-0.5 text-primary/50 hover:bg-primary/10 hover:text-primary"
                )}
              >
                {copied ? <Check size={12} /> : <Copy size={12} />}
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowConfirm(true)}
          className={clsx(
            animateFast,
            "flex cursor-pointer items-center gap-2 rounded-lg border border-danger/40 px-3 py-1.5 text-sm text-danger",
            "hover:border-danger hover:bg-danger hover:text-white"
          )}
        >
          <Trash2 size={15} />
          Xóa bản ghi
        </button>
      </header>

      {/* Body */}
      <div className="grid gap-5 md:grid-cols-2">
        <DetailImagePanel log={log} onUpdated={setLog} />
        <DetailInfoPanel log={log} onUpdated={setLog} />
      </div>

      {/* Delete modal */}
      <DeleteConfirmModal
        open={showConfirm}
        onClose={() => !deleting && setShowConfirm(false)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Xóa bản ghi này?"
        description="Bản ghi và ảnh đi kèm sẽ bị xóa vĩnh viễn, không thể khôi phục."
      />
    </div>
  );
}