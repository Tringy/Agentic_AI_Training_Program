# Exercise 04: Cost Calculator Dashboard

## Description

Build an interactive, real-time dashboard to monitor and optimize LLM API costs. Visualize usage, predict future costs, and generate automatic alerts.

## Objectives

- ✅ Track real-time LLM API costs
- ✅ Visualize usage patterns and trends
- ✅ Predict future costs
- ✅ Generate cost optimization recommendations
- ✅ Set up budget alerts

## Core Features

### 1. Cost Tracking
- Log all API calls
- Calculate cost per request
- Aggregate by project/user
- Historical tracking

### 2. Dashboard
- Real-time cost display
- Usage charts (daily/weekly/monthly)
- Cost breakdown by model
- Top consumers

### 3. Predictions
- Forecast next month's costs
- Identify usage spikes
- Trend analysis

### 4. Alerts & Notifications
- Budget threshold alerts
- Anomaly detection
- Daily/weekly reports

## Tech Stack

### Frontend
```bash
- Next.js 14 (App Router)
- TailwindCSS + shadcn/ui
- Recharts for visualizations
- React Query for data fetching
```

### Backend
```bash
- PostgreSQL (tracking data)
- Redis (caching)
- FastAPI/Next.js API routes
```

## Quick Implementation

### Database Schema

```sql
-- Usage tracking
CREATE TABLE api_calls (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    model VARCHAR(50),
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost DECIMAL(10, 6),
    project VARCHAR(100),
    user_id VARCHAR(100),
    latency_ms INTEGER
);

-- Budget alerts
CREATE TABLE budget_alerts (
    id SERIAL PRIMARY KEY,
    project VARCHAR(100),
    threshold DECIMAL(10, 2),
    period VARCHAR(20), -- 'daily', 'monthly'
    notification_channel VARCHAR(50)
);
```

### Cost Tracking Hook

```typescript
// lib/useCostTracking.ts
export function useCostTracking() {
  const trackCall = async (call: APICall) => {
    const cost = calculateCost(
      call.inputTokens,
      call.outputTokens,
      call.model
    );

    await fetch('/api/track', {
      method: 'POST',
      body: JSON.stringify({
        ...call,
        cost,
        timestamp: new Date()
      })
    });

    return cost;
  };

  return { trackCall };
}
```

### Dashboard Component

```typescript
// components/CostDashboard.tsx
export function CostDashboard() {
  const { data: costs } = useQuery('costs', fetchCosts);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader>
          <CardTitle>Today's Cost</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            ${costs?.today?.toFixed(2)}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>This Month</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            ${costs?.month?.toFixed(2)}
          </div>
          <p className="text-sm text-muted-foreground">
            {costs?.percentChange}% vs last month
          </p>
        </CardContent>
      </Card>

      {/* Usage Chart */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>Usage Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <LineChart data={costs?.timeseries} />
        </CardContent>
      </Card>
    </div>
  );
}
```

### Cost Prediction

```python
# services/prediction.py
import numpy as np
from sklearn.linear_model import LinearRegression

def predict_monthly_cost(historical_data):
    # Simple linear regression
    X = np.array(range(len(historical_data))).reshape(-1, 1)
    y = np.array(historical_data)

    model = LinearRegression()
    model.fit(X, y)

    # Predict next 30 days
    future_days = np.array(range(len(X), len(X) + 30)).reshape(-1, 1)
    predictions = model.predict(future_days)

    return {
        "predicted_cost": predictions.sum(),
        "confidence": calculate_confidence(model, X, y),
        "trend": "increasing" if model.coef_[0] > 0 else "decreasing"
    }
```

## Key Features to Implement

### 1. Real-time Tracking
```typescript
// middleware to intercept API calls
export const costTrackingMiddleware = (client) => {
  return new Proxy(client, {
    get(target, prop) {
      if (prop === 'complete') {
        return async (...args) => {
          const start = Date.now();
          const result = await target[prop](...args);
          const latency = Date.now() - start;

          await trackCost({
            tokens: result.usage,
            latency,
            model: args[0].model
          });

          return result;
        };
      }
      return target[prop];
    }
  });
};
```

### 2. Budget Alerts
```python
# alerts/monitor.py
async def check_budgets():
    active_alerts = await db.get_active_alerts()

    for alert in active_alerts:
        current_usage = await db.get_usage(
            project=alert.project,
            period=alert.period
        )

        if current_usage > alert.threshold:
            await send_alert(
                project=alert.project,
                current=current_usage,
                threshold=alert.threshold
            )
```

### 3. Optimization Recommendations
```typescript
function generateRecommendations(usage: Usage[]): Recommendation[] {
  const recommendations = [];

  // Check if using expensive models for simple tasks
  const simpleTasksExpensiveModel = usage.filter(
    u => u.tokens < 500 && u.model === 'gpt-4'
  );

  if (simpleTasksExpensiveModel.length > 100) {
    recommendations.push({
      type: 'model-switch',
      message: 'Consider using gpt-3.5-turbo for simple tasks',
      potential_savings: calculateSavings(simpleTasksExpensiveModel)
    });
  }

  return recommendations;
}
```

## Testing

```typescript
// __tests__/cost-tracking.test.ts
describe('Cost Tracking', () => {
  it('should calculate GPT-4 costs correctly', () => {
    const cost = calculateCost(1000, 500, 'gpt-4');
    expect(cost).toBeCloseTo(0.045);
  });

  it('should aggregate daily costs', async () => {
    const calls = [
      { cost: 0.01, timestamp: '2024-01-01' },
      { cost: 0.02, timestamp: '2024-01-01' },
      { cost: 0.03, timestamp: '2024-01-02' },
    ];

    const daily = aggregateDaily(calls);
    expect(daily['2024-01-01']).toBe(0.03);
  });
});
```

## Extra Challenges

1. **Multi-tenant**: Support multiple organizations
2. **Slack Integration**: Send alerts to Slack
3. **Cost Attribution**: Tag costs by feature/team
4. **Anomaly Detection**: ML-based spike detection

## Resources

- [Recharts Documentation](https://recharts.org)
- [shadcn/ui Components](https://ui.shadcn.com)
- [OpenAI Usage Dashboard](https://platform.openai.com/usage)

## Submission

- Working dashboard deployed
- 7-day mock data showing usage
- Budget alert system functioning
- Cost predictions displayed
- Optimization recommendations shown

---

**Control your costs! 💰**
