// src/components/ui/WasteTypePie.jsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import clsx from "clsx";

import { bgSurface, baseBorder, cardTitle, mutedText } from "../../utils/style";
import {
  WASTE_TYPE_LABELS,
  WASTE_TYPE_COLORS,
} from "../../constant/statistics";

// Tooltip tuỳ biến — mặc định recharts dùng nền xám, không hợp theme sáng/tối
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }
  const item = payload[0].payload;
  const label = WASTE_TYPE_LABELS[item.waste_type] || item.waste_type;
  return (
    <div
      className={clsx(
        bgSurface,
        baseBorder,
        "rounded-lg border px-3 py-2 text-sm shadow-md"
      )}
    >
      <p className="font-medium">{label}</p>
      <p className={mutedText}>Số lượt: {item.count}</p>
    </div>
  );
};

export const WasteTypePie = ({ items }) => {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i].count;
  }

  if (total === 0) {
    return (
      <section
        className={clsx(bgSurface, baseBorder, "rounded-xl border p-4 shadow-sm")}
      >
        <h3 className={clsx(cardTitle, "mb-3")}>Phân bố loại rác</h3>
        <p className={clsx(mutedText, "py-8 text-center text-sm")}>
          Chưa có dữ liệu
        </p>
      </section>
    );
  }

  return (
    <section
      className={clsx(bgSurface, baseBorder, "rounded-xl border p-4 shadow-sm")}
    >
      <h3 className={clsx(cardTitle, "mb-3")}>Phân bố loại rác</h3>

      <div className="flex flex-col items-center gap-4 md:flex-row">
        {/* Vùng donut — vuông, tối đa 220px, co giãn theo màn hình */}
        <div className="aspect-square w-full max-w-[220px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={items}
                dataKey="count"
                nameKey="waste_type"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={85}
                paddingAngle={2}
              >
                {items.map((entry) => (
                  <Cell
                    key={entry.waste_type}
                    fill={WASTE_TYPE_COLORS[entry.waste_type] || "#6B7274"}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend tự vẽ — khớp theme + có % */}
        <ul className="w-full flex-1 space-y-2">
          {items.map((item) => {
            const percent = Math.round((item.count / total) * 1000) / 10;
            const label = WASTE_TYPE_LABELS[item.waste_type] || item.waste_type;
            const color = WASTE_TYPE_COLORS[item.waste_type] || "#6B7274";
            return (
              <li
                key={item.waste_type}
                className="flex items-center gap-2 text-sm"
              >
                <span
                  className="inline-block h-3 w-3 rounded-sm"
                  style={{ backgroundColor: color }}
                />
                <span className="flex-1">{label}</span>
                <span className={mutedText}>
                  {item.count} · {percent}%
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
};