import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import clsx from "clsx";
import { AlertCircle, ArrowLeft, FileText, Loader2, Trash2 } from "lucide-react";
import { toast } from "react-toastify";
import { classificationLogService } from "../services/classificationLog";
import DetailImagePanel from "../components/ui/DetailImagePanel";
import DetailInfoPanel from "../components/ui/DetailInfoPanel";
import DeleteConfirmModal from "../components/ui/DeleteConfirmModal";
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
      {/* Back link — tách riêng, không đè lên header */}
      <Link
        to="/history"
        className={clsx(
          animateFast,
          "inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
        )}
      >
        <ArrowLeft size={16} />
        Quay lại lịch sử
      </Link>

      {/* Header row */}
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="rounded-xl bg-primary/15 p-2.5 text-primary">
            <FileText size={22} />
          </span>
          <div>
            <h1 className={sectionTitle}>Chi tiết bản ghi</h1>
            <p className={clsx(mutedText, bodyLarge)}>
              Xem và chỉnh sửa thông tin phân loại
            </p>
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