import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "pitch-green": "#0f5233",
        "grass": "#0d7d3e",
        "goal-yellow": "#fbbf24",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
