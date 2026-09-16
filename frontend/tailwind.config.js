/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0a0d14",
        surface: "#111622",
        "surface-raised": "#182030",
        border: "#232c40",
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
        academic: {
          glow: "#3b82f6",
          badge: "#1d4ed8",
        },
        engineering: {
          glow: "#10b981",
          badge: "#047857",
        },
        commerce: {
          glow: "#f59e0b",
          badge: "#b45309",
        },
        management: {
          glow: "#8b5cf6",
          badge: "#6d28d9",
        },
        law: {
          glow: "#ec4899",
          badge: "#be185d",
        },
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        glow: "0 0 25px -5px rgba(99, 102, 241, 0.3)",
        "glow-emerald": "0 0 25px -5px rgba(16, 185, 129, 0.3)",
        "glow-blue": "0 0 25px -5px rgba(59, 130, 246, 0.3)",
      },
    },
  },
  plugins: [],
}
