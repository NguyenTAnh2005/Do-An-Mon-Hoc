import clsx from "clsx";
import { bgSurface, baseBorder, mutedText, body, animateBase, animateSlow } from "../../utils/style";

export const StatusBadge = ({ label, online }) => {
    // Mặc định là offline
    let dotClass = "bg-danger";
    let text = "Offline";

    if (online) {
        dotClass = "bg-success";
        text = "Online";
    }

    return (
        <div className={clsx(
            bgSurface, baseBorder, animateSlow, body,
            "border-2 rounded-full px-3 py-1 flex items-center gap-2"
        )}>
            <span className={clsx(dotClass, animateBase, "h-2.5 w-2.5 rounded-full")} />
            <span className="font-semibold">{label}</span>
            <span className={mutedText}>{text}</span>
        </div>
    );
};