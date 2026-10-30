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
        // MÀU CHÍNH — teal thật (hue ~174°), tách hẳn khỏi success
        primary: { DEFAULT: '#0D9488', hover: '#0F766E' },

        // MÀU TRẠNG THÁI — 3 gam tách biệt: green / rose / amber
        success: { DEFAULT: '#16A34A', hover: '#15803D' },
        danger:  { DEFAULT: '#E11D48', hover: '#BE123C' },
        warning: { DEFAULT: '#F59E0B', hover: '#D97706' },

        light: {
          bg:      '#F5F8F8',   // trắng ngả teal rất nhẹ
          surface: '#FFFFFF',
          text:    '#0F1A1A',   // đen ngả teal nhẹ
          muted:   '#5B6E6C'    // xám teal
        },
        dark: {
          bg:      '#0F1416',   // đen ngả teal
          surface: '#181E20',   // surface teal nhẹ
          text:    '#F0F4F3',   // trắng teal
          muted:   '#8AA19E'    // xám teal sáng
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