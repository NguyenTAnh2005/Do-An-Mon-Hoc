/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],

  theme: {
    extend: {
      colors: {
        // ── PRIMARY — emerald eco ─────────────────────────────
        // Sâu hơn success để tách bạch; có token sáng cho dark mode
        primary: {
          DEFAULT:     '#047857',                  // emerald-700 — đậm, "premium"
          hover:       '#065F46',                  // emerald-800
          soft:        '#ECFDF5',                  // emerald-50  — bg alert/badge
          'soft-dark': 'rgba(4,120,87,0.18)',      // cho dark mode
          muted:       '#6EE7B7',                  // emerald-300 — text/icon trên nền tối
        },

        // ── SEMANTIC — tách rõ khỏi primary ──────────────────
        success: { DEFAULT: '#22C55E', hover: '#16A34A', soft: '#DCFCE7' },
        danger:  { DEFAULT: '#EF4444', hover: '#DC2626', soft: '#FEE2E2' },
        warning: { DEFAULT: '#F59E0B', hover: '#D97706', soft: '#FEF3C7' },
        info:    { DEFAULT: '#3B82F6', hover: '#2563EB', soft: '#DBEAFE' },

        // ── NEUTRAL — ám xanh rất nhẹ cho cohesion ───────────
        light: {
          bg:       '#F5F8F6',   // thay #F6F7F7 — pha xanh nhẹ
          surface:  '#FFFFFF',
          elevated: '#EFF4F1',   // input / card hover
          border:   '#E2E9E5',   // viền mềm (đang thiếu)
          text:     '#17191A',
          muted:    '#6B7274',
        },
        dark: {
          bg:       '#0D1211',   // thay #0F1112 — ám xanh rất nhẹ
          surface:  '#171C1A',
          elevated: '#1F2624',   // input / card hover
          border:   '#283230',
          text:     '#EBEDEE',
          muted:    '#8B9193',
        },
      },

      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      transitionDuration: { fast: '200ms', base: '300ms', slow: '500ms' },
    },
  },
  plugins: [],
}