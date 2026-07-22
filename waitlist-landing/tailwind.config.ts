import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#FAFAF7",
        ink: "#15181A",
        stone: {
          light: "#EDEDE8",
          mid: "#8A8F8C",
        },
        accent: {
          DEFAULT: "#1E4D3B",
          dark: "#153A2C",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        widest2: "0.2em",
      },
    },
  },
  plugins: [],
};

export default config;
