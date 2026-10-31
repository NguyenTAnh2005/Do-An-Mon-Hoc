// src/components/ui/DaysSelect.jsx
import clsx from "clsx";

import { animateFast, baseBorder } from "../../utils/style";
import { STATS_DAYS_OPTIONS } from "../../constant/statistics";

export const DaysSelect = ({ value, onChange, disabled = false }) => {
  return (
    <div
      className={clsx(
        "inline-flex overflow-hidden rounded-lg border",
        baseBorder,
        disabled && "opacity-60"
      )}
    >
      {STATS_DAYS_OPTIONS.map((option) => {
        const isActive = value === option;
        return (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            disabled={disabled}
            className={clsx(
              animateFast,
              "px-3 py-1.5 text-sm font-medium",
              isActive
                ? "bg-primary text-light-surface"
                : clsx(
                    "text-light-text dark:text-dark-text",
                    "hover:bg-primary/10 hover:text-primary"
                  ),
              disabled && "cursor-not-allowed",
              "disabled:hover:bg-transparent disabled:hover:text-light-text dark:disabled:hover:text-dark-text"
            )}
          >
            {option} ngày
          </button>
        );
      })}
    </div>
  );
};