# Exercise 02: Hallucination Detector

## Description

Build a system to detect and measure hallucinations in LLM outputs. Hallucinations are one of the most critical problems in production, and this tool will allow you to identify, measure, and mitigate them.

## Learning Objectives

Upon completing this exercise, you will be able to:

- ✅ Identify different types of hallucinations
- ✅ Implement automatic detection techniques
- ✅ Use LLMs as evaluators (LLM-as-judge)
- ✅ Create confidence/fidelity metrics
- ✅ Design anti-hallucination prompts

## Prerequisites

- Complete Day 1-2 of the main program
- Understand hallucination concepts
- Familiarity with prompt engineering
- API key from at least one LLM provider

## Types of Hallucinations to Detect

### 1. Factual Hallucinations
- False information presented as true
- Incorrect dates, numbers, names
- Events that did not occur

### 2. Contextual Hallucinations
- Information not present in the context
- Incorrect inferences
- Baseless extrapolations

### 3. Consistency Hallucinations
- Internal contradictions
- Inconsistent information
- Fact changes during conversation

## Required Features

### Core Features

1. **Hallucination Detection**
   ```typescript
   interface HallucinationDetection {
     isHallucinated: boolean;
     confidence: number; // 0-1
     type: 'factual' | 'contextual' | 'consistency';
     evidence: string[];
     suggestions: string[];
   }
   ```

2. **Multiple Detection Methods**
   - Self-consistency checking
   - External fact verification (optional)
   - Confidence score analysis
   - Citation checking

3. **Scoring System**
   - Hallucination severity score (0-10)
   - Confidence score
   - Reliability rating

4. **Mitigation Strategies**
   - Suggest prompt improvements
   - Recommend verification steps
   - Generate safer alternatives

### Advanced Features (Optional)

- 🔥 Integration with fact-checking APIs
- 🔥 Historical tracking of hallucination rates
- 🔥 A/B testing of anti-hallucination prompts
- 🔥 Real-time detection in streaming responses

## Suggested Tech Stack

### Backend

```python
# Python is ideal for this project
- fastapi
- anthropic / openai
- pydantic
- numpy (for scoring)
- httpx (for fact-checking APIs optional)
```

### Frontend (Optional)

```typescript
- next.js / streamlit
- react-markdown
- recharts (for visualization)
```

## Implementation Guide

### Step 1: Project Setup

```bash
mkdir hallucination-detector
cd hallucination-detector
python -m venv venv
source venv/bin/activate
pip install fastapi anthropic pydantic uvicorn pytest
```

### Step 2: Define Data Models

**File: `models.py`**

```python
from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum

class HallucinationType(str, Enum):
    FACTUAL = "factual"
    CONTEXTUAL = "contextual"
    CONSISTENCY = "consistency"

class HallucinationResult(BaseModel):
    is_hallucinated: bool
    confidence: float = Field(ge=0, le=1)
    hallucination_type: HallucinationType | None
    evidence: List[str]
    severity: int = Field(ge=0, le=10)
    suggestions: List[str]

class DetectionRequest(BaseModel):
    text: str
    context: str | None = None
    previous_responses: List[str] = []
    detection_method: str = "self-consistency"
```

**Tasks**:
- [ ] Define all necessary models
- [ ] Add Pydantic validations
- [ ] Document each field

### Step 3: Implement Self-Consistency Checking

**File: `detectors/self_consistency.py`**

