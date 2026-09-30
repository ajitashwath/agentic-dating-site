import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ember: "#fc5000",
        plasma: "#524ae9",
        sulfur: "#f5f28e",
        limestone: "#f7f6f2",
        pumice: "#e2e2df",
        obsidian: "#070607",
      },
    },
  },
  plugins: [],
};
export default config;
