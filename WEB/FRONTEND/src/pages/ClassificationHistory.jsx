import { useEffect, useState } from "react";
import clsx from "clsx";
import { History, Loader2, AlertCircle } from "lucide-react";
import { toast } from "react-toastify";

import { classificationLogService } from "../services/classificationLog";
import { dashboardService } from "../services/dashboard";
import HistoryTable from "../components/history/HistoryTable";
import HistoryFilters from "../components/history/HistoryFilters";
import BulkActionBar from "../components/history/BulkActionBar";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import Pagination from "../components/ui/Pagination";
import {
  bgSurface, baseBorder, mutedText,
  animateBase, animateSlow, sectionTitle, bodyLarge,
} from "../utils/style";

const PAGE_SIZE = 10;

const EMPTY_FILTERS = {
  area_id: "",
  detected_waste_type: "",
  confirmation_result: "",
  has_image: "",
  from_date: "",
  to_date: "",
};

const buildParams = (page, filters) => ({
  page,
  page_size: PAGE_SIZE,
  area_id: filters.area_id || undefined,
  detected_waste_type: filters.detected_waste_type || undefined,
  confirmation_result: filters.confirmation_result || undefined,
  has_image: filters.has_image === "" ? undefined : filters.has_image === "true",
  from_date: filters.from_date || undefined,
  to_date: filters.to_date || undefined,
});

export default function ClassificationHistory() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [areas, setAreas] = useState([]);

  // ---- Multi-select & delete ----
  const [selectedIds, setSelectedIds] = useState(() => new Set());
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  // Lấy danh sách khu vực
  useEffect(() => {
    const fetchAreas = async () => {
      try {
        const res = await dashboardService.getSnapshot();
        setAreas(res.areas.map((a) => ({ id: a.id, name: a.location_description })));
      } catch {
        setAreas([]);
      }
    };
    fetchAreas();
  }, []);

  // Lấy logs
  useEffect(() => {
    let cancelled = false;
    const fetchLogs = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await classificationLogService.getLogs(buildParams(page, filters));
        if (!cancelled) setData(res.data);
      } catch (err) {
        if (!cancelled) setError(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchLogs();
    return () => {
      cancelled = true;
    };
  }, [page, filters, reloadKey]);

  // Clear selection khi đổi trang / đổi filter
  useEffect(() => {
    setSelectedIds(new Set());
  }, [page, filters]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleReset = () => {
    setFilters(EMPTY_FILTERS);
    setPage(1);
  };

  // ---- Selection handlers ----
  const handleToggleRow = (id) => {
    if (deleting) return;
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleToggleAll = (ids) => {
    if (deleting) return;
    setSelectedIds(new Set(ids));
  };

  const handleClearSelection = () => setSelectedIds(new Set());

  // ---- Delete flow ----
  const handleDeleteSelected = async () => {
    if (!data || selectedIds.size === 0) return;
    const ids = [...selectedIds];
    setDeleting(true);
    try {
      await classificationLogService.batchDelete(ids);
      toast.success(`Đã xóa ${ids.length} bản ghi`);
      setConfirmOpen(false);
      setSelectedIds(new Set());

      // Nếu xóa hết dòng của trang hiện tại → lùi 1 trang, ngược lại refetch tại chỗ
      const wasAllOnPage = ids.length === data.items.length;
      if (wasAllOnPage && page > 1) {
        setPage((p) => p - 1);
      } else {
        setReloadKey((k) => k + 1);
      }
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        "Xóa thất bại, vui lòng thử lại";
      toast.error(msg);
    } finally {
      setDeleting(false);
    }
  };

  // ---- Early states ----
  if (!data && loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-20">
        <Loader2 size={34} className="animate-spin text-primary" />
        <p className={clsx(mutedText, "text-sm")}>Đang tải dữ liệu...</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-20">
        <span className="rounded-full bg-danger/10 p-3 text-danger">
          <AlertCircle size={30} />
        </span>
        <p className="text-sm text-danger">Lỗi: {String(error.message || error)}</p>
      </div>
    );
  }

  return (
    <div className={clsx("space-y-5", animateSlow)}>
      {/* Header */}
      <header className="flex items-center gap-3">
        <span className="rounded-xl bg-primary/15 p-2.5 text-primary">
          <History size={28} />
        </span>
        <div>
          <h1 className={sectionTitle}>Lịch sử phân loại</h1>
          <p className={clsx(mutedText, bodyLarge)}>
            Xem lại toàn bộ các lần phân loại rác
          </p>
        </div>
      </header>

      {/* Bộ lọc */}
      <section className={clsx(bgSurface, baseBorder, animateSlow, "rounded-xl border p-4 shadow-sm")}>
        <HistoryFilters
          filters={filters}
          areas={areas}
          onChange={handleFilterChange}
          onReset={handleReset}
        />
      </section>

      {/* Danh sách + action bar */}
      <section className={clsx(bgSurface, baseBorder, animateSlow, "overflow-hidden rounded-xl border shadow-sm")}>
        <div className={clsx(baseBorder, "flex items-center justify-between border-b px-4 py-3")}>
          <p className={clsx(mutedText, "text-sm")}>Danh sách bản ghi</p>
          <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
            Tổng: {data.total}
          </span>
        </div>

        {selectedIds.size > 0 && (
          <div className="px-4 pt-3">
            <BulkActionBar
              count={selectedIds.size}
              onClear={handleClearSelection}
              onDelete={() => setConfirmOpen(true)}
              disabled={deleting}
            />
          </div>
        )}

        <div className={clsx(animateBase, loading && "opacity-50")}>
          <HistoryTable
            items={data.items}
            selectedIds={selectedIds}
            onToggleRow={handleToggleRow}
            onToggleAll={handleToggleAll}
          />
        </div>

        <div className={clsx(baseBorder, "border-t px-4 py-3")}>
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={data.total}
            onChange={setPage}
            disabled={loading}
          />
        </div>
      </section>

      {error && (
        <p className="flex items-center gap-2 text-sm text-danger">
          <AlertCircle size={15} />
          Tải dữ liệu thất bại, thử lại.
        </p>
      )}

      {/* Hộp thoại xác nhận */}
      <ConfirmDialog
        open={confirmOpen}
        tone="danger"
        title="Xóa các bản ghi đã chọn?"
        description={`Bạn sắp xóa ${selectedIds.size} bản ghi. Hành động này không thể hoàn tác.`}
        confirmText={deleting ? "Đang xóa..." : `Xóa ${selectedIds.size} mục`}
        loading={deleting}
        onConfirm={handleDeleteSelected}
        onCancel={() => !deleting && setConfirmOpen(false)}
      />
    </div>
  );
}