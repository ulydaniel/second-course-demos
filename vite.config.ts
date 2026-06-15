import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages project site: https://existenze.github.io/second-course-university-dashboard/
const base =
  process.env.GITHUB_PAGES === "true" ? "/second-course-university-dashboard/" : "/";

export default defineConfig({
  plugins: [react()],
  base,
});
