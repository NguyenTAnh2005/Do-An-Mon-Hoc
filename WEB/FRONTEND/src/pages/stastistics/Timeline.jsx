// src/pages/statistics/Timeline.jsx
import { useCallback, useState } from "react";
import clsx from "clsx";

import { StatusLoading, StatusError } from "../../components/ui/FetchStatus";
import { JsonPreview } from "../../components/ui/JsonPreview";
import { DaysSelect } from "../../components/ui/DaysSelect";
import { TimelineBar } from "../../components/ui/TimelineBar";
import { useStatApi } from "../../hooks/useStatApi";
import { getTimeline } from "../../services/statistics";
import {
  bgSurface,
  baseBorder,
  mutedText,
  animateBase,
  animateSlow,
  cardTitle,
} from "../../utils/style";

export function Timeline() {
  const [days, setDays] = useState(7);

  // useCallback giữ fetcher ổn định — useStatApi refetch khi `days` đổi
  const fetcher = useCallback(() => getTimeline(days), [days]);
  const { data, loading, error } = useStatApi(fetcher);

  // Loading ban đầu: chưa có data của bất kỳ lần nào
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
        {/* Header + bộ chọn ngày */}
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 className={cardTitle}>Số lượt theo ngày</h2>
          <DaysSelect value={days} onChange={setDays} disabled={loading} />
        </div>

        {/* Chart fade nhẹ khi đang fetch data mới — tránh "đứng hình" */}
        <div className={clsx(animateBase, loading && "opacity-50")}>
          <TimelineBar items={data.data.items} />
        </div>
      </section>
    </div>
  );
}