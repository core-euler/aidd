# Docker Standard

docker-compose is the source of truth for runtime. Everything must work via `docker-compose up`.

## Project Structure

```
project/
├── docker-compose.yml        # Main (production-ready)
├── docker-compose.dev.yml    # Dev overrides (hot reload, debug)
├── docker-compose.test.yml   # Test environment
├── .env.example              # Variable template (committed)
├── .env                      # Actual values (gitignored)
├── services/
│   ├── bot/Dockerfile
│   ├── backend/Dockerfile
│   └── worker/Dockerfile
└── scripts/
    └── init-db.sh
```

## Required

- `docker-compose down -v && docker-compose up` works from scratch with zero manual steps
- All secrets and config via environment variables (`.env` → `env_file` / `environment`)
- `.env.example` with documented variables — committed to git
- `.env` — in `.gitignore`
- Health check on every service
- `depends_on` with `condition: service_healthy` (not just service name)
- Named volumes for persistent data (postgres, redis)
- Custom network (`driver: bridge`) for service isolation
- `restart: unless-stopped` on all services
- Specific image tags (not `latest`)
- Non-root user in Dockerfile
- Multi-stage build: builder stage for dependencies, production stage for code
- DB migrations run automatically on start (alembic upgrade head in CMD)

## Forbidden

- Hardcoded secrets in docker-compose.yml or Dockerfile
- `latest` tags in production
- `.env` in git
- `depends_on` without health conditions (race conditions)
- Containers running as root
- Data inside containers without volumes (lost on restart)
- Unnecessary exposed ports

## Standard Services

| Service | Image | Health Check | Volume |
|---------|-------|-------------|--------|
| PostgreSQL | `postgres:15-alpine` | `pg_isready -U $USER -d $DB` | `postgres_data:/var/lib/postgresql/data` |
| Redis | `redis:7-alpine` | `redis-cli --raw incr ping` | `redis_data:/data` |
| Bot | custom build | python ping script | — |
| Backend (FastAPI) | custom build | `curl -f http://localhost:8000/health` | — |
| Worker (Celery) | custom build | — | — |

## Dev vs Prod

- `docker-compose.yml` — production-ready base
- `docker-compose.dev.yml` — overrides: bind mounts for hot reload, `LOG_LEVEL=DEBUG`, `--reload` flags
- Dev start: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`
- Prod start: `docker-compose up -d`

## Health Endpoint (backend)

- `GET /health` — checks DB connection, returns `{"status": "healthy"}` or 503

## Pre-deploy Checklist

- [ ] Cold start works (`down -v && up`)
- [ ] All services have health checks
- [ ] `.env.example` is up to date
- [ ] `.env` is in `.gitignore`
- [ ] No hardcoded secrets
- [ ] Logs visible via `docker-compose logs`
- [ ] Migrations run automatically
- [ ] Volumes configured for persistent data
