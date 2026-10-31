// src/pages/Statistics.jsx
import { NavLink, Outlet } from "react-router-dom";
import clsx from "clsx";
import { BarChart3 } from "lucide-react";

import {
  bgSurface,
  baseBorder,
  mutedText,
  animateSlow,
  animateFast,
  sectionTitle,
  bodyLarge,
} from "../utils/style";
import { STATS_TABS } from "../constant/statistics";

export default function Statistics() {
  return (
    <div className={clsx("space-y-5", animateSlow)}>
      <header className="flex items-center gap-3">
        <span className="rounded-xl bg-primary/15 p-2.5 text-primary">
          <BarChart3 size={28} />
        </span>
        <div>
          <h1 className={sectionTitle}>Thống kê</h1>
          <p className={clsx(mutedText, bodyLarge)}>
            Thống kê các lượt phân loại, độ tin cậy hay độ chính xác model
          </p>
        </div>
      </header>

      <nav
        className={clsx(
          bgSurface,
          baseBorder,
          "flex gap-1 overflow-x-auto rounded-xl border p-1.5 shadow-sm"
        )}
      >
        {STATS_TABS.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            end={tab.end}
            className={({ isActive }) =>
              clsx(
                animateFast,
                "whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium",
                isActive
                  ? "bg-primary/15 text-primary"
                  : clsx(mutedText, "hover:bg-primary/10 hover:text-primary")
              )
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>

      <Outlet />
    </div>
  );
}