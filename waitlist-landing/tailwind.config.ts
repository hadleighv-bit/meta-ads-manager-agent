import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // LaLa Labs palette — sign orange on café teal
        paper: "#FBF9F4",
        ink: "#17383B",
        stone: {
          light: "#EDEBE3",
          mid: "#84908D",
        },
        accent: {
          DEFAULT: "#EFA33C", // sign orange: buttons, fills, marks
          dark: "#D68A25", // hover
          deep: "#A05F10", // small text on light grounds (AA contrast)
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        logo: ["var(--font-logo)", "cursive"],
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
