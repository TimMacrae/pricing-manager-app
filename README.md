# Pricing Learning Platform

A **full internal pricing analytics platform** designed to simulate a real SAP-like pricing environment with automation, ETL, anomaly detection, ML scoring, and a React frontend.

This project mirrors how an internal pricing team would:

- Analyze thousands of products
- Detect pricing errors
- Compare competitors
- Run nightly jobs
- Track job executions
- Expose results via a web UI

---

## Tech Stack

### Backend

- Python 3.12
- Django + Django REST Framework
- Celery (async job processing)
- Redis (broker + result backend)
- MySQL 8
- pandas / NumPy
- scikit-learn (IsolationForest)
- TensorFlow (ready for later ML)

### Frontend

- React (Vite)
- React Query
- Axios
- Tailwind / shadcn (optional UI layer)

### Infrastructure

- Docker & Docker Compose
- uv (Python dependency manager)

---

## High-Level Architecture

### Components

| Component          | Description                                                                  |
| ------------------ | ---------------------------------------------------------------------------- |
| React UI (Vite)    | Internal web UI for the pricing team                                         |
| Django/DRF API     | Authentication, orchestration, configuration, job tracking, API endpoints    |
| Celery Worker      | Heavy lifting (ETL, feature engineering, anomaly scoring, later ML training) |
| Celery Beat        | Scheduling (nightly pipelines)                                               |
| MySQL Source DB    | SAP-like raw data (materials, daily prices, competitor snapshots)            |
| MySQL Analytics DB | Derived tables (features, anomalies, JobRun tracking)                        |
| Redis              | Broker + result backend for Celery                                           |

### Data Flow

```
React → (REST) → Django API
Django API → (enqueue) → Celery Worker
Celery Worker → read source_db → transform/score → write analytics_db
React → query Django API → read from analytics outputs
```

---

## Repository Structure

```
pricing-learning/
├── backend/
│   ├── config/                      # Django project
│   ├── pricing/                     # Django app
│   │   ├── analytics/               # feature engineering helpers
│   │   ├── ml/                      # anomaly model helpers
│   │   ├── services/                # query services (anomalies, etc.)
│   │   ├── tasks.py                 # Celery tasks
│   │   ├── models.py                # JobRun model etc.
│   │   └── ...
│   ├── scripts/
│   │   └── seed_source_db.py        # seed SAP-like dataset
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   └── ...
│   └── package.json
├── docker-compose.yml
├── .env                             # local environment vars (not committed)
└── README.md
```

---

## Services & Ports

| Service         | Container         | Host Port | Notes                        |
| --------------- | ----------------- | --------: | ---------------------------- |
| Django API      | `backend`         |      8000 | http://localhost:8000        |
| Django Admin    | `backend`         |      8000 | http://localhost:8000/admin/ |
| Frontend        | local node        |      5173 | http://localhost:5173        |
| MySQL Source    | `mysql_source`    |      3307 | Schema: `source_db`          |
| MySQL Analytics | `mysql_analytics` |      3308 | Schema: `analytics_db`       |
| Redis           | `redis`           |      6379 | Celery broker/result backend |
| Celery Worker   | `celery_worker`   |         — | ETL/ML execution             |
| Celery Beat     | `celery_beat`     |         — | Scheduling                   |

---

## Environment Variables

Create a file named `.env` next to `docker-compose.yml`:

```env
# Django
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_SECRET_KEY=change-me-to-a-long-random-string
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL credentials
MYSQL_USER=app
MYSQL_PASSWORD=app
MYSQL_ROOT_PASSWORD=root

# DB names
MYSQL_SOURCE_DB=source_db
MYSQL_ANALYTICS_DB=analytics_db

# Docker service names
MYSQL_SOURCE_HOST=mysql_source
MYSQL_ANALYTICS_HOST=mysql_analytics

# Redis
REDIS_HOST=redis
```

> **Important:** Add `.env` to `.gitignore`

---

## Docker

### Build & Start

```bash
docker compose up -d --build
```

### Check running services

```bash
docker compose ps
```

### Stop services (keep DB data)

