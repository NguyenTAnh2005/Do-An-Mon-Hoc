/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        // MÀU CHÍNH HỆ THỐNG — teal, gợi công nghệ + môi trường, tách biệt với các màu trạng thái bên dưới
        primary: { DEFAULT: '#66BB6A', hover: '#57A55C' },

        // MÀU TRẠNG THÁI (semantic) — dùng cho online/offline, mức đầy thùng, xác nhận đúng/sai...
        success: { DEFAULT: '#22C55E', hover: '#16A34A' }, // online, an toàn, xác nhận đúng
        danger:  { DEFAULT: '#EF4444', hover: '#DC2626' }, // offline, đầy thùng, xác nhận sai
        warning: { DEFAULT: '#F59E0B', hover: '#D97706' }, // sắp đầy, cần chú ý

        light: {
          bg: '#F7F7F6',
          surface: '#FFFFFF',
          text: '#1F1F1D',
          muted: '#6E6E6B'
        },
        dark: {
          bg: '#16171A',
          surface: '#1E1F23',
          text: '#F2F2F0',
          muted: '#93938E'
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