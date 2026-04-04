"""
FastAPI application — containerize-app project.
Demonstrates production-ready Docker containerization patterns.
"""

from fastapi import FastAPI, HTTPException
from starlette.responses import Response
import os
import platform
import time
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import psycopg

app = FastAPI(
    title="containerize-app",
    description="Portfolio project: containerizing a FastAPI app with production Docker best practices.",
    version="1.0.0",
)

START_TIME = time.time()
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=str(response.status_code),
    ).inc()
    return response


@app.get("/", tags=["root"])
def root():
    return {
        "app": "containerize-app",
        "version": "1.0.0",
        "status": "ok",
    }


@app.get("/health", tags=["ops"])
def health():
    """Liveness probe — returns 200 when the process is alive."""
    return {"status": "healthy"}


@app.get("/ready", tags=["ops"])
def ready():
    """Readiness probe — verify critical dependencies are reachable."""
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise HTTPException(status_code=503, detail="DATABASE_URL not configured")

    try:
        with psycopg.connect(database_url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail="database not ready") from exc

    return {"status": "ready"}


@app.get("/info", tags=["ops"])
def info():
    """Returns runtime environment information for debugging."""
    return {
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "os": platform.system(),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "environment": os.environ.get("APP_ENV", "production"),
    }


@app.get("/metrics", tags=["ops"])
def metrics():
    """Prometheus scrape endpoint for basic runtime metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
