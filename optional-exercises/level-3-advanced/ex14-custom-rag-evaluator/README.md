# Exercise 14: Custom RAG Evaluator

## Description
Complete evaluation suite for RAG systems with custom metrics, test cases, and benchmarking.

## Objectives
- Evaluate retrieval quality (precision, recall, MRR)
- Measure generation (faithfulness, relevance)
- Create test datasets
- Benchmark different configurations
- Identify failure modes

## Implemented Metrics

### Retrieval Metrics
- **Precision@K**: Are retrieved documents relevant?
- **Recall@K**: Did we find all relevant ones?
- **MRR (Mean Reciprocal Rank)**: Position of first relevant
- **NDCG**: Ranking quality

### Generation Metrics
- **Faithfulness**: Is response faithful to context?
- **Answer Relevance**: Does it answer the question?
- **Context Relevance**: Is context useful?
- **Hallucination Rate**: Invented information?

## Implementation

```python
from dataclasses import dataclass
from typing import List, Dict
import numpy as np

@dataclass
class TestCase:
    query: str
    ground_truth_answer: str
    relevant_doc_ids: List[str]
    metadata: Dict = None

@dataclass
class RAGResult:
    query: str
    retrieved_docs: List[str]
    retrieved_doc_ids: List[str]
    generated_answer: str
    latency: float

class RAGEvaluator:
    def __init__(self, test_cases: List[TestCase]):
        self.test_cases = test_cases
        self.llm_judge = ChatAnthropic(model="claude-sonnet-4")

    async def evaluate(self, rag_system) -> Dict:
        """Run full evaluation suite"""
        results = []

        for test_case in self.test_cases:
            # Run RAG system
            result = await rag_system.query(test_case.query)

            # Evaluate
            metrics = await self._evaluate_result(test_case, result)
            results.append(metrics)

        # Aggregate metrics
        return self._aggregate_results(results)

    async def _evaluate_result(
        self,
        test_case: TestCase,
        result: RAGResult
    ) -> Dict:
        """Evaluate single result"""

        metrics = {}

        # Retrieval metrics
        metrics.update(self._eval_retrieval(test_case, result))

        # Generation metrics
        gen_metrics = await self._eval_generation(test_case, result)
        metrics.update(gen_metrics)

        # Latency
        metrics['latency'] = result.latency

        return metrics

    def _eval_retrieval(
        self,
        test_case: TestCase,
        result: RAGResult
    ) -> Dict:
        """Evaluate retrieval quality"""

        retrieved_ids = set(result.retrieved_doc_ids)
        relevant_ids = set(test_case.relevant_doc_ids)

        # Precision@K
        precision = len(retrieved_ids & relevant_ids) / len(retrieved_ids) \
            if retrieved_ids else 0

        # Recall@K
        recall = len(retrieved_ids & relevant_ids) / len(relevant_ids) \
            if relevant_ids else 0

        # MRR (Mean Reciprocal Rank)
        mrr = 0
        for i, doc_id in enumerate(result.retrieved_doc_ids, 1):
            if doc_id in relevant_ids:
                mrr = 1 / i
                break

        # F1 Score
        f1 = 2 * (precision * recall) / (precision + recall) \
            if (precision + recall) > 0 else 0

        return {
            'precision': precision,
            'recall': recall,
            'mrr': mrr,
            'f1': f1
        }

    async def _eval_generation(
        self,
        test_case: TestCase,
        result: RAGResult
    ) -> Dict:
        """Evaluate generation quality using LLM-as-judge"""

        # Faithfulness
        faithfulness = await self._eval_faithfulness(
            result.generated_answer,
            result.retrieved_docs
        )

        # Answer relevance
        relevance = await self._eval_relevance(
            test_case.query,
            result.generated_answer
        )

        # Correctness (vs ground truth)
        correctness = await self._eval_correctness(
            result.generated_answer,
            test_case.ground_truth_answer
        )

        return {
            'faithfulness': faithfulness,
            'answer_relevance': relevance,
            'correctness': correctness
        }

    async def _eval_faithfulness(
        self,
        answer: str,
        context_docs: List[str]
    ) -> float:
        """Check if answer is faithful to context"""

        prompt = f"""
Evaluate if this answer is faithful to the provided context (0-1 scale).

Context:
{chr(10).join(context_docs)}

Answer:
{answer}

Score 1.0 if all claims are supported by context.
Score 0.0 if answer contains unsupported claims.

Respond with just a number between 0 and 1.
"""

        response = await self.llm_judge.ainvoke(prompt)
        return float(response.content.strip())

    async def _eval_relevance(self, query: str, answer: str) -> float:
        """Check if answer addresses the query"""

        prompt = f"""
Rate how well this answer addresses the query (0-1 scale).

Query: {query}
Answer: {answer}

Score 1.0 if answer directly and completely addresses query.
Score 0.0 if answer is completely unrelated.

Respond with just a number.
"""

        response = await self.llm_judge.ainvoke(prompt)
        return float(response.content.strip())

    async def _eval_correctness(
        self,
        answer: str,
        ground_truth: str
    ) -> float:
        """Compare answer to ground truth"""

        prompt = f"""
Rate how semantically similar these answers are (0-1).

Ground Truth: {ground_truth}
Generated Answer: {answer}

Score 1.0 if meaning is identical.
Score 0.0 if completely different.

Respond with just a number.
"""

        response = await self.llm_judge.ainvoke(prompt)
        return float(response.content.strip())

    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate metrics across all test cases"""

        metrics = [
            'precision', 'recall', 'mrr', 'f1',
            'faithfulness', 'answer_relevance', 'correctness',
            'latency'
        ]

        aggregated = {}
        for metric in metrics:
            values = [r[metric] for r in results]
            aggregated[metric] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }

        return aggregated
```