```bash
docker compose down
```

### Reset everything (deletes DB volumes)

> ⚠️ This removes MySQL volumes (all data)

```bash
docker compose down -v
docker compose up -d --build
```

### Rebuild backend only

```bash
docker compose build backend
docker compose restart backend celery_worker celery_beat
```

### Force rebuild backend (no cache)

Use this if dependencies don't show up in the container:

```bash
docker compose build --no-cache backend
docker compose restart backend celery_worker celery_beat
```

---

## Logs & Monitoring

### View logs

```bash
docker compose logs -f backend
docker compose logs -f celery_worker
docker compose logs -f celery_beat
docker compose logs -f mysql_source
docker compose logs -f mysql_analytics
docker compose logs -f redis
```

### Exec into containers

```bash
docker compose exec backend bash
docker compose exec mysql_source bash
docker compose exec mysql_analytics bash
```

---

## Backend Setup (Django)

### Run migrations

```bash
docker compose exec backend bash -lc "uv run python manage.py migrate"
```

### Create superuser (Admin login)

```bash
docker compose exec backend bash -lc "uv run python manage.py createsuperuser"
```

### Django admin

Open: http://localhost:8000/admin/

### Health endpoint

```bash
curl http://localhost:8000/api/health/
```

Expected response:

```json
{ "status": "ok" }
```

---

## Dependency Management (uv)

### Sync dependencies

```bash
docker compose exec backend bash -lc "uv sync"
```

### Create a lock file

```bash
docker compose exec backend bash -lc "uv lock"
```

### Add new dependency workflow

1. Add package to `backend/pyproject.toml`
2. Install it:

```bash
docker compose exec backend bash -lc "uv sync"
docker compose restart backend celery_worker celery_beat
```

### Verify a dependency exists

```bash
docker compose exec backend bash -lc "python -c 'import pymysql; print(pymysql.__version__)'"
```

---

// ...existing code...

## Development Workflow (Git)

// ...existing code...

---

## Testing

### Run all tests

```bash
docker compose exec backend bash -lc "uv run python manage.py test --settings=config.settings_test"
```

### Run tests for a specific app

```bash
docker compose exec backend python manage.py test pricing
docker compose exec backend python manage.py test task_manager
```

### Run a specific test class

```bash
docker compose exec backend python manage.py test pricing.tests.TestAnomalyDetection
```

### Run a specific test method

```bash
docker compose exec backend python manage.py test pricing.tests.TestAnomalyDetection.test_price_spike_detection
```

### Run tests with verbose output

```bash
docker compose exec backend python manage.py test -v 2
```

### Run tests locally (without Docker)

```bash
cd backend
uv run python manage.py test
```

---

## Database Tooling (MySQL Workbench)

### Connect to Source DB

| Setting  | Value                                    |
| -------- | ---------------------------------------- |
| Host     | 127.0.0.1                                |
| Port     | 3307                                     |
| User     | root                                     |
| Password | `${MYSQL_ROOT_PASSWORD}` (default: root) |
| Schema   | source_db                                |

### Connect to Analytics DB

| Setting  | Value                                    |
| -------- | ---------------------------------------- |
| Host     | 127.0.0.1                                |
| Port     | 3308                                     |
| User     | root                                     |
| Password | `${MYSQL_ROOT_PASSWORD}` (default: root) |
| Schema   | analytics_db                             |

---

## Seed the Source Database

This creates a realistic training dataset:

- 60 products (>= 50)
- Daily prices for multiple customers/sales orgs
- Competitor prices
- Intentional irregularities: spikes, too-low prices, margin collapse, competitor undercut events

### Run seed script

```bash
docker compose exec backend bash -lc "uv run python scripts/seed_source_db.py"
```

### Verify row counts

```bash
docker compose exec mysql_source mysql -u root -p -e \
"USE source_db; \
 SELECT COUNT(*) AS materials FROM materials; \
 SELECT COUNT(*) AS daily_prices FROM daily_prices; \
 SELECT COUNT(*) AS competitor_prices FROM competitor_prices;"
```

---

## ETL & Job Automation

### Run ETL manually

