# ArtifactVault — Merged Project (Django serves both API + Frontend)

> **If you already have a partly-set-up `museum`/`artifactvault-backend` folder
> with duplicate `manage.py`/`config`/`db.sqlite3` files:** delete that whole
> folder and use this one instead. Trying to patch two overlapping Django
> projects together is what caused the `Page not found (404)` error — this
> folder replaces both with a single, working project.

A single Django project for **ArtifactVault — Maharashtra Heritage Museum**.
One server, one command, one URL (`http://127.0.0.1:8000/`) — it serves both
the **REST API** (Django REST Framework + MongoDB) and the **frontend pages**
(`index.html`, `catalog.html`, `dashboard.html`, etc.) together, so there's
no separate frontend server and no CORS setup to worry about.

---

## 1. Where each required concept lives

| Concept       | Where |
|---------------|-------|
| **Dict**      | Every MongoDB document *is* a Python dict once read by PyMongo. See `apps/common/repository.py` (CRUD returns dicts), `apps/common/pagination.py` (`paginate_list` returns a result dict), `apps/common/threads.py` (`JOBS` dict tracking background job progress), `apps/artifacts/repository.py` (`stats()` builds a category-count dict via aggregation). |
| **CSV**       | `apps/common/csv_utils.py` (`dicts_to_csv_response`, `read_csv_text_rows`) used by `/api/artifacts/export/`, `/api/loans/export/` (download) and `/api/artifacts/import/` (upload). Also `apps/common/management/commands/seed_data.py`, which loads `data/artifacts_seed.csv` and `data/loans_seed.csv` into MongoDB. |
| **OOP**       | `apps/common/mongo.py` — `MongoConnection` is a Singleton (`__new__` override). `apps/common/repository.py` — `BaseRepository` is a base class; `ArtifactRepository`, `LoanRepository`, `CuratorRepository`, `SessionRepository` all **inherit** from it and add their own methods. `apps/common/authentication.py` and `permissions.py` subclass DRF's `BaseAuthentication` / `BasePermission`. `apps/common/threads.py` — `BackgroundTask` subclasses `threading.Thread`. |
| **Regex**     | `apps/common/validators.py` — email format, password strength, accession-number formats (`AV-####`, `LN-####`, `CUR-###`), and `sanitize_search_term()` which escapes user search input before it's used in a MongoDB `$regex` query. |
| **Threading** | `apps/common/threads.py` (background CSV-import job runner with a thread-safe dict + `Lock`), `apps/loans/background.py` (a daemon thread that periodically scans MongoDB and marks overdue loans — started from `apps/loans/apps.py`'s `ready()`), `apps/loans/notifications.py` (fire-and-forget notification thread when a loan is created), `apps/common/management/commands/check_mongo.py` (pings MongoDB concurrently from multiple threads). |
| **MongoDB**   | Every collection (`artifacts`, `loans`, `curators`, `sessions`) is plain PyMongo, no Django models. See `apps/common/mongo.py` + each app's `repository.py`. Aggregation pipeline example: `ArtifactRepository.stats()`. |
| **Django**    | Standard project layout (`config/settings.py`, `config/urls.py`), an `AppConfig.ready()` hook starting a background thread, and a custom `manage.py` management command (`seed_data`, `check_mongo`). |
| **DRF**       | `APIView` subclasses in every app's `views.py`, custom `Serializer` classes (not `ModelSerializer`, since there's no Django model), a custom `BaseAuthentication` (`MongoTokenAuthentication`) and `BasePermission` (`IsCurator`). |

---

## 2. Project layout

