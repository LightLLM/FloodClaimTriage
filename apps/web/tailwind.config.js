/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        card: '#1f2937',
        border: '#334155',
        primary: '#38bdf8',
        p1: '#ef4444',
        p2: '#f59e0b',
        p3: '#10b981',
        text: '#e5e7eb',
        'text-muted': '#94a3b8',
      },
    },
  },
  plugins: [],
}
