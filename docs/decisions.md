# Key Design Decisions (ADRs)

---

## ADR-001: Multi-Stage Dockerfile

**Decision:** Use a two-stage build (builder + runtime).

**Context:** Single-stage builds include compilers and package tools in the runtime image.

**Chosen:** Builder stage installs wheels; runtime stage copies only the installed package prefix.

**Consequences:**

- Runtime image is significantly smaller and has no build tooling.
- Reduces attack surface; no gcc or pip in production.
- Slightly more complex Dockerfile but the pattern is standard and learnable.

---

## ADR-002: Non-Root Container User

**Decision:** Create `appuser` (uid 10001) and drop to it before `CMD`.

**Context:** Many base images default to root, violating the principle of least privilege.

**Chosen:** Explicit `RUN groupadd/useradd` + `USER appuser` in Dockerfile.

**Consequences:**

- Limits blast radius if the process is exploited.
- Satisfies Pod Security Standards `restricted` profile when deployed to Kubernetes.
- Requires `chown` on working directories during build.

---

## ADR-003: Read-Only Container Filesystem in Compose

**Decision:** Set `read_only: true` and mount `/tmp` as tmpfs in `docker-compose.yml`.

**Context:** Writable container filesystems allow attackers to modify binaries or drop payloads.

**Chosen:** Read-only root with explicit tmpfs for dynamic temp writes.

**Consequences:**

- Application cannot write anywhere except `/tmp`.
- Forces intentional separation of ephemeral vs persistent storage.
- Highlights any silent assumption about writable paths early.

---

## ADR-004: Capability Drop (`cap_drop: ALL`)

**Decision:** Drop all Linux capabilities in Compose service config.

**Context:** Docker containers inherit a broad default capability set even when running as non-root.

**Chosen:** `cap_drop: ALL` with `no-new-privileges:true` security option.

**Consequences:**

- Application cannot perform privileged syscalls.
- If specific capabilities are needed later they must be explicitly added and justified.

---

## ADR-005: Image Scanning as a Blocking CI Gate

**Decision:** Trivy scan with `exit-code: 1` on HIGH/CRITICAL findings blocks the CI pipeline.

**Context:** Warn-only scan policies are routinely bypassed.

**Chosen:** Blocking gate on severity HIGH/CRITICAL; results surfaced to GitHub Security tab via SARIF upload.

**Consequences:**

- Release requires clean scan or justified suppression with `.trivyignore`.
- Upstream base image vulnerabilities must be patched on cadence.

---

## ADR-006: PostgreSQL Not Exposed on Host Network

**Decision:** DB service has no `ports:` entry in docker-compose.yml.

**Context:** Exposing database ports on the host is a common misconfiguration.

**Chosen:** DB is only reachable within the Compose-managed bridge network by service name `db`.

**Consequences:**

- No external tooling can reach the DB without explicit port mapping override.
- Developers must exec into the app or use a local psql via `docker compose exec db psql`.

---

## Rejected Alternatives

### RA-001: Single-stage Docker build

- Rejected because build toolchain would remain in runtime image, increasing attack surface.

### RA-002: Run container as root user

- Rejected because it violates least-privilege baseline and increases blast radius.

### RA-003: Warn-only vulnerability scanning

- Rejected because non-blocking scans are frequently ignored under delivery pressure.

### RA-004: Expose DB port to host by default

- Rejected because default host exposure increases accidental data access risk.
