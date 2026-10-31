// src/components/ui/AreaStackedBar.jsx
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

import { bgSurface, baseBorder, cardTitle, mutedText } from "../../utils/style";
import {
  WASTE_TYPE_LABELS,
  WASTE_TYPE_COLORS,
} from "../../constant/statistics";

// Style chung cho tick trục — recharts đổ qua prop SVG, không nhận class Tailwind
const AXIS_TICK_STYLE = { fontSize: 12, fill: "#6B7274" };

// 3 loại cố định — dùng để render 3 <Bar> + legend
const WASTE_TYPE_KEYS = ["recyclable", "organic", "inorganic"];

const BarTooltip = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  const row = payload[0].payload;
  const rawTypes = row.by_waste_type_raw || [];

  return (
    <div
      className={clsx(
        bgSurface,
        baseBorder,
        "rounded-lg border px-3 py-2 text-sm shadow-md"
      )}
    >
      <p className="font-medium">{row.fullLabel}</p>
      <p className={mutedText}>Tổng: {row.total_logs}</p>
      <ul className="mt-2 space-y-1">
        {rawTypes.map((t) => (
          <li key={t.waste_type} className="flex items-center gap-2 text-xs">
            <span
              className="inline-block h-2 w-2 rounded-sm"
              style={{
                backgroundColor: WASTE_TYPE_COLORS[t.waste_type] || "#6B7274",
              }}
            />
            <span className="flex-1">
              {WASTE_TYPE_LABELS[t.waste_type] || t.waste_type}
            </span>
            <span className={mutedText}>{t.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

// "Area 1 - Front yard" → "Area 1"; fallback "Khu {id}" nếu chuỗi không có " - "
const shortenAreaName = (item) => {
  if (!item.location_description) {
    return `Khu ${item.area_id}`;
  }
  const parts = item.location_description.split(" - ");
  return parts[0] || `Khu ${item.area_id}`;
};

// Chuyển item backend → row phẳng cho BarChart: 3 key số + nhãn
const buildChartRow = (item) => {
  const counts = { recyclable: 0, organic: 0, inorganic: 0 };
  for (let i = 0; i < item.by_waste_type.length; i++) {
    const t = item.by_waste_type[i];
    counts[t.waste_type] = t.count;
  }

  return {
    area_id: item.area_id,
    shortLabel: shortenAreaName(item),
    fullLabel: item.location_description,
    total_logs: item.total_logs,
    recyclable: counts.recyclable,
    organic: counts.organic,
    inorganic: counts.inorganic,
    by_waste_type_raw: item.by_waste_type,
  };
};

export const AreaStackedBar = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <section
        className={clsx(bgSurface, baseBorder, "rounded-xl border p-4 shadow-sm")}
      >
        <h3 className={clsx(cardTitle, "mb-3")}>Phân bố theo khu vực</h3>
        <p className={clsx(mutedText, "py-8 text-center text-sm")}>
          Chưa có dữ liệu
        </p>
      </section>
    );
  }

  const chartData = [];
  for (let i = 0; i < items.length; i++) {
    chartData.push(buildChartRow(items[i]));
  }

  return (
    <section
      className={clsx(bgSurface, baseBorder, "rounded-xl border p-4 shadow-sm")}
    >
      <h3 className={clsx(cardTitle, "mb-3")}>Phân bố theo khu vực</h3>

      {/* Chart cao cố định 320px — chỉ có 2 cột nên đủ thoáng */}
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
              dataKey="shortLabel"
              tick={AXIS_TICK_STYLE}
              axisLine={{ stroke: "#6B7274", strokeOpacity: 0.3 }}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={AXIS_TICK_STYLE}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={<BarTooltip />}
              cursor={{ fill: "rgba(107, 114, 116, 0.08)" }}
            />
            <Bar
              dataKey="recyclable"
              stackId="a"
              fill={WASTE_TYPE_COLORS.recyclable}
            />
            <Bar
              dataKey="organic"
              stackId="a"
              fill={WASTE_TYPE_COLORS.organic}
            />
            <Bar
              dataKey="inorganic"
              stackId="a"
              fill={WASTE_TYPE_COLORS.inorganic}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend 3 loại rác */}
      <ul className="mt-3 flex flex-wrap gap-4">
        {WASTE_TYPE_KEYS.map((key) => (
          <li key={key} className="flex items-center gap-2 text-sm">
            <span
              className="inline-block h-3 w-3 rounded-sm"
              style={{ backgroundColor: WASTE_TYPE_COLORS[key] }}
            />
            <span>{WASTE_TYPE_LABELS[key]}</span>
          </li>
        ))}
      </ul>
    </section>
  );
};