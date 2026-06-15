/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["LotaGrotesqueAlt3SemiBold", "system-ui", "sans-serif"],
        display: ["Worktalk", "system-ui", "sans-serif"],
      },
      colors: {
        cream: "#EDDBC3",
        black: "#18181b",
        gray: "#6b7280",
        scGreen: "#6EC100",
        scPink: "#FD8DFD",
        scOrange: "#FF6E02",
        scRed: "#FE0000",
        scYellow: "#FFDE00",
        brandGreen: "#008B48",
      },
    },
  },
  plugins: [],
};