```python
import anthropic
from typing import List

class SelfConsistencyDetector:
    """
    Generate multiple responses and compare consistency
    """

    def __init__(self, client: anthropic.Client):
        self.client = client

    async def detect(
        self,
        prompt: str,
        num_samples: int = 5
    ) -> HallucinationResult:
        # 1. Generate N responses with temperature > 0
        responses = await self._generate_multiple(prompt, num_samples)

        # 2. Compare responses among themselves
        consistency_score = self._calculate_consistency(responses)

        # 3. Identify inconsistencies
        inconsistencies = self._find_inconsistencies(responses)

        # 4. Generate result
        return HallucinationResult(
            is_hallucinated=consistency_score < 0.7,
            confidence=consistency_score,
            hallucination_type=HallucinationType.CONSISTENCY,
            evidence=inconsistencies,
            severity=self._calculate_severity(consistency_score),
            suggestions=self._generate_suggestions(inconsistencies)
        )

    async def _generate_multiple(
        self,
        prompt: str,
        num_samples: int
    ) -> List[str]:
        # Generate multiple responses with temperature
        # Implement here
        pass

    def _calculate_consistency(self, responses: List[str]) -> float:
        # Calculate semantic similarity between responses
        # Use embeddings or text comparison
        # Return score 0-1
        pass

    def _find_inconsistencies(self, responses: List[str]) -> List[str]:
        # Identify parts that differ between responses
        # These are potential hallucinations
        pass
```

**Tasks**:
- [ ] Implement multiple response generation
- [ ] Calculate semantic similarity (cosine similarity)
- [ ] Identify specific inconsistencies
- [ ] Generate improvement suggestions

### Step 4: Implement LLM-as-Judge

**File: `detectors/llm_judge.py`**

```python
class LLMJudgeDetector:
    """
    Use an LLM to evaluate if another LLM is hallucinating
    """

    JUDGE_PROMPT = """
You are an expert fact-checker. Analyze the following response and determine if it contains hallucinations.

Context (ground truth):
{context}

Response to evaluate:
{response}

Evaluate for:
1. Factual accuracy
2. Information not supported by context
3. Internal contradictions

Respond in JSON format:
{{
  "is_hallucinated": boolean,
  "confidence": 0-1,
  "hallucination_type": "factual|contextual|consistency|none",
  "evidence": ["specific examples"],
  "severity": 0-10,
  "suggestions": ["how to fix"]
}}
"""

    async def detect(
        self,
        response: str,
        context: str | None = None
    ) -> HallucinationResult:
        # 1. Build evaluation prompt
        prompt = self.JUDGE_PROMPT.format(
            context=context or "No context provided",
            response=response
        )

        # 2. Call LLM judge
        judgment = await self._get_judgment(prompt)

        # 3. Parse JSON response
        result = self._parse_judgment(judgment)

        return result
```

**Tasks**:
- [ ] Design effective judge prompt
- [ ] Implement JSON response parsing
- [ ] Handle parsing errors
- [ ] Validate results

### Step 5: Implement Citation Checking

**File: `detectors/citation_checker.py`**

```python
class CitationChecker:
    """
    Verify that claims are supported by citations/context
    """

    async def detect(
        self,
        response: str,
        context: str
    ) -> HallucinationResult:
        # 1. Extract claims from response
        claims = await self._extract_claims(response)

        # 2. For each claim, verify if it's in context
        unsupported = []
        for claim in claims:
            is_supported = await self._verify_claim(claim, context)
            if not is_supported:
                unsupported.append(claim)

        # 3. Calculate score based on % of unsupported claims
        hallucination_rate = len(unsupported) / len(claims)

        return HallucinationResult(
            is_hallucinated=hallucination_rate > 0.2,
            confidence=1.0 - hallucination_rate,
            hallucination_type=HallucinationType.CONTEXTUAL,
            evidence=unsupported,
            severity=int(hallucination_rate * 10),
            suggestions=self._generate_suggestions(unsupported)
        )

    async def _extract_claims(self, text: str) -> List[str]:
        # Use LLM to extract individual claims
        pass

    async def _verify_claim(self, claim: str, context: str) -> bool:
        # Verify if claim is supported by context
        # Use embeddings similarity or LLM
        pass
```

**Tasks**:
- [ ] Implement claim extraction
- [ ] Verify support in context
- [ ] Calculate fidelity metrics
- [ ] Generate specific evidence

### Step 6: Create API Endpoints

