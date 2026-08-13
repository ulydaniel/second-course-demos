# Session Report: Firestore Demographics + Posts / Weight / Savings

| | |
|---|---|
| **Date** | Thursday, August 13, 2026 |
| **Branch** | `feature/student-demographics` |
| **Base** | `main` @ `c6e99ce` (identical at session start; all work is still **uncommitted**) |
| **Session** | [Firestore demographics ingest](1bcabd3a-7dec-4c29-aee0-27c79497d99e) |
| **Scope decision** | Dashboard ingest only — **no** student signup UI in this repo |

---

## 1. Goal

Wire the university dashboard to **Firestore as the source of truth** for:

1. **Posts** (counts, claim rates, post lists)
2. **Weight** (lbs diverted from claims)
3. **Saving costs** (student meal value + waste hauling dollars)
4. **Student demographics** as **privacy-safe campus aggregates** only

Student signup (major, demographic fields, etc.) already lives in the production mobile app and is stored on `users/{uid}.demographics` per the handoff `DATA_CONTRACT.md`. This repo **reads** that data with the Admin/Client SDK, never writes it back, and never exposes individual students.

---

## 2. What was decided (planning)

| Question | Decision |
|---|---|
| Where do students answer signup demographics? | Production mobile app (not this demo Portal) |
| What does this repo do? | Backend ingest + Impact tab aggregates |
| Privacy model | Server-side Admin SDK only; aggregates + `minCellSize` suppression; no uid/email/displayName |
| Live updates | In-memory cache + Firestore `on_snapshot` listeners (TTL poll fallback) |
| Offline / missing campus | Fall back to existing `mock_data.py` |

---

## 3. Architecture

```
Firestore
  campuses / posts / claims / post_views / users
        │
        ▼
firestore_client.py  ─── emulator or service account
        │
        ▼
metrics_cache.py     ─── TTL + on_snapshot invalidation
        │
        ▼
firestore_metrics.py ─── KPIs + k-anonymous demographics
        │
        ▼
metrics.py           ─── Firestore if available, else mock_data
        │
   ┌────┼────┐
overview  posts  impact (+ GET /demographics)
        │
        ▼
Dashboard Impact tab (KPIs + DemographicsPanel)
```

---

## 4. New files

| File | Role |
|---|---|
| `backend/app/services/firestore_client.py` | Lazy singleton Firestore client; emulator (anonymous creds) vs cloud (service account / ADC); `southwestern` → `swccd` campus alias |
| `backend/app/services/metrics_cache.py` | Thread-safe in-memory cache of mirrored collections; `on_snapshot` on `posts` / `claims` / `users`; TTL refresh |
| `backend/app/services/firestore_metrics.py` | Campus-scoped KPI computation (DATA_CONTRACT §5/§6) + demographic aggregation with `minCellSize` |
| `backend/app/services/metrics.py` | Single selector: Firestore snapshot when available, else `mock_data` (injects approximate `meal_value` for mock) |

---

## 5. Modified files

### Backend

| File | Change |
|---|---|
| `backend/app/config.py` | Added `metrics_source`, `firestore_project_id`, `firestore_emulator_host`, `firestore_cache_ttl_seconds` |
| `backend/.env.example` | Documented `METRICS_SOURCE`, `FIRESTORE_*` vars *(file is gitignored in this repo)* |
| `backend/requirements.txt` | Added `google-cloud-firestore>=2.16.0` (`firebase-admin` left optional/commented for Auth path) |
| `backend/app/schemas/dashboard.py` | `SummaryKpis.meal_value` / `mealValue`; new `DemographicBucket` + `DemographicsResponse` |
| `backend/app/services/overview.py` | Uses `metrics.get_snapshot` instead of `mock_data` directly |
| `backend/app/services/posts.py` | Same |
| `backend/app/services/impact.py` | Same + new `get_demographics()` |
| `backend/app/routes/impact.py` | New `GET /api/impact/demographics` (campus-scoped via `dashboard_scope`) |
| `backend/README.md` | New **Firestore metrics** section (setup, formulas, verify steps, expected SDSU totals) |

### Frontend

| File | Change |
|---|---|
| `src/api.ts` | `mealValue` on `SummaryKpis`; `DemographicBucket` / `DemographicsResponse` types; `fetchDemographics()` |
| `src/data.ts` | Mock `SUMMARY.mealValue` |
| `src/pages/Dashboard.tsx` | Impact tab KPI row (posts / lbs / meal value / hauling); `DemographicsPanel` replacing “future” placeholder |

### Repo hygiene

| File | Change |
|---|---|
| `.gitignore` | Ignore `workspaces/*` |

---

## 6. Features implemented

### 6.1 Firestore client & config

- **Modes**: `METRICS_SOURCE=auto|firestore|mock`
  - `auto` — use Firestore when emulator host or credentials exist, else mock
  - `firestore` — prefer Firestore (still falls back to mock on connection/compute failure)
  - `mock` — never touch Firestore
- Emulator: `FIRESTORE_EMULATOR_HOST` + project `demo-second-course` (anonymous credentials)
- Cloud: `FIREBASE_CREDENTIALS_PATH` / `GOOGLE_APPLICATION_CREDENTIALS` / application-default credentials
- Campus id bridge: dashboard tenant `southwestern` ↔ Firestore `swccd`
- Read-only mirror of: `campuses`, `posts`, `claims`, `post_views`, `users`

### 6.2 Live metrics refresh

- Cache TTL (default **30s** via `FIRESTORE_CACHE_TTL_SECONDS`)
- `on_snapshot` listeners mark cache dirty when posts/claims/users change so the next dashboard request refetches without a redeploy
- If listeners fail to attach, TTL polling alone still works

