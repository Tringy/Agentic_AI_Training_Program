# Exercise 03: Prompt Testing Framework

## Description

Build a complete framework for A/B testing prompts, tracking performance, and systematic optimization. Essential for any team using LLMs in production.

## Learning Objectives

- ✅ Design A/B testing experiments for prompts
- ✅ Define and measure quality metrics
- ✅ Implement statistical significance testing
- ✅ Create reproducible evaluation pipelines
- ✅ Optimize prompts based on data

## Core Features

### 1. Test Runner
```python
class PromptTest:
    variants: List[PromptVariant]
    test_cases: List[TestCase]
    metrics: List[Metric]

    async def run(self) -> TestResults
```

### 2. Supported Metrics
- Response quality (LLM-as-judge)
- Latency
- Token usage
- Cost
- Success rate
- Custom metrics

### 3. Statistical Analysis
- A/B test significance (t-test, chi-square)
- Confidence intervals
- Sample size recommendations
- Power analysis

### 4. Result Reporting
- Comparison tables
- Visualization (charts)
- Winner selection
- Recommendations

## Quick Implementation

```python
# Quick start example
from prompt_tester import PromptTest, Variant, Metric

test = PromptTest(
    name="Code Review Prompts",
    variants=[
        Variant("v1", "You are a code reviewer. Review:\n{code}"),
        Variant("v2", "Review this code for bugs:\n{code}"),
    ],
    test_cases=[
        {"code": "def add(a,b): return a+b"},
        {"code": "x = [1,2,3]; print(x[10])"},
    ],
    metrics=[
        Metric.quality_score(),
        Metric.latency(),
        Metric.cost()
    ]
)

results = await test.run()
results.show_winner()  # v2 wins (p=0.023)
```

## Suggested Stack

- Python + FastAPI
- SQLite/PostgreSQL for results
- Pandas for analysis
- Plotly for visualizations
- Scipy for statistical tests

## Implementation Guide

### Step 1: Core Framework

```python
# core/test_runner.py
class TestRunner:
    async def run_variant(
        self,
        variant: PromptVariant,
        test_case: TestCase
    ) -> VariantResult:
        start = time.time()
        response = await self.llm_client.complete(
            variant.format(test_case)
        )
        latency = time.time() - start

        return VariantResult(
            response=response,
            latency=latency,
            tokens=response.usage,
            cost=self.calculate_cost(response)
        )
```

### Step 2: Metrics System

```python
# metrics/base.py
class Metric(ABC):
    @abstractmethod
    async def evaluate(
        self,
        result: VariantResult,
        ground_truth: Any
    ) -> float:
        pass

class QualityMetric(Metric):
    """LLM-as-judge quality evaluation"""
    async def evaluate(self, result, ground_truth):
        # Use GPT-4 to judge quality 1-10
        pass

class CostMetric(Metric):
    """Calculate cost per request"""
    def evaluate(self, result, ground_truth):
        return result.cost
```

### Step 3: Statistical Analysis

```python
# analysis/statistics.py
from scipy import stats

def calculate_significance(
    variant_a: List[float],
    variant_b: List[float]
) -> SignificanceResult:
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(variant_a, variant_b)

    # Calculate effect size (Cohen's d)
    effect_size = calculate_cohens_d(variant_a, variant_b)

    return SignificanceResult(
        p_value=p_value,
        is_significant=p_value < 0.05,
        effect_size=effect_size,
        winner="A" if mean(variant_a) > mean(variant_b) else "B"
    )
```

### Step 4: Results Dashboard

```python
# reporting/dashboard.py
import plotly.graph_objects as go

def create_comparison_chart(results: TestResults):
    fig = go.Figure()

    # Bar chart comparing variants
    fig.add_trace(go.Bar(
        name='Variant A',
        x=['Quality', 'Cost', 'Latency'],
        y=results.variant_a_metrics
    ))

    fig.add_trace(go.Bar(
        name='Variant B',
        x=['Quality', 'Cost', 'Latency'],
        y=results.variant_b_metrics
    ))

    return fig
```

## Testing Strategy

```python
# tests/test_framework.py
def test_statistical_significance():
    # Variant A consistently better
    a_scores = [8, 9, 8.5, 9, 8]
    b_scores = [6, 5.5, 6, 5, 6.5]

    result = calculate_significance(a_scores, b_scores)
    assert result.is_significant
    assert result.winner == "A"

def test_insufficient_sample():
    # Too few samples
    a_scores = [8, 9]
    b_scores = [7, 6]

    result = calculate_significance(a_scores, b_scores)
    assert not result.is_significant  # Need more data
```

## Extra Challenges

1. **Multi-Armed Bandit**: Implement adaptive testing
2. **Bayesian A/B Testing**: Alternative to frequentist
3. **Continuous Evaluation**: Monitor in production
4. **Auto-optimization**: Suggest prompt improvements

## Resources

- [Statistical Testing Guide](https://www.statsmodels.org)
- [Evan Miller's A/B Calculator](https://www.evanmiller.org/ab-testing/)
- [Prompt Engineering Guide](https://www.promptingguide.ai)

## Submission

- GitHub repo with framework
- 3+ example tests executed
- Statistical analysis report
- Comparison visualizations
- Usage documentation

---

**Next**: [Ex 04: Cost Calculator →](../ex04-cost-calculator/)
