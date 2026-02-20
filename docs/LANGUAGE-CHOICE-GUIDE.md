# Language Choice Guide: Python vs TypeScript

This guide helps you choose between Python and TypeScript for the labs in this training program.

---

## Quick Decision Matrix

| If you... | Choose |
|-----------|--------|
| Are new to both languages | **Python** |
| Work primarily on backend/ML | **Python** |
| Work primarily on web frontends | **TypeScript** |
| Want more mature AI tooling | **Python** |
| Need strong type safety | **TypeScript** |
| Plan to use Vercel/Next.js | **TypeScript** |
| Plan to use LangChain extensively | **Python** |
| Want to deploy serverless functions | **TypeScript** |

---

## Detailed Comparison

### Ecosystem Maturity

| Aspect | Python | TypeScript |
|--------|--------|------------|
| LLM SDKs | Excellent | Good |
| Agent frameworks | Many options | Growing |
| Vector databases | Native support | Client libraries |
| Embeddings | Local + API | Mostly API |
| Documentation | Extensive | Improving |

**Python** has a significant head start in AI/ML tooling. Libraries like LangChain, LlamaIndex, and most AI research code are Python-first.

**TypeScript** is catching up rapidly. The Vercel AI SDK is excellent, and all major LLM providers have TypeScript SDKs.

### SDK Equivalents

| Python | TypeScript | Notes |
|--------|------------|-------|
| `anthropic` | `@anthropic-ai/sdk` | Nearly identical API |
| `openai` | `openai` | Identical API |
| `google-generativeai` | `@google/generative-ai` | Similar API |
| `langchain` | `langchain` | Python more feature-complete |
| `chromadb` | `chromadb` | Python more mature |
| `sentence-transformers` | `@xenova/transformers` | Python has more models |

### Web Framework Comparison

| Python | TypeScript | Use Case |
|--------|------------|----------|
| FastAPI | Hono | Lightweight APIs |
| FastAPI | Express | Traditional web servers |
| Pydantic | Zod | Schema validation |
| Django | Next.js | Full-stack frameworks |

### Type Safety

**Python** with type hints:
```python
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

def chat(messages: list[Message]) -> str:
    # Type hints are optional, runtime validation via Pydantic
    ...
```

**TypeScript** with native types:
```typescript
interface Message {
    role: string;
    content: string;
}

function chat(messages: Message[]): Promise<string> {
    // Types are enforced at compile time
    ...
}
```

TypeScript provides stronger compile-time guarantees, while Python relies on runtime validation.

---

## When to Choose Python

### Best For:
1. **Data Science Integration**: If your AI system needs pandas, numpy, or scikit-learn
2. **Local Embeddings**: Running sentence-transformers or other local models
3. **Research/Prototyping**: Most AI papers and tutorials are in Python
4. **LangChain Power Users**: Advanced LangChain features are Python-first
5. **ML Pipeline Integration**: Connecting to ML infrastructure

### Python Advantages:
- More AI/ML libraries and examples
- Local embedding model support
- Jupyter notebook integration
- Larger community for AI-specific questions
- More production deployment examples

### Sample Use Cases:
- RAG systems with custom embedding models
- Multi-agent systems using LangGraph
- Integration with existing ML pipelines
- Research and experimentation

---

## When to Choose TypeScript

### Best For:
1. **Full-Stack Web Apps**: Building AI features into web applications
2. **Vercel Deployment**: Serverless functions and edge deployment
3. **Frontend Integration**: Real-time UI updates from AI responses
4. **API Development**: Type-safe REST APIs
5. **Existing Node.js Stack**: Adding AI to Node.js applications

### TypeScript Advantages:
- Excellent IDE support and autocomplete
- Strong compile-time type checking
- Native async/await patterns
- Easy deployment to Vercel, Cloudflare Workers
- Shared types between frontend and backend

### Sample Use Cases:
- AI chatbots in web applications
- Streaming AI responses to React frontends
- Serverless AI functions
- Type-safe agent tool definitions

---

## Implementation Differences

### Agent Loop

<details>
<summary><b>Python</b></summary>

```python
async def agent_loop(task: str) -> str:
    messages = [{"role": "user", "content": task}]

    while True:
        response = await llm.chat(messages)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = execute_tool(tool_call)
                messages.append({"role": "tool", "content": result})
        else:
            return response.content
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
async function agentLoop(task: string): Promise<string> {
    const messages: Message[] = [{ role: 'user', content: task }];

    while (true) {
        const response = await llm.chat(messages);

        if (response.toolCalls) {
            for (const toolCall of response.toolCalls) {
                const result = executeTool(toolCall);
                messages.push({ role: 'tool', content: result });
            }
        } else {
            return response.content;
        }
    }
}
```

</details>

### Tool Definition

<details>
<summary><b>Python</b></summary>

```python
from pydantic import BaseModel, Field

class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=10, description="Max results")

tools = [{
    "name": "search",
    "description": "Search the web",
    "parameters": SearchParams.model_json_schema()
}]
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
import { z } from 'zod';

const SearchParams = z.object({
    query: z.string().describe("Search query"),
    maxResults: z.number().default(10).describe("Max results")
});

const tools = [{
    name: "search",
    description: "Search the web",
    parameters: zodToJsonSchema(SearchParams)
}];
```

</details>

---

## Performance Considerations

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Cold start | Slower | Faster |
| Async handling | Good (asyncio) | Excellent (native) |
| Memory usage | Higher | Lower |
| CPU-bound tasks | Good | Limited by single-thread |
| I/O-bound tasks | Good | Excellent |

For AI applications (mostly I/O-bound waiting for LLM responses), both perform similarly.

---

## Deployment Options

### Python
- **Railway**: Great for FastAPI apps
- **Render**: Free tier available
- **AWS Lambda**: Via container or Mangum
- **Google Cloud Run**: Container-based

### TypeScript
- **Vercel**: Excellent for serverless
- **Cloudflare Workers**: Edge deployment
- **Railway**: Node.js support
- **AWS Lambda**: Native Node.js runtime

---

## Switching Between Languages

The patterns learned in this training are **language-agnostic**:

1. **Agent loops** work the same way
2. **Tool calling** follows identical patterns
3. **RAG pipelines** have the same architecture
4. **Evaluation metrics** are computed identically

If you learn in Python, you can easily apply the same concepts in TypeScript (and vice versa).

---

## Recommendations by Day

| Day | Topic | Recommendation |
|-----|-------|----------------|
| Day 1 | Foundations | Either |
| Day 2 | Prompting | Either |
| Day 3 | Agents | Either |
| Day 4 | RAG | Python (local embeddings) or TypeScript (API embeddings) |
| Day 5 | Production | Match your deployment target |

---

## Final Advice

**Start with what you know.** If you're comfortable with Python, use Python. If you're a TypeScript developer, use TypeScript.

**Don't stress the choice.** The core concepts transfer between languages. Pick one, complete the training, and you'll be able to apply what you learned in any language.

**Consider your deployment target.** If you know you'll deploy to Vercel, TypeScript makes sense. If you're deploying to a traditional server or need ML integration, Python is likely better.
