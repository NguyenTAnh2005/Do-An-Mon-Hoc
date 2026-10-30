import { useEffect, useState } from "react";
import clsx from "clsx";
import { MapPin, AlertTriangle, Server, Inbox, LayoutDashboard  } from "lucide-react";

import {
    sectionTitle, cardTitle, mutedText, body, bodyLarge,
    bgSurface, baseBorder, animateSlow, hoverShadow
} from "../utils/style";
import { useDashboardSocket } from "../hooks/useDashboardSocket";
import { dashboardService } from "../services/dashboard";
import { TrashBinCard } from "../components/ui/TrashBinCard";
import { StatusBadge } from "../components/ui/StatusBadge";
import { FILL_WARNING_PERCENT, FILL_DANGER_PERCENT } from "../constant/dashboard";

const Dashboard = () => {
    const [areas, setAreas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState(null);

    // Nhận từng tin từ WebSocket rồi cập nhật đúng phần tử trong state
    const handleMessage = (message) => {
        if (message.type === "fill_level") {
            setAreas((prevAreas) =>
                prevAreas.map((area) => {
                    if (area.id !== message.area_id) return area;
                    return {
                        ...area,
                        trash_bins: area.trash_bins.map((bin) => {
                            if (bin.waste_type !== message.waste_type) return bin;
                            return { ...bin, current_fill_percent: message.current_fill_percent };
                        }),
                    };
                })
            );
        } else if (message.type === "status") {
            setAreas((prevAreas) =>
                prevAreas.map((area) => {
                    if (area.id !== message.area_id) return area;
                    if (message.source === "iot") return { ...area, iot_online: message.online };
                    if (message.source === "ai") return { ...area, ai_online: message.online };
                    return area;
                })
            );
        }
    };
    const { status } = useDashboardSocket(handleMessage);

    // Tải dữ liệu ban đầu bằng REST
    useEffect(() => {
        let isMounted = true;
        const fetchSnapshot = async () => {
            try {
                const res = await dashboardService.getSnapshot();
                if (isMounted) setAreas(res.areas);
            } catch (error) {
                console.error("[Dashboard] snapshot lỗi:", error);
                if (isMounted) setErrorMessage("Không tải được dữ liệu dashboard, vui lòng thử lại.");
            } finally {
                if (isMounted) setLoading(false);
            }
        };
        fetchSnapshot();
        return () => { isMounted = false; };
    }, []);

    // ---- Thống kê chỉ để HIỂN THỊ, đọc từ state, không thay đổi logic ----
    const totalBins = areas.reduce((s, a) => s + (a.trash_bins?.length || 0), 0);
    const onlineAreas = areas.filter((a) => a.iot_online && a.ai_online).length;
    const warningBins = areas.reduce(
        (s, a) => s + (a.trash_bins?.filter((b) =>
            b.current_fill_percent >= FILL_WARNING_PERCENT &&
            b.current_fill_percent < FILL_DANGER_PERCENT
        ).length || 0), 0
    );
    const dangerBins = areas.reduce(
        (s, a) => s + (a.trash_bins?.filter((b) =>
            b.current_fill_percent >= FILL_DANGER_PERCENT
        ).length || 0), 0
    );

    return (
        <div className={clsx("flex flex-col gap-8 w-full", animateSlow)}>
            {/* TIÊU ĐỀ + TRẠNG THÁI KẾT NỐI REALTIME */}
            <div className="flex flex-wrap items-start justify-between gap-4">
                <header className="flex items-center gap-3">
                    <span className="rounded-xl bg-primary/15 p-2.5 text-primary">
                        <LayoutDashboard size={28} />
                    </span>
                    <div>
                        <h1 className={sectionTitle}>Dashboard</h1>
                        <p className={clsx(mutedText, bodyLarge)}>
                            Theo dõi mức đầy của từng thùng và trạng thái thiết bị theo thời gian thực
                        </p>
                    </div>
                </header>
                <StatusBadge label="Realtime" online={status === "open"} />
            </div>

            {/* THỐNG KÊ NHANH — chỉ hiện khi đã có dữ liệu */}
            {!loading && !errorMessage && areas.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard
                        Icon={MapPin}
                        label="Khu vực"
                        value={areas.length}
                        sub={`${totalBins} thùng`}
                        tone="primary"
                    />
                    <StatCard
                        Icon={Server}
                        label="Online"
                        value={`${onlineAreas}/${areas.length}`}
                        sub="Khu vực"
                        tone="success"
                    />
                    <StatCard
                        Icon={AlertTriangle}
                        label="Sắp đầy"
                        value={warningBins}
                        sub="Thùng"
                        tone="warning"
                    />
                    <StatCard
                        Icon={AlertTriangle}
                        label="Đã đầy"
                        value={dangerBins}
                        sub="Thùng"
                        tone="danger"
                    />
                </div>
            )}

            {/* ĐANG TẢI — SKELETON */}
            {loading && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {[0, 1, 2].map((i) => (
                        <SkeletonCard key={i} />
                    ))}
                </div>
            )}

            {/* LỖI */}
            {!loading && errorMessage && (
                <div className={clsx(
                    bgSurface, baseBorder, animateSlow,
                    "border-2 rounded-xl p-6 flex items-center gap-3 text-danger"
                )}>
                    <AlertTriangle size={22} className="shrink-0" />
                    <p>{errorMessage}</p>
                </div>
            )}

            {/* RỖNG */}
            {!loading && !errorMessage && areas.length === 0 && (
                <div className={clsx(
                    bgSurface, baseBorder, animateSlow,
                    "border-2 rounded-xl p-12 flex flex-col items-center gap-3 text-center"
                )}>
                    <span className="h-14 w-14 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                        <Inbox size={26} />
                    </span>
                    <p className={clsx(body, "font-semibold")}>Chưa có khu vực nào</p>
                    <p className={clsx(mutedText, body)}>
                        Hệ thống sẽ hiển thị khi có dữ liệu từ thiết bị.
                    </p>
                </div>
            )}

            {/* TỪNG KHU VỰC */}
            <div className="flex flex-col gap-6">
                {areas.map((area) => (
                    <section
                        key={area.id}
                        className={clsx(
                            bgSurface, baseBorder, animateSlow, hoverShadow,
                            "border-2 rounded-xl p-5 flex flex-col gap-4"
                        )}
                    >
                        <div className={clsx(
                            "flex flex-wrap items-center justify-between gap-3 pb-3",
                            "border-b border-light-text/10 dark:border-dark-text/10"
                        )}>
                            <div className="flex items-center gap-3 min-w-0">
                                <span className="h-10 w-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                                    <MapPin size={20} />
                                </span>
                                <div className="min-w-0">
                                    <h2 className={clsx(cardTitle, "truncate")}>
                                        {area.location_description}
                                    </h2>
                                    <p className={clsx(mutedText, "text-xs")}>
                                        {area.trash_bins?.length || 0} thùng
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-2 flex-wrap">
                                <StatusBadge label="IoT" online={area.iot_online} />
                                <StatusBadge label="AI" online={area.ai_online} />
                            </div>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            {area.trash_bins.map((bin) => (
                                <TrashBinCard
                                    key={bin.waste_type}
                                    wasteType={bin.waste_type}
                                    percent={bin.current_fill_percent}
                                />
                            ))}
                        </div>
                    </section>
                ))}
            </div>
        </div>
    );
};

