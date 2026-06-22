import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages project site: https://existenze.github.io/second-course-demos/
const base = process.env.GITHUB_PAGES === "true" ? "/second-course-demos/" : "/";

export default defineConfig({
  plugins: [react()],
  base,
});
