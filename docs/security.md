# Security Notes

## Threat Surface

- Exposed surface: FastAPI service on port `8000`.
- Internal-only surface: PostgreSQL service on Compose bridge network.
- Build-time supply chain: base image + Python packages.

## Secret Handling

- Secrets are not committed to git.
- Runtime values are injected through environment variables.
- Production recommendation: use a secret manager (for example, Key Vault, Vault, or platform-native secrets).

## Runtime Hardening

- Non-root user in container (`uid=10001`).
- Read-only filesystem with tmpfs for temporary writes.
- Linux capabilities dropped (`cap_drop: ALL`).
- `no-new-privileges` security option enabled in Compose.

## Least Privilege

- DB is not externally published in local stack.
- App only receives required connection values.
- CI uses scoped GitHub token permissions by job.

## Security Validation

- Trivy blocks HIGH/CRITICAL findings in CI.
- SARIF results uploaded to GitHub Security tab.
- Base image and dependency update cadence required for risk reduction.

## Hardening Gaps / Next Steps

- Add signed image provenance (for example, cosign/SLSA).
- Add secret scanning in CI (for example, gitleaks).
- Add runtime policy checks in deployment platform (Kubernetes PSP replacement or admission policies).
