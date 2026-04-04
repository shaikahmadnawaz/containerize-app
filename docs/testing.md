# Testing and Validation

## Validation Strategy

- Static quality: lint (`ruff`).
- Runtime quality: smoke tests for health/readiness/info endpoints.
- Supply chain safety: Trivy vulnerability scan gate.

## CI Checks

1. Install dependencies.
2. Lint FastAPI app source.
3. Run smoke tests.
4. Build runtime image.
5. Scan built image for HIGH/CRITICAL CVEs.

## Smoke Tests

- `/health` returns healthy status.
- `/ready` fails when DB URL not configured and succeeds when set.
- `/info` returns runtime metadata fields.

## Failure Testing (Current)

- Misconfiguration simulation through missing `DATABASE_URL` in tests.
- Rollback path documented and executable from runbook.

## Promotion Checks

- PR must be green before merge.
- Main branch image push only after scan gate passes.
- Deployment must verify health/readiness after release.
