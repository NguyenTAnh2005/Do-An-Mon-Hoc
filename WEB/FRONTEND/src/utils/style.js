import clsx from 'clsx';

// Nền gốc
export const baseBackground = "bg-light-bg dark:bg-dark-bg";
export const baseText = "text-light-text dark:text-dark-text";
// --> Class Gốc
export const baseTextBg = clsx( baseBackground, baseText);

// Phụ - nổi bật
export const bgSurface = "bg-light-surface dark:bg-dark-surface"; 
export const mutedText = "text-light-muted dark:text-dark-muted";

// Animate
const animate = 'transition-all ease-linear';
export const animateFast = clsx(animate, "duration-fast");
export const animateBase = clsx(animate, "duration-base");
export const animateSlow = clsx(animate, "duration-slow");


// ============ TYPE SCALE (5 bậc + 1 biến thể) ============
// Đọc trong note DOCS/FRONTEND/setup-ui.md
export const display = "text-4xl md:text-6xl font-bold";
export const bodyLarge = clsx("text-xl md:text-2xl font-semibold");
export const sectionTitle = "text-3xl md:text-4xl font-bold";
export const cardTitle = "text-lg md:text-xl font-semibold";
export const body = "text-sm lg:text-base";
export const metaLabel = "text-xs font-mono";


// Khác
export const baseBorder = "border-light-text/15 dark:border-dark-text/15";
export const hoverShadow = "hover:shadow-md hover:shadow-primary";
