# University Dashboard API

FastAPI backend for the Second Course University Dashboard. Matches the PRD stack:
**React + FastAPI + SQL + TypeScript** (frontend stays in `src/`, backend here).

## Quick start

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

## Layout

```
backend/
├── app/
│   ├── main.py          # FastAPI app + CORS
│   ├── config.py        # env vars (PORT, DATABASE_URL, …)
│   ├── routes/          # HTTP layer — one module per dashboard tab
│   ├── services/        # business logic + metric calculations
│   ├── schemas/         # Pydantic response models (API contracts)
│   ├── models/          # SQLAlchemy tables (stub — add when DB is live)
│   ├── db/              # session factory
│   └── services/mock_data.py  # demo data from src/data.ts
├── requirements.txt
└── .env.example
```

## Request flow

```
Browser → GET /api/overview → routes/overview.py → services/overview.py → mock_data (→ SQL later)
```

## Endpoints (demo)

| Method | Path | Dashboard tab |
|--------|------|---------------|
| GET | `/api/health` | — |
| GET | `/api/overview` | Overview |
| GET | `/api/posts` | Posts & Claims |
| GET | `/api/demand` | Demand Map |
| GET | `/api/staff` | Staff Activity |
| GET | `/api/impact` | Impact |

Exports remain client-side for now (`src/export.ts`); a future `routes/exports.py` can
generate `.xlsx` / `.csv` server-side per PRD section 5.

## Metrics mapping

See `resources/Second Course Data Metrics - Sheet1.csv` for how collected app data
(student users, food posters) maps to dashboard sections. Stub table plans live in
`app/models/__init__.py`.

## Next steps

1. Replace `mock_data.py` reads with SQL queries via `models/` + `db/session.py`
2. Add date-range query params to all list endpoints
3. Add auth middleware + AllowList role checks (Administrator / Editor / Viewer)
4. Point frontend `Dashboard.tsx` at `/api/*` instead of `src/data.ts`
