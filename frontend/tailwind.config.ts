import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F4EFE4", card: "#FBF8F1", ink: "#1C2B21", muted: "#6B6F5E", line: "#D9CFB8", kraft: "#E6DAC0",
        forest: { DEFAULT: "#2F5D3A", dark: "#1F4029", light: "#E3EDDD" },
        leaf: "#7FA650", apple: "#C4452F", amber: "#D8A23A",
        grade: { A: "#2F7D43", B: "#B98A1E", C: "#CC6A1B", Reject: "#B3261E" },
      },
      fontFamily: {
        display: ["Fraunces", "Noto Sans Devanagari", "Georgia", "serif"],
        sans: ["DM Sans", "Noto Sans Devanagari", "system-ui", "sans-serif"],
        mono: ["DM Mono", "ui-monospace", "monospace"],
      },
      boxShadow: { tag: "0 1px 0 #fff inset, 0 10px 30px -12px rgba(47,93,58,.35), 0 2px 6px rgba(28,43,33,.08)" },
      keyframes: {
        scan: { "0%": { top: "0%" }, "50%": { top: "100%" }, "100%": { top: "0%" } },
        rise: { "0%": { opacity: "0", transform: "translateY(14px)" }, "100%": { opacity: "1", transform: "none" } },
        stamp: { "0%": { opacity: "0", transform: "scale(1.8) rotate(-18deg)" }, "70%": { transform: "scale(.94) rotate(-5deg)" }, "100%": { opacity: "1", transform: "scale(1) rotate(-7deg)" } },
      },
      animation: { scan: "scan 1.8s ease-in-out infinite", rise: "rise .5s ease both", stamp: ".55s cubic-bezier(.2,.9,.3,1) .15s both stamp" },
    },
  },
  plugins: [],
};
export default config;
