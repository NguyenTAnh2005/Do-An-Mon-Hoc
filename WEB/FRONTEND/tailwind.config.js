/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      // WEB/FRONTEND/tailwind.config.js — phần colors
      colors: {
        // MÀU CHÍNH — xanh lá emerald, đủ đậm để không chói, tách biệt với success
        primary: { DEFAULT: '#059669', hover: '#047857' }, // emerald-600 / emerald-700

        // MÀU TRẠNG THÁI (semantic) — giữ nguyên
        success: { DEFAULT: '#22C55E', hover: '#16A34A' },
        danger:  { DEFAULT: '#EF4444', hover: '#DC2626' },
        warning: { DEFAULT: '#F59E0B', hover: '#D97706' },

        // NEUTRAL — đen/trắng phân biệt rõ, không dùng #000/#FFF để tránh chói
        light: {
          bg:      '#F6F7F7',   // trắng xám nhẹ — phân biệt với surface
          surface: '#FFFFFF',   // trắng tinh cho card
          text:    '#17191A',   // đen mềm (không phải #000)
          muted:   '#6B7274'    // xám trung tính
        },
        dark: {
          bg:      '#0F1112',   // đen mềm (không phải #000) — viền không bị cứng
          surface: '#1A1D1E',   // sáng hơn nền để card nổi khối
          text:    '#EBEDEE',   // trắng mềm (không phải #FFF) — không chói
          muted:   '#8B9193'    // xám sáng đủ đọc
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      transitionDuration: { fast: '200ms', base: '300ms', slow: '500ms' }
    },
  },
  plugins: [],
}