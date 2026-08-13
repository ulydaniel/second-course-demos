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

## Firestore metrics

Overview / Posts / Impact read live analytics from Firestore when a client can be
built, and fall back to `mock_data.py` otherwise (`METRICS_SOURCE=auto|firestore|mock`).

- `services/firestore_client.py` — emulator (anonymous creds via `FIRESTORE_EMULATOR_HOST`)
  or a service account (`FIREBASE_CREDENTIALS_PATH`). Normalises the retired
  `southwestern` → `swccd` campus id.
- `services/metrics_cache.py` — caches the mirrored collections (`posts`, `claims`,
  `post_views`, `users`, `campuses`) and attaches `on_snapshot` listeners so new
  posts / weight / savings show up without a redeploy (TTL poll as fallback).
- `services/firestore_metrics.py` — computes KPIs per DATA_CONTRACT §5/§6: claim rate
  over unique viewers, lbs diverted, student meal value, hauling (`$/lb`) and CO₂e
  from per-campus factors. Read-only — the analytics collections are never written.

Demographics are exposed only as privacy-safe aggregates at
`GET /api/impact/demographics` (campus-scoped, small cells below `minCellSize`
suppressed, no student PII).

Verify against the handoff emulator:

```powershell
# In the dashboard-handoff folder: npm run emulator ; npm run seed
$env:METRICS_SOURCE = "firestore"
$env:FIRESTORE_EMULATOR_HOST = "localhost:8080"
$env:FIRESTORE_PROJECT_ID = "demo-second-course"
uvicorn app.main:app --reload --port 8000
```

SDSU year totals should read ~260 posts / 2,389 claims / ~1,529 lbs / ~$14,962 meal
value / ~$138 hauling (not the mock 847 / 3,420 / $4,280).

## Next steps

1. Replace `mock_data.py` reads with SQL queries via `models/` + `db/session.py`
2. Add date-range query params to all list endpoints
3. Add auth middleware + AllowList role checks (Administrator / Editor / Viewer)
4. Point frontend `Dashboard.tsx` at `/api/*` instead of `src/data.ts`
