// src/pages/statistics/ByArea.jsx
import clsx from "clsx";

import { StatusLoading, StatusError } from "../../components/ui/FetchStatus";
import { AreaStackedBar } from "../../components/ui/AreaStackedBar";
import { useStatApi } from "../../hooks/useStatApi";
import { getByArea } from "../../services/statistics";
import { animateSlow } from "../../utils/style";

export function ByArea() {
  const { data, loading, error } = useStatApi(getByArea);

  if (loading && !data) {
    return <StatusLoading />;
  }
  if (error && !data) {
    return <StatusError message={String(error.message || error)} />;
  }

  return (
    <div className={clsx("space-y-5", animateSlow)}>
      <AreaStackedBar items={data.data.items} />
    </div>
  );
}