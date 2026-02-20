"""RAG Evaluation utilities."""
from typing import List, Dict, Set, Optional
from dataclasses import dataclass


@dataclass
class EvalExample:
    """Evaluation example with ground truth."""
    question: str
    expected_answer: str
    relevant_files: List[str]


def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Precision@K: fraction of retrieved docs that are relevant."""
    retrieved_k = retrieved[:k]
    relevant_retrieved = len(set(retrieved_k) & relevant)
    return relevant_retrieved / k if k > 0 else 0.0


def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Recall@K: fraction of relevant docs that were retrieved."""
    retrieved_k = retrieved[:k]
    relevant_retrieved = len(set(retrieved_k) & relevant)
    return relevant_retrieved / len(relevant) if relevant else 0.0


def mrr(retrieved: List[str], relevant: Set[str]) -> float:
    """Mean Reciprocal Rank: how high is the first relevant result."""
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            return 1.0 / (i + 1)
    return 0.0


class RAGEvaluator:
    """Evaluator for RAG system performance."""

    def __init__(self, rag_system, llm_judge=None):
        self.rag = rag_system
        self.judge = llm_judge

    def evaluate_retrieval(
        self,
        examples: List[EvalExample],
        k: int = 5
    ) -> Dict:
        """Evaluate retrieval quality."""
        metrics = {
            'precision': [],
            'recall': [],
            'mrr': []
        }

        for example in examples:
            result = self.rag.query(example.question, n_results=k)
            retrieved = [s['file'] for s in result['sources']]
            relevant = set(example.relevant_files)

            metrics['precision'].append(precision_at_k(retrieved, relevant, k))
            metrics['recall'].append(recall_at_k(retrieved, relevant, k))
            metrics['mrr'].append(mrr(retrieved, relevant))

        n = len(examples)
        return {
            f'precision@{k}': round(sum(metrics['precision']) / n, 3) if n else 0,
            f'recall@{k}': round(sum(metrics['recall']) / n, 3) if n else 0,
            'mrr': round(sum(metrics['mrr']) / n, 3) if n else 0,
            'n_examples': n
        }

    def evaluate_generation(
        self,
        examples: List[EvalExample]
    ) -> Dict:
        """Evaluate generation quality using LLM-as-judge."""
        if not self.judge:
            return {"error": "No LLM judge configured"}

        scores = {
            'relevance': [],
            'accuracy': []
        }

        for example in examples:
            result = self.rag.query(example.question)
            generated = result['answer']

            relevance = self._judge_relevance(example.question, generated)
            scores['relevance'].append(relevance)

            accuracy = self._judge_accuracy(
                example.question,
                example.expected_answer,
                generated
            )
            scores['accuracy'].append(accuracy)

        n = len(examples)
        return {
            'relevance': round(sum(scores['relevance']) / n, 3) if n else 0,
            'accuracy': round(sum(scores['accuracy']) / n, 3) if n else 0,
            'n_examples': n
        }

    def _judge_relevance(self, question: str, answer: str) -> float:
        """Judge if answer is relevant to question."""
        prompt = f"""Rate how relevant this answer is to the question on a scale of 1-5.

Question: {question}
Answer: {answer}

Return only a single number from 1 to 5."""

        response = self.judge.chat([{"role": "user", "content": prompt}])
        try:
            score = float(response.strip())
            return min(max(score, 1), 5) / 5.0
        except:
            return 0.5

    def _judge_accuracy(
        self,
        question: str,
        expected: str,
        generated: str
    ) -> float:
        """Judge if answer matches expected answer."""
        prompt = f"""Compare these two answers to the same question on a scale of 1-5.

Question: {question}
Expected Answer: {expected}
Generated Answer: {generated}

How well does the generated answer match the expected answer?
Return only a single number from 1 to 5."""

        response = self.judge.chat([{"role": "user", "content": prompt}])
        try:
            score = float(response.strip())
            return min(max(score, 1), 5) / 5.0
        except:
            return 0.5


def create_eval_dataset(examples: List[Dict]) -> List[EvalExample]:
    """Create evaluation dataset from list of dicts."""
    return [
        EvalExample(
            question=ex['question'],
            expected_answer=ex['expected_answer'],
            relevant_files=ex['relevant_files']
        )
        for ex in examples
    ]