```
artifactvault-full/
├── config/                  Django project (settings, urls, wsgi/asgi)
├── apps/
│   ├── common/               Shared infra: Mongo connection, base repository,
│   │                         regex validators, CSV helpers, threading helpers,
│   │                         pagination, custom DRF auth/permission classes,
│   │                         management commands (seed_data, check_mongo)
│   ├── artifacts/            Public catalog + curator CRUD + CSV import/export
│   ├── loans/                Loan tracking + overdue background thread
│   ├── curators/             Register / login / logout / me (token auth)
│   └── frontend/             Serves the HTML pages in templates/ at clean URLs
│                             (/, /catalog.html, /dashboard.html, ...)
├── templates/                 The 6 HTML pages (plain HTML + vanilla JS, no
│                             Django template tags used)
├── static/
│   ├── css/style.css
│   └── js/                   data.js (offline fallback data), api.js (fetch
│                             wrapper, talks to /api/... on the same origin),
│                             script.js (page logic)
├── data/
│   ├── artifacts_seed.csv    Same 18 artifacts shown in the frontend
│   └── loans_seed.csv        Same 10 loan records shown in the frontend
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

**Why pages are served from `templates/` without Django's template engine:**
`apps/frontend/views.py` just reads each `.html` file's raw text and returns
it as an `HttpResponse` — it does **not** call Django's `render()`. This
keeps the pages working exactly as plain HTML/JS, with zero risk of Django's
`{{ }}` / `{% %}` parser misinterpreting anything inside the JavaScript.

**Why `css/style.css` and `js/script.js` still work unmodified:**
`config/urls.py` maps `/css/<file>`, `/js/<file>`, `/images/<file>` straight
to the matching folder under `static/`, so the existing relative paths
already used inside the HTML (`<link href="css/style.css">`,
`<script src="js/script.js">`) resolve correctly with no changes needed.

---

## 3. Setup

### 3.1 Install MongoDB

You need a running MongoDB server. Easiest options:
- **Local install**: install MongoDB Community Server for your OS and run `mongod`.
- **MongoDB Atlas (free cloud tier)**: create a free cluster at mongodb.com and copy
  its connection string.

### 3.2 Python environment

```bash
cd artifactvault-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.3 Configure environment variables

```bash
cp .env.example .env
# then edit .env and set MONGO_URI (and DJANGO_SECRET_KEY for production)
```

### 3.4 Run Django's own internal migrations

(Only needed for Django's built-in admin/auth/sessions tables in SQLite —
your actual artifact/loan/curator data lives in MongoDB, not here.)

```bash
python manage.py migrate
```

### 3.5 Seed MongoDB with sample data

```bash
python manage.py seed_data
# or, to wipe existing collections first:
python manage.py seed_data --reset
```

This creates 18 artifacts, 10 loans, and **one demo curator login**:

```
email:    curator@artifactvault.example.org
password: Heritage@123
```

### 3.6 (Optional) Verify MongoDB connectivity

```bash
python manage.py check_mongo
```

### 3.7 Run the server

```bash
python manage.py runserver
```

Everything is now live at **`http://127.0.0.1:8000/`** — one server, one port:

| Page | URL |
|---|---|
| Home | `http://127.0.0.1:8000/` |
| Public Catalog | `http://127.0.0.1:8000/catalog.html` |
| Artifact Details | `http://127.0.0.1:8000/artifact-details.html?id=AV-1001` |
| Curator Dashboard | `http://127.0.0.1:8000/dashboard.html` |
| Loan Tracking | `http://127.0.0.1:8000/loans.html` |
| About the Museum | `http://127.0.0.1:8000/about.html` |
| API root | `http://127.0.0.1:8000/api/...` (see section 4) |

On `dashboard.html`, sign in with the demo curator account created by
`seed_data` (see step 3.5):

```
email:    curator@artifactvault.example.org
password: Heritage@123
```


---

## 4. API reference

All responses are JSON. Endpoints marked 🔒 require a curator token:
`Authorization: Token <token>` (obtained from `/api/curators/login/`).