**File: `main.py`**

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hallucination Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/detect", response_model=HallucinationResult)
async def detect_hallucination(request: DetectionRequest):
    """
    Detect hallucinations using the specified method
    """
    detector = get_detector(request.detection_method)
    result = await detector.detect(
        text=request.text,
        context=request.context,
        previous_responses=request.previous_responses
    )
    return result

@app.post("/batch-detect")
async def batch_detect(requests: List[DetectionRequest]):
    """
    Detect hallucinations in multiple texts
    """
    results = []
    for req in requests:
        result = await detect_hallucination(req)
        results.append(result)
    return results

@app.get("/methods")
async def list_methods():
    """
    List available detection methods
    """
    return {
        "methods": [
            "self-consistency",
            "llm-judge",
            "citation-checking"
        ]
    }
```

**Tasks**:
- [ ] Implement main endpoints
- [ ] Add input validation
- [ ] Handle errors appropriately
- [ ] Document API with OpenAPI

### Step 7: Testing & Validation

**File: `tests/test_detectors.py`**

```python
import pytest
from detectors import SelfConsistencyDetector, LLMJudgeDetector

# Test cases with known hallucinations
HALLUCINATED_EXAMPLES = [
    {
        "text": "Python was invented in 1985 by Guido van Rossum",
        "context": "Python was created in 1991",
        "expected": True  # Incorrect date
    },
    {
        "text": "The capital of France is Paris",
        "context": "France is a country in Europe",
        "expected": False  # Correct but additional info
    },
]

@pytest.mark.asyncio
async def test_factual_hallucination():
    detector = LLMJudgeDetector(client)

    result = await detector.detect(
        response="Python was invented in 1985",
        context="Python was created in 1991"
    )

    assert result.is_hallucinated == True
    assert result.hallucination_type == HallucinationType.FACTUAL
    assert result.severity > 5

@pytest.mark.asyncio
async def test_self_consistency():
    detector = SelfConsistencyDetector(client)

    result = await detector.detect(
        prompt="What is 2+2?",
        num_samples=5
    )

    # Simple math must be consistent
    assert result.confidence > 0.9
```

**Tasks**:
- [ ] Create complete test suite
- [ ] True positive cases
- [ ] True negative cases
- [ ] Edge cases

## Extra Challenges

### 1. Real-Time Detection
Implement detection in streaming responses:
```python
async def detect_streaming(stream):
    buffer = ""
    async for chunk in stream:
        buffer += chunk
        if should_check(buffer):
            result = await quick_check(buffer)
            if result.is_hallucinated:
                yield StopSignal()
```

### 2. Confidence Calibration
Calibrate confidence scores with ground truth dataset

### 3. Prompt Library
Create library of tested anti-hallucination prompts

### 4. Dashboard
Build dashboard to visualize hallucination rates

## Resources

### Papers
- [Survey of Hallucination in NLP](https://arxiv.org/abs/2202.03629)
- [Self-Consistency Improves CoT](https://arxiv.org/abs/2203.11171)

### Datasets for Testing
- [TruthfulQA](https://github.com/sylinrl/TruthfulQA)
- [HaluEval](https://github.com/RUCAIBox/HaluEval)

### Tools
- [Langfuse (Tracing)](https://langfuse.com/)
- [Guardrails AI](https://github.com/guardrails-ai/guardrails)

## Evaluation

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Detection Accuracy** | 35% | Precision/Recall on test set |
| **Multiple Methods** | 25% | Implement 2+ methods |
| **API Quality** | 20% | Well-designed endpoints |
| **Testing** | 15% | Comprehensive tests |
| **Documentation** | 5% | README + commented code |

**Minimum score**: 70%

## Submission

1. Code on GitHub
2. README with:
   - Explanation of each detection method
   - Evaluation results (precision/recall)
   - Usage examples
3. Deployed API (Railway/Fly.io)
4. Test results (pytest output)

## Reference Solution

- [View solution →](./solution/)

---

**Good luck detecting hallucinations! 🔍**
