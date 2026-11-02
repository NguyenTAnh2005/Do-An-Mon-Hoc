// src/components/ui/TimelineBar.jsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import clsx from "clsx";

import { bgSurface, baseBorder, mutedText } from "../../utils/style";
import { formatDateShort, formatDateFull } from "../../utils/format";
import { TIMELINE_BAR_COLOR } from "../../constant/statistics";

const AXIS_TICK_STYLE = { fontSize: 12, fill: "#6B7274" };

const TimelineTooltip = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  const row = payload[0].payload;
  return (
    <div
      className={clsx(
        bgSurface,
        baseBorder,
        "rounded-lg border px-3 py-2 text-sm shadow-md"
      )}
    >
      <p className="font-medium">{row.fullDate}</p>
      <p className={mutedText}>Số lượt: {row.count}</p>
    </div>
  );
};

export const TimelineBar = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <p className={clsx(mutedText, "py-8 text-center text-sm")}>
        Chưa có dữ liệu
      </p>
    );
  }

  const chartData = [];
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    chartData.push({
      date_vn: item.date_vn,
      count: item.count,
      shortDate: formatDateShort(item.date_vn),
      fullDate: formatDateFull(item.date_vn),
    });
  }

  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 8, right: 8, left: 0, bottom: 8 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#6B7274"
            strokeOpacity={0.15}
            vertical={false}
          />
          <XAxis
            dataKey="shortDate"
            tick={AXIS_TICK_STYLE}
            axisLine={{ stroke: "#6B7274", strokeOpacity: 0.3 }}
            tickLine={false}
            interval="preserveStartEnd"
            minTickGap={20}
          />
          <YAxis
            allowDecimals={false}
            tick={AXIS_TICK_STYLE}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            content={<TimelineTooltip />}
            cursor={{ fill: "rgba(107, 114, 116, 0.08)" }}
          />
          <Bar
            dataKey="count"
            fill={TIMELINE_BAR_COLOR}
            radius={[4, 4, 0, 0]}
            maxBarSize={48}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};