### Curators (auth)
| Method | URL | Description |
|---|---|---|
| POST | `/api/curators/register/` | Create a curator account |
| POST | `/api/curators/login/` | Returns `{ token, curator }` |
| POST 🔒 | `/api/curators/logout/` | Invalidate the current token |
| GET 🔒 | `/api/curators/me/` | Current curator's profile |
| GET 🔒 | `/api/curators/` | List all curators |

### Artifacts
| Method | URL | Description |
|---|---|---|
| GET | `/api/artifacts/?q=&category=&era=&material=&origin=&status=&page=&page_size=` | Search/filter/paginate (public — powers Home + Catalog pages) |
| POST 🔒 | `/api/artifacts/` | Create an artifact |
| GET | `/api/artifacts/<id>/` | `{ artifact, related }` (public — powers Details page) |
| PATCH 🔒 | `/api/artifacts/<id>/` | Partial update |
| DELETE 🔒 | `/api/artifacts/<id>/` | Delete |
| GET | `/api/artifacts/stats/` | Totals + per-category breakdown (public — powers Home stats + Dashboard bars) |
| GET 🔒 | `/api/artifacts/export/` | Download full catalog as CSV |
| POST 🔒 | `/api/artifacts/import/` | Upload a CSV (`file` field) → returns `{ job_id }` immediately, processed on a background thread |
| GET 🔒 | `/api/artifacts/import/status/<job_id>/` | Poll import progress |

### Loans
| Method | URL | Description |
|---|---|---|
| GET 🔒 | `/api/loans/?tab=Active\|Returned\|All&q=&page=&page_size=` | List/search loans |
| POST 🔒 | `/api/loans/` | Create a loan (fires an async notification thread) |
| GET 🔒 | `/api/loans/<id>/` | Loan detail |
| PATCH 🔒 | `/api/loans/<id>/` | Partial update |
| PATCH 🔒 | `/api/loans/<id>/return/` | Mark as Returned |
| GET 🔒 | `/api/loans/summary/` | `{ active, overdue, returned }` counts |
| GET 🔒 | `/api/loans/export/` | Download all loans as CSV |

A background thread (`apps/loans/background.py`) automatically flips any
`Active` loan whose `dueDate` has passed to `Overdue` every 5 minutes —
no manual action needed, this mirrors the "Overdue" badges already shown
on the frontend's Loan Tracking page.

---

## 5. Frontend ↔ Backend wiring (already done)

`static/js/api.js` defines `ApiClient`, a small `fetch()` wrapper with one
method per endpoint above (`ApiClient.getArtifacts()`, `ApiClient.login()`,
`ApiClient.createLoan()`, ...). Since the frontend and API are now served
from the same Django process, `API_BASE_URL` inside `api.js` is just the
relative path `/api` — no absolute host/port, no CORS configuration needed.

Currently only `dashboard.html` actively uses it (the curator login gate +
live stats/loan-summary widgets). The other pages (`index.html`,
`catalog.html`, etc.) still render from the static arrays in
`static/js/data.js`. If you want those pages to read live data from MongoDB
too, swap the relevant `ARTIFACTS` / `LOANS` array lookups in
`static/js/script.js` for the matching `ApiClient.getArtifacts(...)` /
`ApiClient.getLoans(...)` calls.

---

## 6. Notes / things to harden before real deployment

- `CORS_ALLOW_ALL_ORIGINS = True` in `config/settings.py` is no longer
  needed now that the frontend and API share an origin — fine to remove.
- Tokens in the `sessions` collection never expire — add a TTL index / expiry check for production.
- The background-job `JOBS` dict (`apps/common/threads.py`) is in-memory and per-process;
  use Celery + Redis (or store job state in MongoDB) if you run multiple server processes.
- `DJANGO_SECRET_KEY` in `.env.example` is a placeholder — generate a real one for production.
- `apps/frontend/views.py` serves raw HTML/JS as-is — fine for development;
  for production, serve `static/` via `collectstatic` + a real web server
  (nginx, WhiteNoise, etc.) instead of Django's dev server.

