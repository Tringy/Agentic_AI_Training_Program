# Exercise 17: Production Monitoring System

## Description
Complete observability system for LLM applications in production.

## Objectives
- Distributed tracing of LLM calls
- Real-time metrics dashboard
- Alerting system
- Log aggregation
- Performance profiling
- Cost tracking

## Stack

```bash
- Prometheus (metrics)
- Grafana (dashboards)
- Jaeger/Tempo (tracing)
- Loki (logs)
- AlertManager (alerts)
```

## Implementation

### 1. Tracing

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("llm_call")
async def traced_completion(prompt: str):
    span = trace.get_current_span()

    # Add attributes
    span.set_attribute("prompt.length", len(prompt))
    span.set_attribute("model", "gpt-4")

    start = time.time()
    result = await llm.complete(prompt)
    latency = time.time() - start

    span.set_attribute("latency", latency)
    span.set_attribute("tokens", result.usage.total_tokens)
    span.set_attribute("cost", calculate_cost(result.usage))

    return result
```

### 2. Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

llm_latency = Histogram(
    'llm_latency_seconds',
    'LLM request latency',
    ['model']
)

llm_cost = Counter(
    'llm_cost_dollars',
    'Total cost in dollars',
    ['model']
)

active_requests = Gauge(
    'llm_active_requests',
    'Currently active requests'
)

@active_requests.track_inprogress()
async def monitored_completion(prompt: str, model: str):
    start = time.time()

    try:
        result = await llm.complete(prompt, model=model)

        # Record metrics
        llm_requests_total.labels(model=model, status="success").inc()
        llm_latency.labels(model=model).observe(time.time() - start)
        llm_cost.labels(model=model).inc(result.cost)

        return result

    except Exception as e:
        llm_requests_total.labels(model=model, status="error").inc()
        raise
```

### 3. Structured Logging

```python
import structlog

logger = structlog.get_logger()

async def logged_completion(prompt: str):
    log = logger.bind(
        request_id=generate_id(),
        model="gpt-4",
        prompt_length=len(prompt)
    )

    log.info("llm_request_started")

    try:
        result = await llm.complete(prompt)

        log.info("llm_request_completed",
            tokens=result.usage.total_tokens,
            cost=result.cost,
            latency=result.latency
        )

        return result

    except Exception as e:
        log.error("llm_request_failed", error=str(e))
        raise
```

### 4. Alerting Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: llm_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(llm_requests_total{status="error"}[5m]) > 0.05
        for: 2m
        annotations:
          summary: "High LLM error rate"

      - alert: HighLatency
        expr: histogram_quantile(0.95, llm_latency_seconds) > 5
        for: 5m
        annotations:
          summary: "LLM P95 latency > 5s"

      - alert: HighCost
        expr: increase(llm_cost_dollars[1h]) > 100
        annotations:
          summary: "LLM costs > $100/hour"
```

### 5. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "LLM Production Metrics",
    "panels": [
      {
        "title": "Requests per Second",
        "targets": [
          {
            "expr": "rate(llm_requests_total[5m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, llm_latency_seconds)"
          }
        ]
      },
      {
        "title": "Cost per Hour",
        "targets": [
          {
            "expr": "increase(llm_cost_dollars[1h])"
          }
        ]
      }
    ]
  }
}
```

## Performance Profiling

```python
import cProfile
import pstats

def profile_llm_call():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = llm.complete(prompt)

    profiler.disable()

    # Analyze
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

## Challenges

1. **Distributed Tracing**: Trace across microservices
2. **Custom Metrics**: Business-specific KPIs
3. **Anomaly Detection**: ML-based alerting
4. **SLO Tracking**: Track SLIs/SLOs

**Time**: 12-15h
**Resources**: [Prometheus](https://prometheus.io/), [Grafana](https://grafana.com/)
