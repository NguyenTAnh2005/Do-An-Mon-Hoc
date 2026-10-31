// src/pages/statistics/Overview.jsx
import clsx from "clsx";
import { Recycle, Target, Gauge, HelpCircle } from "lucide-react";

import { StatusLoading, StatusError } from "../../components/ui/FetchStatus";
import { JsonPreview } from "../../components/ui/JsonPreview";
import { StatCard } from "../../components/ui/StatCard";
import { WasteTypePie } from "../../components/ui/WasteTypePie";
import { ConfirmBar } from "../../components/ui/ConfirmBar";
import { useStatApi } from "../../hooks/useStatApi";
import { getOverview } from "../../services/statistics";
import { bgSurface, baseBorder, mutedText, animateSlow } from "../../utils/style";
import {
  ACCURACY_THRESHOLDS,
  STAT_EMPTY_PLACEHOLDER,
} from "../../constant/statistics";

const formatPercent = (value) => {
  if (value === null || value === undefined) {
    return STAT_EMPTY_PLACEHOLDER;
  }
  return `${value}%`;
};

const formatNumber = (value) => {
  if (value === null || value === undefined) {
    return STAT_EMPTY_PLACEHOLDER;
  }
  return String(value);
};

const accuracyTone = (value) => {
  if (value === null || value === undefined) {
    return "primary";
  }
  if (value >= ACCURACY_THRESHOLDS.good) {
    return "success";
  }
  if (value >= ACCURACY_THRESHOLDS.medium) {
    return "warning";
  }
  return "danger";
};

export function Overview() {
  const { data, loading, error } = useStatApi(getOverview);

  if (loading && !data) {
    return <StatusLoading />;
  }
  if (error && !data) {
    return <StatusError message={String(error.message || error)} />;
  }

  const overview = data.data;
  const confirmedTotal =
    overview.confirmed_correct + overview.confirmed_incorrect;

  let confidencePercent = null;
  if (
    overview.average_confidence !== null &&
    overview.average_confidence !== undefined
  ) {
    confidencePercent = Math.round(overview.average_confidence * 1000) / 10;
  }

  return (
    <div className={clsx("space-y-5", animateSlow)}>
      {/* Hàng 4 thẻ số (giữ nguyên) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Recycle}
          label="Tổng lượt phân loại"
          value={formatNumber(overview.total_logs)}
          hint={`${overview.by_waste_type.length} loại rác`}
          tone="primary"
        />
        <StatCard
          icon={Target}
          label="Độ chính xác"
          value={formatPercent(overview.accuracy_percent)}
          hint={`${confirmedTotal} lượt đã xác nhận`}
          tone={accuracyTone(overview.accuracy_percent)}
        />
        <StatCard
          icon={Gauge}
          label="Độ tin cậy TB"
          value={formatPercent(confidencePercent)}
          hint="Thang 0–100%"
          tone="primary"
        />
        <StatCard
          icon={HelpCircle}
          label="Chưa xác nhận"
          value={formatNumber(overview.unconfirmed)}
          hint={`Trên ${overview.total_logs} tổng cộng`}
          tone={overview.unconfirmed > 0 ? "warning" : "success"}
        />
      </div>

      {/* Hai khối cạnh nhau: donut 3 loại rác + thanh xác nhận */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <WasteTypePie items={overview.by_waste_type} />
        <ConfirmBar
          correct={overview.confirmed_correct}
          incorrect={overview.confirmed_incorrect}
          unconfirmed={overview.unconfirmed}
        />
      </div>
    </div>
  );
}