# Operations Guide

## Deployment Flow

1. Developer opens PR.
2. CI runs lint, smoke tests, Docker build, and Trivy scan.
3. Review + approval required before merge.
4. Merge to `master` pushes immutable image tags to GHCR.
5. Runtime platform pulls approved image tag/digest.

## Environment Strategy

| Environment | Purpose          | Deployment Mechanism                        | Config Source                           |
| ----------- | ---------------- | ------------------------------------------- | --------------------------------------- |
| dev         | local iteration  | `docker compose up`                         | local env vars                          |
| stage       | validation gate  | GitHub Actions PR jobs                      | GitHub Actions secrets/vars             |
| prod        | release artifact | `master` image push for downstream deployment | platform secret manager + env injection |

## Change Safety and Rollback

- Always deploy by immutable tag or digest, never `latest`.
- Keep previous known-good release available in registry.
- Rollback pattern:
  1. identify failing release tag
  2. redeploy previous digest
  3. verify `/health`, `/ready`, and smoke checks

## Routine Maintenance

- Weekly: refresh base image and rerun scan.
- Weekly: dependency review (`pip list --outdated` in controlled branch).
- Monthly: runbook and alert-path dry run.
- Monthly: image/volume cleanup in dev environments.

## Observability Coverage

- Logs: container logs from app and db services.
- Health checks: `/health` and `/ready` endpoints.
- Metrics: `/metrics` endpoint for scrape-based monitoring.
- Alert strategy: upstream platform should alert on health failure, readiness degradation, and elevated error/latency signals.

## Ownership Boundaries

- App team: FastAPI behavior, API contracts, dependency updates.
- Platform team: container baseline, runtime hardening, CI gates, registry policy.
- Shared: incident response and rollback execution.

## Upgrade Path

- Minor Python/FastAPI updates through PR + CI.
- Base image upgrades validated by Trivy and smoke tests.
- Major upgrades require compatibility check in stage path first.

## Operational Risks

- Single local PostgreSQL instance is a reliability bottleneck.
- No built-in multi-region or HA in this reference project.
- Metrics endpoint exists, but external alerting platform integration is out of scope for this repo.

## Backup/Restore Notes

- Local DB persistence relies on named Docker volume.
- Backup command (local):

```bash
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

- Restore command (local):

```bash
cat backup.sql | docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```
