import clsx from "clsx";
import {
  MapPin, Tag, CheckCircle2, Image as ImageIcon,
  CalendarDays, ChevronDown, RotateCcw,
} from "lucide-react";
import { WASTE_TYPE_LABELS } from "../../constant/dashboard";
import { CONFIRMATION_LABELS } from "../../constant/classificationHistory";
import { animateFast, animateSlow, baseBorder, mutedText } from "../../utils/style";

const wrapperClass = "relative flex items-center";

// Phần "tĩnh" của field, tách khỏi phần active/idle để tránh lặp
const fieldBase = clsx(
  animateSlow,
  "rounded-lg border pl-9 pr-8 py-2 text-sm cursor-pointer",
  "bg-light-surface text-light-text",
  "dark:bg-dark-surface dark:text-dark-text",
  "focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary",
);

// Khi field CÓ giá trị → viền + nền primary nhạt để mắt bắt ngay "đang lọc cái này"
const fieldActive = clsx(
  "border-primary/60 bg-primary/5 dark:bg-primary/10",
  "ring-1 ring-primary/20",
);

// Khi field TRỐNG → viền mặc định, hover nhẹ
const fieldIdle = clsx(baseBorder, "hover:border-primary/50");

const selectClass = clsx(fieldBase, "appearance-none");
const dateClass = clsx(
  fieldBase,
  "pr-3",
  "dark:[color-scheme:dark]",
  // Làm mờ icon lịch gốc của Chromium cho đỡ "rối" cạnh icon riêng bên trái
  "[&::-webkit-calendar-picker-indicator]:opacity-60",
  "[&::-webkit-calendar-picker-indicator]:cursor-pointer",
);

const optionClass = "bg-light-surface text-light-text dark:bg-dark-surface dark:text-dark-text";

// Icon đổi màu theo trạng thái active → phụ họa cho viền
const iconClass = (active) =>
  clsx(
    "absolute left-3 pointer-events-none z-10 transition-colors",
    active ? "text-primary" : "text-primary/60"
  );

const chevronClass = "absolute right-2.5 pointer-events-none opacity-60 z-10";

// Nhãn nhỏ đứng trước 2 ô ngày — thu gọn hơn kiểu "Từ [date] Đến [date]"
const dateLabelClass = clsx(mutedText, "text-xs font-medium whitespace-nowrap uppercase tracking-wide");

export default function HistoryFilters({ filters, areas, onChange, onReset }) {
  // Đếm số filter đang bật — hiển thị lên nút Xóa cho trực quan
  const activeCount = Object.values(filters).filter((v) => v !== "").length;

  return (
    <div className={clsx("flex flex-wrap items-center gap-3", animateSlow)}>
      {/* Khu vực */}
      <div className={wrapperClass}>
        <MapPin size={15} className={iconClass(!!filters.area_id)} />
        <select
          className={clsx(selectClass, filters.area_id ? fieldActive : fieldIdle)}
          value={filters.area_id}
          onChange={(e) => onChange("area_id", e.target.value)}
        >
          <option className={optionClass} value="">Tất cả khu vực</option>
          {areas.map((a) => (
            <option className={optionClass} key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
        <ChevronDown size={14} className={chevronClass} />
      </div>

      {/* Loại rác */}
      <div className={wrapperClass}>
        <Tag size={15} className={iconClass(!!filters.detected_waste_type)} />
        <select
          className={clsx(selectClass, filters.detected_waste_type ? fieldActive : fieldIdle)}
          value={filters.detected_waste_type}
          onChange={(e) => onChange("detected_waste_type", e.target.value)}
        >
          <option className={optionClass} value="">Tất cả loại rác</option>
          {Object.entries(WASTE_TYPE_LABELS).map(([value, label]) => (
            <option className={optionClass} key={value} value={value}>{label}</option>
          ))}
        </select>
        <ChevronDown size={14} className={chevronClass} />
      </div>

      {/* Trạng thái xác nhận */}
      <div className={wrapperClass}>
        <CheckCircle2 size={15} className={iconClass(!!filters.confirmation_result)} />
        <select
          className={clsx(selectClass, filters.confirmation_result ? fieldActive : fieldIdle)}
          value={filters.confirmation_result}
          onChange={(e) => onChange("confirmation_result", e.target.value)}
        >
          <option className={optionClass} value="">Tất cả trạng thái</option>
          {Object.entries(CONFIRMATION_LABELS).map(([value, label]) => (
            <option className={optionClass} key={value} value={value}>{label}</option>
          ))}
        </select>
        <ChevronDown size={14} className={chevronClass} />
      </div>

      {/* Ảnh */}
      <div className={wrapperClass}>
        <ImageIcon size={15} className={iconClass(!!filters.has_image)} />
        <select
          className={clsx(selectClass, filters.has_image ? fieldActive : fieldIdle)}
          value={filters.has_image}
          onChange={(e) => onChange("has_image", e.target.value)}
        >
          <option className={optionClass} value="">Ảnh: tất cả</option>
          <option className={optionClass} value="true">Có ảnh</option>
          <option className={optionClass} value="false">Chưa có ảnh</option>
        </select>
        <ChevronDown size={14} className={chevronClass} />
      </div>

      {/* Nhóm ngày — gom vào 1 khối con để khi wrap không bị tách rời */}
      <div className="flex items-center gap-2 rounded-lg bg-primary/5 dark:bg-primary/10 px-2 py-1">
        <div className="flex items-center gap-2">
          <span className={dateLabelClass}>Từ</span>
          <div className={wrapperClass}>
            <CalendarDays size={15} className={iconClass(!!filters.from_date)} />
            <input
              type="date"
              className={clsx(dateClass, filters.from_date ? fieldActive : fieldIdle)}
              value={filters.from_date}
              max={filters.to_date || undefined}
              onChange={(e) => onChange("from_date", e.target.value)}
            />
          </div>
        </div>

        {/* Dấu gạch nối giữa 2 mốc thời gian */}
        <span className={clsx(mutedText, "text-sm select-none")}>→</span>

        <div className="flex items-center gap-2">
          <span className={dateLabelClass}>Đến</span>
          <div className={wrapperClass}>
            <CalendarDays size={15} className={iconClass(!!filters.to_date)} />
            <input
              type="date"
              className={clsx(dateClass, filters.to_date ? fieldActive : fieldIdle)}
              value={filters.to_date}
              min={filters.from_date || undefined}
              onChange={(e) => onChange("to_date", e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Nút xóa lọc — có badge đếm + disable khi không có filter nào */}
      <button
        onClick={onReset}
        disabled={activeCount === 0}
        className={clsx(
          animateFast,
          "ml-auto flex items-center gap-2 rounded-lg border px-3 py-2 text-sm cursor-pointer",
          "border-danger/40 text-danger",
          "hover:bg-danger hover:text-white hover:border-danger",
          "disabled:opacity-40 disabled:cursor-not-allowed",
          "disabled:hover:bg-transparent disabled:hover:text-danger disabled:hover:border-danger/40"
        )}
      >
        <RotateCcw size={14} />
        Xóa lọc
        {activeCount > 0 && (
          <span className="ml-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-danger px-1.5 text-[11px] font-bold text-white">
            {activeCount}
          </span>
        )}
      </button>
    </div>
  );
}