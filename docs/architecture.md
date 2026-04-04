# Architecture

## Overview

A production-containerized FastAPI service running as a non-root process inside a minimal multi-stage Docker image, composed locally with a PostgreSQL dependency and shipped via an automated CI pipeline.

## System Diagram

```text
Developer
   │
   ▼
+-------------------------------+
| docker compose up             |
|   ┌────────────────────────┐  |
|   │  app (containerize-app)|  |   Port 8000
|   │  - non-root (uid 10001)|◄─┼──── external traffic
|   │  - read-only fs        |  |
|   │  - cap_drop: ALL       |  |
|   │  - healthcheck /health |  |
|   └────────────┬───────────┘  |
|                │ postgres://   |
|   ┌────────────▼───────────┐  |
|   │  db (postgres:16-alpine)|  |   (internal network only)
|   │  - named volume        |  |
|   │  - healthcheck         |  |
|   └────────────────────────┘  |
+-------------------------------+

Shared network: containerize-app-net (bridge)
Persistent storage: containerize-app-pgdata (named volume)
```

## CI/CD Pipeline

```text
git push (master / PR)
   │
   ▼
[lint-test]     ruff + pytest
   │
   ▼
[build-scan]    docker build → Trivy scan (HIGH/CRITICAL blocking)
   │
   ▼ (master only)
[push]          tag by SHA + semver → GHCR private registry
```

## Image Build Strategy (Multi-Stage)

```text
Stage 1: builder (python:3.12-slim)
  ├── Install gcc (wheel compilation only)
  └── pip install --prefix=/install requirements.txt

Stage 2: runtime (python:3.12-slim)
  ├── Create non-root user (uid 10001)
  ├── COPY --from=builder /install  ← packages only, no build tools
  ├── COPY app/                      ← source only
  └── USER appuser
```

**Final image contains:** Python runtime, installed packages, app source, and nothing else.

## Endpoints

| Path       | Method | Purpose                                  |
| ---------- | ------ | ---------------------------------------- |
| `/`        | GET    | Root — version and status                |
| `/health`  | GET    | Liveness probe (process is alive)        |
| `/ready`   | GET    | Readiness probe (dependencies reachable) |
| `/metrics` | GET    | Prometheus metrics endpoint              |
| `/info`    | GET    | Runtime debug information                |

## Request and Data Flow

```text
Client -> FastAPI app -> PostgreSQL
       |
       +-> health/readiness/metrics for operations
```

- Request path: HTTP request lands on FastAPI container.
- Data path: application reads/writes PostgreSQL over internal network.
- Operational path: `/health`, `/ready`, `/metrics` support automation and verification.

## Scaling Path

Current state:

- Single app container and single DB instance for local integration.

Next step:

- Multiple app replicas behind ingress/load balancer.
- Managed DB with connection pooling.
- External metrics/log pipeline with alerting.

## Failure Domains

- App container failure: service restart required.
- DB container/volume failure: data availability risk in local stack.
- CI scanner failure: release blocked by policy (intended safety gate).

## Trust Boundaries

```text
[Internet Client]
   |
   v
[App Container Boundary]
   |
   v
[Internal Compose Network Boundary]
   |
   v
[PostgreSQL Data Boundary]
```

- Only app service is published externally.
- DB traffic remains internal to app network.
- Secret values are expected to cross boundary through env injection only.
  | `/docs` | GET | Swagger UI (FastAPI auto-generated) |