## Creating Test Cases

```python
class TestCaseGenerator:
    """Generate test cases from documentation"""

    async def generate_from_docs(
        self,
        documents: List[str],
        num_cases: int = 50
    ) -> List[TestCase]:
        """Generate synthetic test cases"""

        test_cases = []

        for doc in documents[:num_cases]:
            # Generate question from document
            question = await self._generate_question(doc)

            # Extract ground truth answer
            answer = await self._extract_answer(doc, question)

            test_cases.append(TestCase(
                query=question,
                ground_truth_answer=answer,
                relevant_doc_ids=[doc.id]
            ))

        return test_cases

    async def _generate_question(self, document: str) -> str:
        prompt = f"""
Generate a specific question that can be answered using this document:

{document}

Make it realistic - something a user would actually ask.
"""

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()
```

## Benchmarking Different Configs

```python
class RAGBenchmark:
    """Compare different RAG configurations"""

    async def compare_configs(
        self,
        configs: List[RAGConfig],
        test_cases: List[TestCase]
    ) -> pd.DataFrame:
        """Benchmark multiple configurations"""

        results = []

        for config in configs:
            print(f"📊 Testing config: {config.name}")

            # Build RAG system with this config
            rag = self._build_rag(config)

            # Evaluate
            evaluator = RAGEvaluator(test_cases)
            metrics = await evaluator.evaluate(rag)

            results.append({
                'config': config.name,
                **{k: v['mean'] for k, v in metrics.items()}
            })

        return pd.DataFrame(results)

# Example usage
configs = [
    RAGConfig("baseline", chunk_size=500, top_k=5),
    RAGConfig("large_chunks", chunk_size=1000, top_k=5),
    RAGConfig("more_context", chunk_size=500, top_k=10),
    RAGConfig("hybrid", chunk_size=500, top_k=5, use_reranking=True),
]

results_df = await benchmark.compare_configs(configs, test_cases)
print(results_df.to_markdown())
```

## Failure Analysis

```python
class FailureAnalyzer:
    """Identify and categorize failures"""

    def analyze_failures(
        self,
        results: List[Tuple[TestCase, RAGResult, Dict]]
    ):
        failures = {
            'retrieval_failure': [],  # Didn't find right docs
            'generation_failure': [],  # Wrong answer
            'hallucination': [],  # Made up facts
        }

        for test_case, result, metrics in results:
            # Retrieval failure
            if metrics['recall'] < 0.5:
                failures['retrieval_failure'].append({
                    'query': test_case.query,
                    'missed_docs': test_case.relevant_doc_ids,
                    'retrieved_docs': result.retrieved_doc_ids
                })

            # Generation failure
            if metrics['correctness'] < 0.7:
                failures['generation_failure'].append({
                    'query': test_case.query,
                    'expected': test_case.ground_truth_answer,
                    'generated': result.generated_answer
                })

            # Hallucination
            if metrics['faithfulness'] < 0.8:
                failures['hallucination'].append({
                    'query': test_case.query,
                    'answer': result.generated_answer,
                    'context': result.retrieved_docs
                })

        return failures
```

## Visualization

```python
import matplotlib.pyplot as plt

def plot_metrics(results: Dict):
    """Visualize evaluation results"""

    metrics = ['precision', 'recall', 'f1', 'faithfulness']
    values = [results[m]['mean'] for m in metrics]

    plt.figure(figsize=(10, 6))
    plt.bar(metrics, values)
    plt.ylabel('Score')
    plt.title('RAG System Performance')
    plt.ylim(0, 1)
    plt.axhline(y=0.8, color='r', linestyle='--', label='Target')
    plt.legend()
    plt.show()
```

## Challenges Extra

1. **Automated Optimization**: Use eval results to auto-tune RAG
2. **Adversarial Testing**: Generate challenging test cases
3. **Cost-Quality Tradeoff**: Optimize for cost and quality
4. **Real-time Monitoring**: Evaluate in production

## Resources
- [RAGAS Framework](https://github.com/explodinggradients/ragas)
- [TruLens](https://www.trulens.org/)
- [LangSmith](https://www.langchain.com/langsmith)

**Time**: 6-8h
