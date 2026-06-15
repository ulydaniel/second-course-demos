# University Dashboard DEMO

Standalone mockup for sharing Second Course's university admin dashboard concept while we develop it. **Not** the production marketing site or app — sample SDSU data only.

## Local development

```bash
npm install
npm run dev
```

Open http://localhost:5173

## Build

```bash
npm run build
```

For GitHub Pages:

```bash
GITHUB_PAGES=true npm run build
```

## Deploy to GitHub Pages

1. Create a new GitHub repo (suggested name: `second-course-university-dashboard`).
2. Push this folder to `main`.
3. In repo **Settings → Pages**, set source to **GitHub Actions**.
4. The included workflow deploys on every push to `main`.
5. Live URL: `https://<your-username>.github.io/second-course-university-dashboard/`

## Exports (demo)

- **Download all data (.xlsx)** — multi-sheet workbook with sample data
- **Posts only (.csv)** — post-level CSV
- **Export charts (PNG/SVG)** — zip of dashboard charts

## Brand

Uses Second Course cream palette, Worktalk + Lota Grotesque fonts, and logo assets bundled in `public/`.