```bash
curl -X POST http://localhost:8000/api/etl/run/
```

### Check job history (API)

```bash
curl http://localhost:8000/api/jobs/
curl http://localhost:8000/api/jobs/latest/
```

### Check job runs (Admin)

http://localhost:8000/admin/ → Job Runs

---

## Anomaly Detection

The pipeline computes:

- Cost & margin %
- 7-day price change %
- 14-day volatility
- Competitor min price + delta %
- Rule-based flags: `NEGATIVE_MARGIN`, `LOW_MARGIN`, `PRICE_SPIKE`, `COMPETITOR_UNDERCUT`
- ML score (IsolationForest)

Results go to: `analytics_db.pricing_anomalies`

---

## Anomalies API Endpoints

### List anomalies

```bash
curl "http://localhost:8000/api/anomalies/?limit=20"
```

### Filter by reason

```bash
curl "http://localhost:8000/api/anomalies/?reason=PRICE_SPIKE&limit=20"
```

### Filter by SKU

```bash
curl "http://localhost:8000/api/anomalies/?sku=SKU0007&limit=50"
```

### Filter by date range

```bash
curl "http://localhost:8000/api/anomalies/?dt_from=2025-11-01&dt_to=2025-12-31&limit=200"
```

### List available reasons + counts

```bash
curl "http://localhost:8000/api/anomalies/reasons/"
```

### SKU detail (timeseries + anomalies)

```bash
curl "http://localhost:8000/api/anomalies/SKU0007/?days=60"
```

---

## Frontend Setup (React)

### Install dependencies and start dev server

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

---

## Common Commands Cheat Sheet

| Action           | Command                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------ |
| Start all        | `docker compose up -d --build`                                                             |
| Stop all         | `docker compose down`                                                                      |
| Reset everything | `docker compose down -v && docker compose up -d --build`                                   |
| Rebuild backend  | `docker compose build backend && docker compose restart backend celery_worker celery_beat` |
| Watch logs       | `docker compose logs -f backend`                                                           |
| Seed data        | `docker compose exec backend bash -lc "uv run python scripts/seed_source_db.py"`           |
| Run ETL manually | `curl -X POST http://localhost:8000/api/etl/run/`                                          |

---

## Troubleshooting

### Backend server running but not reachable

Check port mapping:

```bash
docker compose ps
```

You should see: `0.0.0.0:8000->8000/tcp`

### CORS errors in browser

- Ensure `corsheaders` is installed and enabled
- Ensure `CORS_ALLOWED_ORIGINS` includes `http://localhost:5173`
- Restart backend: `docker compose restart backend`

### Task triggers but nothing happens

Check worker logs:

```bash
docker compose logs -f celery_worker
docker compose logs -f redis
```

### ModuleNotFoundError after adding dependency

```bash
docker compose exec backend bash -lc "uv sync"
docker compose build --no-cache backend
docker compose restart backend celery_worker celery_beat
```

### MySQL auth error (caching_sha2_password)

If using PyMySQL with MySQL8 auth you need cryptography installed. Verify:

```bash
docker compose exec backend bash -lc "python -c 'import cryptography; print(cryptography.__version__)'"
```

---

## Development Workflow (Git)

### Branching

- `main` → stable
- `feature/<name>` → feature work

```bash
git checkout -b feature/anomaly-detection-v1
```

### Commit discipline

- Small commits
- One logical change per commit
- Run ETL and check anomalies after changes

---

## Roadmap

- [ ] React Anomalies page (filters + table + detail panel)
- [ ] SKU drill-down charts (price vs competitor + anomaly overlay)
- [ ] Export anomalies to Excel
- [ ] Alerts (Slack/email) on severe anomalies
- [ ] Model versioning & retraining schedule
- [ ] Permissions / roles (pricing manager vs analyst)
- [ ] Feature store patterns (optional)

---

## Philosophy

This project intentionally mirrors:

- SAP-style data complexity
- Internal pricing workflows
- Heavy automation & ETL
- Explainable rules + ML scoring
- Maintainable architecture for small teams

It is designed to be a realistic foundation for an internal pricing platform.