/* ---- Component con: THUẦN HIỂN THỊ ---- */

const StatCard = ({ Icon, label, value, sub, tone = "primary" }) => {
    const toneClasses = {
        primary: "bg-primary/10 text-primary",
        success: "bg-success/10 text-success",
        warning: "bg-warning/10 text-warning",
        danger:  "bg-danger/10  text-danger",
    };
    return (
        <div className={clsx(
            bgSurface, baseBorder, animateSlow,
            "border-2 rounded-xl p-4 flex items-center gap-3"
        )}>
            <span className={clsx(
                "h-10 w-10 rounded-lg flex items-center justify-center shrink-0",
                toneClasses[tone]
            )}>
                <Icon size={20} />
            </span>
            <div className="min-w-0">
                <p className={clsx(mutedText, "text-xs uppercase tracking-wide")}>{label}</p>
                <p className="text-xl font-bold leading-tight">{value}</p>
                {sub && <p className={clsx(mutedText, "text-xs")}>{sub}</p>}
            </div>
        </div>
    );
};

const SkeletonCard = () => (
    <div className={clsx(
        bgSurface, baseBorder,
        "border-2 rounded-xl p-4 flex flex-col gap-3 animate-pulse"
    )}>
        <div className="h-5 w-1/2 rounded bg-light-text/10 dark:bg-dark-text/10" />
        <div className="h-8 w-1/3 rounded bg-light-text/10 dark:bg-dark-text/10" />
        <div className="h-3 w-full rounded-full bg-light-text/10 dark:bg-dark-text/10" />
    </div>
);

export default Dashboard;