// src/components/ui/AccuracyLine.jsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import clsx from "clsx";

import { bgSurface, baseBorder, mutedText } from "../../utils/style";
import { formatDateShort, formatDateFull } from "../../utils/format";
import { ACCURACY_LINE_COLORS } from "../../constant/statistics";

const AXIS_TICK_STYLE = { fontSize: 12, fill: "#6B7274" };

// null → "—", số → "57.3%" — KHÔNG map null thành "0%"
const formatPercentOrDash = (value) => {
  if (value === null || value === undefined) {
    return "—";
  }
  return `${value}%`;
};

const AccuracyTooltip = ({ active, payload }) => {
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
      <ul className="mt-1 space-y-1">
        <li className="flex items-center gap-2">
          <span
            className="inline-block h-0.5 w-3 rounded-sm"
            style={{ backgroundColor: ACCURACY_LINE_COLORS.accuracy }}
          />
          <span className="flex-1">Độ chính xác</span>
          <span className={mutedText}>
            {formatPercentOrDash(row.accuracy_percent)}
          </span>
        </li>
        <li className="flex items-center gap-2">
          <span
            className="inline-block h-0.5 w-3 rounded-sm"
            style={{ backgroundColor: ACCURACY_LINE_COLORS.confidence }}
          />
          <span className="flex-1">Độ tin cậy</span>
          <span className={mutedText}>
            {formatPercentOrDash(row.confidence_percent)}
          </span>
        </li>
      </ul>
      <p className={clsx(mutedText, "mt-2 text-xs")}>
        Đã xác nhận: {row.confirmed_correct} đúng · {row.confirmed_incorrect} sai
      </p>
    </div>
  );
};

export const AccuracyLine = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <p className={clsx(mutedText, "py-8 text-center text-sm")}>
        Chưa có dữ liệu
      </p>
    );
  }

  // Build data row: giữ nguyên null ở accuracy_percent / confidence_percent
  const chartData = [];
  for (let i = 0; i < items.length; i++) {
    const item = items[i];

    let confidencePercent = null;
    if (
      item.average_confidence !== null &&
      item.average_confidence !== undefined
    ) {
      confidencePercent = Math.round(item.average_confidence * 1000) / 10;
    }

    chartData.push({
      date_vn: item.date_vn,
      shortDate: formatDateShort(item.date_vn),
      fullDate: formatDateFull(item.date_vn),
      accuracy_percent: item.accuracy_percent,
      confidence_percent: confidencePercent,
      confirmed_correct: item.confirmed_correct,
      confirmed_incorrect: item.confirmed_incorrect,
    });
  }

  return (
    <>
      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
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
              domain={[0, 100]}
              ticks={[0, 25, 50, 75, 100]}
              tick={AXIS_TICK_STYLE}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              content={<AccuracyTooltip />}
              cursor={{
                stroke: "#6B7274",
                strokeOpacity: 0.3,
                strokeDasharray: "3 3",
              }}
            />

            {/* connectNulls={false} — ngày không có xác nhận sẽ đứt đoạn,
                KHÔNG nối về 0 (đó sẽ làm sai nghĩa dữ liệu) */}
            <Line
              type="monotone"
              dataKey="accuracy_percent"
              stroke={ACCURACY_LINE_COLORS.accuracy}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="confidence_percent"
              stroke={ACCURACY_LINE_COLORS.confidence}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Legend dạng đường kẻ ngắn (không phải ô vuông) — gợi ý "line" */}
      <ul className="mt-3 flex flex-wrap gap-4">
        <li className="flex items-center gap-2 text-sm">
          <span
            className="inline-block h-0.5 w-4 rounded-sm"
            style={{ backgroundColor: ACCURACY_LINE_COLORS.accuracy }}
          />
          <span>Độ chính xác</span>
        </li>
        <li className="flex items-center gap-2 text-sm">
          <span
            className="inline-block h-0.5 w-4 rounded-sm"
            style={{ backgroundColor: ACCURACY_LINE_COLORS.confidence }}
          />
          <span>Độ tin cậy (×100)</span>
        </li>
      </ul>
    </>
  );
};