# Cost Assumptions

## Scope

This project runs locally for development and publishes images to GHCR via CI.

## Cost Drivers

- CI minutes for lint/test/build/scan.
- Container registry storage and egress from GHCR.
- Developer workstation resources for local Compose stack.

## Right-Sizing Assumptions

- Single-worker app container is sufficient for local and demo validation.
- DB size and retention are intentionally small in local environment.
- Production right-sizing requires load-test evidence, not fixed defaults.

## Trade-offs

- Blocking vulnerability scans increase CI time but reduce security risk.
- Multi-stage builds reduce runtime footprint and long-term storage overhead.

## Cleanup Guidance

```bash
make clean
docker image prune -f
docker volume prune -f
```

## Future Production Cost Considerations

- Managed DB SKU choice vs self-hosted operational cost.
- Autoscaling min/max replica settings to control idle spend.
- Observability ingestion volume and retention tuning.
