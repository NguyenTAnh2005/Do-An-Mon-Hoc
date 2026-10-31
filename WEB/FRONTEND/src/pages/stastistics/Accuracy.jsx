// src/pages/statistics/Accuracy.jsx
import { useCallback, useState } from "react";
import clsx from "clsx";

import { StatusLoading, StatusError } from "../../components/ui/FetchStatus";
import { JsonPreview } from "../../components/ui/JsonPreview";
import { DaysSelect } from "../../components/ui/DaysSelect";
import { AccuracyLine } from "../../components/ui/AccuracyLine";
import { useStatApi } from "../../hooks/useStatApi";
import { getAccuracyTimeline } from "../../services/statistics";
import {
  bgSurface,
  baseBorder,
  mutedText,
  animateBase,
  animateSlow,
  cardTitle,
} from "../../utils/style";

export function Accuracy() {
  const [days, setDays] = useState(7);

  // fetcher phải ổn định tham chiếu — useCallback để effect chỉ chạy khi days đổi
  const fetcher = useCallback(() => getAccuracyTimeline(days), [days]);
  const { data, loading, error } = useStatApi(fetcher);

  if (loading && !data) {
    return <StatusLoading />;
  }
  if (error && !data) {
    return <StatusError message={String(error.message || error)} />;
  }

  return (
    <div className={clsx("space-y-5", animateSlow)}>
      <section
        className={clsx(
          bgSurface,
          baseBorder,
          "rounded-xl border p-4 shadow-sm"
        )}
      >
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 className={cardTitle}>Độ chính xác & độ tin cậy theo ngày</h2>
          <DaysSelect value={days} onChange={setDays} disabled={loading} />
        </div>

        {/* Chart mờ dần khi đang refetch — tránh flash trắng */}
        <div className={clsx(animateBase, loading && "opacity-50")}>
          <AccuracyLine items={data.data.items} />
        </div>
      </section>
    </div>
  );
}