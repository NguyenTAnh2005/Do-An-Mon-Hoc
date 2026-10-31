// src/components/ui/StatCard.jsx
import clsx from "clsx";
import { CardItem } from "../wrapper/CardItem";
import { mutedText } from "../../utils/style";
import {
  STAT_TONE_ICON_CLASS,
  STAT_TONE_VALUE_CLASS,
} from "../../constant/statistics";

export const StatCard = ({ icon: Icon, label, value, hint, tone = "primary" }) => {
  return (
    <CardItem styleClass="rounded-xl border p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className={clsx(mutedText, "text-xs font-mono uppercase tracking-wide")}>
          {label}
        </p>
        <span className={clsx("rounded-lg p-1.5", STAT_TONE_ICON_CLASS[tone])}>
          <Icon size={18} />
        </span>
      </div>
      <p className={clsx("text-3xl font-bold", STAT_TONE_VALUE_CLASS[tone])}>
        {value}
      </p>
      {hint && <p className={clsx(mutedText, "text-xs")}>{hint}</p>}
    </CardItem>
  );
};