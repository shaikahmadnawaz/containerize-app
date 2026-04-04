# Scaling Notes

## Current Bottlenecks

- Single Uvicorn worker in container (`--workers 1`).
- Single PostgreSQL instance in local Compose stack.
- No external cache or queue for burst smoothing.

## Saturation Signals

- App latency growth at `/ready` and business endpoints.
- Container CPU/memory near limit.
- DB connection saturation and query latency increase.

## Scaling Strategy

1. Horizontal app scaling with multiple replicas.
2. Introduce managed PostgreSQL and connection pooling.
3. Add cache layer for read-heavy workloads.
4. Add ingress/load balancer and autoscaling policies.

## Capacity Assumptions

- Baseline demo load is low-concurrency.
- Production readiness requires load test-derived limits for CPU, memory, and DB connections.

## What Breaks First

- Database throughput and connection pool limits are likely first bottlenecks.
- Under burst load, API p95/p99 latency increases before hard failures.

## Next Validation Steps

- Run synthetic load tests and capture latency/error curves.
- Define SLO targets and alert thresholds from observed load behavior.
