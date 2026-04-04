# Runbook — containerize-app

Operational runbook using a consistent incident workflow:

`diagnose -> mitigate -> recover -> prevent`

---

## Baseline Commands

```bash
make run
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
```

---

## Incident 1: App Unhealthy or Restart Loop

### Diagnose

```bash
docker compose ps
docker compose logs app --tail=200
docker stats --no-stream
```

### Mitigate

```bash
docker compose restart app
```

### Recover

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/ready
```

### Prevent

- Add regression test for the failing startup path.
- Keep runtime config validation on startup.

### Rollback guidance

```bash
docker run --rm ghcr.io/<owner>/containerize-app:<known-good-tag>
```

---

## Incident 2: Readiness 503 (Dependency Not Ready)

### Diagnose

```bash
docker compose config | grep DATABASE_URL
docker compose ps db
docker compose logs db --tail=200
```

### Mitigate

```bash
docker compose restart db
```

### Recover

```bash
docker compose exec -T db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
curl -f http://localhost:8000/ready
```

### Prevent

- Keep `depends_on` with health condition.
- Maintain smoke checks in CI for readiness behavior.

### Rollback guidance

```bash
docker compose down
docker compose up -d
```

---

## Incident 3: CI Blocked by Vulnerability Scan

### Diagnose

```bash
trivy image --severity HIGH,CRITICAL containerize-app:local
```

### Mitigate

- Update base image tag to latest patch.
- Rebuild image and rerun scan.

### Recover

```bash
make build
make scan
```

### Prevent

- Weekly base image refresh cadence.
- Dependency update PRs with scan verification.

### Rollback guidance

- If urgent release is required, deploy last known-good digest and schedule patch release.

---

## Incident 4: Wrong Release Tag Deployed

### Diagnose

```bash
docker inspect containerize-app:local | grep -i -E 'RepoTags|RepoDigests'
```

### Mitigate

- Stop unhealthy container.
- Pull known-good image tag.

### Recover

```bash
docker compose down
docker pull ghcr.io/<owner>/containerize-app:<known-good-tag>
docker compose up -d
```

### Prevent

- Enforce immutable tag/digest promotion policy.
- Record release tag and digest in deployment notes.

### Rollback guidance

```bash
docker pull ghcr.io/<owner>/containerize-app:<previous-good-tag>
docker compose up -d
```

---

## Routine Operations

```bash
make build
make run
make logs
make scan
make stop
make clean
```

---

## Escalation and Ownership

- App behavior issues: application team.
- Container baseline, CI gate, release image policy: platform/devops owner.
- Shared incident command for production-impacting issues.
