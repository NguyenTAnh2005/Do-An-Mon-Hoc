import { useEffect, useState } from "react";
import clsx from "clsx";
import { History, Loader2, AlertCircle } from "lucide-react";
import { classificationLogService } from "../services/classificationLog";
import { dashboardService } from "../services/dashboard";
import HistoryTable from "../components/ui/HistoryTable";
import HistoryFilters from "../components/ui/HistoryFilters";
import Pagination from "../components/ui/Pagination";
import {
  bgSurface, baseBorder, mutedText,
  animateBase, animateSlow, sectionTitle, bodyLarge
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

  // Lấy danh sách khu vực 1 lần cho dropdown
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
  }, [page, filters]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleReset = () => {
    setFilters(EMPTY_FILTERS);
    setPage(1);
  };

  // Trạng thái loading ban đầu
  if (!data && loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-20">
        <Loader2 size={34} className="animate-spin text-primary" />
        <p className={clsx(mutedText, "text-sm")}>Đang tải dữ liệu...</p>
      </div>
    );
  }

  // Trạng thái lỗi ban đầu
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
    <div className={clsx(
      "space-y-5", animateSlow
    )}>
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

      {/* Danh sách kết quả */}
      <section className={clsx(bgSurface, baseBorder, animateSlow, "overflow-hidden rounded-xl border shadow-sm")}>
        <div className={clsx(baseBorder, "flex items-center justify-between border-b px-4 py-3")}>
          <p className={clsx(mutedText, "text-sm")}>Danh sách bản ghi</p>
          <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
            Tổng: {data.total}
          </span>
        </div>

        <div className={clsx(animateBase, loading && "opacity-50")}>
          <HistoryTable items={data.items} />
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

      {/* Lỗi khi đã có dữ liệu cũ */}
      {error && (
        <p className="flex items-center gap-2 text-sm text-danger">
          <AlertCircle size={15} />
          Tải dữ liệu thất bại, thử lại.
        </p>
      )}
    </div>
  );
}