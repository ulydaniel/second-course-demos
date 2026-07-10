# University Dashboard DEMO

Standalone mockup for sharing Second Course's university admin dashboard concept while we develop it. **Not** the production marketing site or app — sample SDSU data only.

## Local development (frontend + backend)

Week 1 connects the React dashboard to a FastAPI server. Run both in separate terminals.

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend (Vite + React)

```bash
npm install
npm run dev
```

Open http://localhost:5173/dashboard — the dashboard loads data from `/api/*` (proxied to port 8000).

To verify the connection, edit a value in `backend/app/services/mock_data.py` (e.g. `SUMMARY["total_posts"]`), save, and refresh the dashboard.

## Frontend only (static demo)

If the backend is not running, the dashboard falls back to built-in sample data from `src/data.ts`.

```bash
npm install
npm run dev
```

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

> GitHub Pages hosts the frontend only. The FastAPI backend needs separate hosting when you go beyond local development.

## Project layout

```
second-course-demos/
├── src/                 # React dashboard (frontend)
├── backend/             # FastAPI API (see backend/README.md)
└── resources/           # PRD, milestones, metrics spreadsheet (local only)
```

## Exports (demo)

- **Download all data (.xlsx)** — multi-sheet workbook with sample data
- **Posts only (.csv)** — post-level CSV
- **Export charts (PNG/SVG)** — zip of dashboard charts

## Brand

Uses Second Course cream palette, Worktalk + Lota Grotesque fonts, and logo assets bundled in `public/`.