### 6.3 Metric formulas (contract-aligned)

| Dashboard need | Source / formula |
|---|---|
| Posts | Count of non-`HIDDEN` posts in period |
| Claims / claim rate | Claims in period ÷ `sum(posts.viewCount)` |
| Weight (lbs diverted) | `sum(claims.estimatedWeightLbs)`; keyword backfill only if stamp missing |
| Student meal value | `sum(claims.estimatedValue)`; same backfill rule |
| Hauling savings | `lbs × campuses.haulingUsdPerLb` (default **$0.09/lb**) |
| tCO₂e | `lbs × campuses.kgCo2ePerLbFood / 1000` |
| Avg first claim | Mean of per-post min `claimDelaySeconds` |
| Period filters | Academic year / month / week in campus timezone |

Also rebuilt for Overview/Posts/Impact charts: month series, hour-of-day bins, top locations, per-post records, waste/climate series.

**Fallback**: campuses with no mirrored posts (e.g. `csulb`) or Firestore unavailable → existing mock snapshot so the demo still boots.

### 6.4 Privacy-safe demographics

New endpoint:

```http
GET /api/impact/demographics
```

- Approved campus-scoped callers only (`dashboard_scope`)
- Aggregates `users.demographics` by campus
- **Never returns** uid, email, displayName, push tokens, or individual answers
- Drops buckets below campus `minCellSize` (k-anonymity; typically 5–10)
- **Auto-discovers** any demographics key present in data so new signup questions appear without a code change
- Response shape: `respondentCount`, `userCount`, `minCellSize`, `suppressed`, `fields: { [key]: [{label, count}] }`

### 6.5 Impact tab UI

Replaced the “Student demographics (future)” callout with:

1. **Four KPI cards**: food posts, lbs diverted, student meal value ($), waste hauling savings ($)
2. Existing waste / climate charts retained
3. **`DemographicsPanel`**: loads `/api/impact/demographics`, shows respondent fraction, privacy note, and horizontal bar breakdowns (preferred order: year, major, housing, foodWorry, firstGen, calfresh; unknown keys humanized and appended)

Portal signup UI was **not** changed (staff-only by design).

---

## 7. Diff summary (working tree)

Uncommitted as of report time:

```
Modified (12):
  .gitignore
  backend/README.md
  backend/app/config.py
  backend/app/routes/impact.py
  backend/app/schemas/dashboard.py
  backend/app/services/impact.py
  backend/app/services/overview.py
  backend/app/services/posts.py
  backend/requirements.txt
  src/api.ts
  src/data.ts
  src/pages/Dashboard.tsx

Untracked (4):
  backend/app/services/firestore_client.py
  backend/app/services/firestore_metrics.py
  backend/app/services/metrics.py
  backend/app/services/metrics_cache.py

Approx. tracked diff: +291 / −20 lines (plus ~29KB in new service modules)
```

---

## 8. Verification done in session

| Check | Result |
|---|---|
| `python -m py_compile` on changed backend modules | OK |
| Frontend lints on `Dashboard.tsx` / `api.ts` / `data.ts` | Clean |
| `npx tsc --noEmit` | Pre-existing `replaceAll` errors in CSV export only; new Impact/demographics code type-clean |

### How to verify against the handoff emulator

```powershell
# In dashboard-handoff:
npm run emulator
npm run seed

# In backend/.env (or session env):
METRICS_SOURCE=firestore
FIRESTORE_EMULATOR_HOST=localhost:8080
FIRESTORE_PROJECT_ID=demo-second-course

uvicorn app.main:app --reload --port 8000
```

Expected SDSU academic-year ballpark (not mock numbers):

| Metric | Expected (approx.) | Old mock |
|---|---|---|
| Posts | ~260 | 847 |
| Claims | ~2,389 | — |
| Lbs diverted | ~1,529 | 3,420 |
| Meal value | ~$14,962 | — |
| Hauling | ~$138 | $4,280 |

---

## 9. Explicitly out of scope (this session)

- Student onboarding / signup UI in this demo app
- Writing demographics or analytics back to Firestore
- Mirroring raw `users` into SQLite/Postgres
- Moving Demand / Staff tabs off mock data
- Enabling Firebase Auth (`firebase-admin` still optional)
- Git commit / PR (changes remain local on `feature/student-demographics`)

---

## 10. Follow-ups / next steps

1. **Commit** the working tree on `feature/student-demographics` and open a PR against `main`
2. Install deps: `pip install -r backend/requirements.txt` (needs `google-cloud-firestore`)
3. Run end-to-end against the handoff emulator and confirm SDSU totals
4. For production cloud: unset emulator host; set `FIREBASE_CREDENTIALS_PATH` (or ADC) + real `FIRESTORE_PROJECT_ID`
5. Optionally wire Demand/Staff to the same Firestore snapshot later
6. Note: `backend/.env.example` is currently listed in `.gitignore` — consider un-ignoring it so env docs stay versioned

---

## 11. Plan todos (all completed)

| ID | Todo | Status |
|---|---|---|
| `firestore-client` | Client + env + campus alias + dependency | Done |
| `metrics-ingest` | Posts / lbs / mealValue / hauling / claim rate + cache invalidation | Done |
| `privacy-demos` | Aggregate demographics + `GET /api/impact/demographics` | Done |
| `wire-routes` | Overview / posts / impact → metrics selector + `mealValue` | Done |
| `impact-ui` | Impact KPIs + demographics panel | Done |
