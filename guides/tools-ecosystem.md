# 🛠️ Tools & Ecosystem Guide

Comprehensive guide to the tools, frameworks, and libraries for building AI applications. From LLM providers to deployment platforms, this is your complete toolkit.

---

## 📋 Table of Contents

- [LLM Providers](#llm-providers)
- [Agent Frameworks](#agent-frameworks)
- [Vector Databases](#vector-databases)
- [Embedding Models](#embedding-models)
- [Development Frameworks](#development-frameworks)
- [Observability & Monitoring](#observability--monitoring)
- [Testing & Evaluation](#testing--evaluation)
- [Deployment Platforms](#deployment-platforms)
- [AI-Assisted Coding](#ai-assisted-coding)
- [Utilities & Libraries](#utilities--libraries)

---

## 🤖 LLM Providers

### Commercial APIs

| Provider | Models | Best For | Pricing | Docs |
|----------|--------|----------|---------|------|
| **Anthropic** | Claude 3.5 Sonnet, Haiku, Opus | Long context, analysis, coding | $3-15/MTok | [docs.anthropic.com](https://docs.anthropic.com/) |
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | General purpose, function calling | $0.15-60/MTok | [platform.openai.com](https://platform.openai.com/) |
| **Google** | Gemini 1.5 Pro, Flash | Multimodal, long context | $1.25-7/MTok | [ai.google.dev](https://ai.google.dev/) |
| **Cohere** | Command R+, Embed v3 | RAG, embeddings, multilingual | $0.15-15/MTok | [docs.cohere.com](https://docs.cohere.com/) |
| **Groq** | Llama 3, Mixtral | Ultra-fast inference | $0.05-0.7/MTok | [console.groq.com](https://console.groq.com/) |
| **Together AI** | Llama 3, Mixtral, many others | Open source models | $0.18-1.1/MTok | [docs.together.ai](https://docs.together.ai/) |

### Open Source Models

| Model | Size | Best For | License | Link |
|-------|------|----------|---------|------|
| **Llama 3.1** | 8B-405B | General purpose | Llama 3 | [meta.ai](https://www.llama.com/) |
| **Mixtral 8x7B** | 47B | Efficient MoE | Apache 2.0 | [mistral.ai](https://mistral.ai/) |
| **Phi-3** | 3.8B-14B | Small, efficient | MIT | [microsoft](https://huggingface.co/microsoft/phi-3-mini-4k-instruct) |
| **Gemma** | 2B-7B | Lightweight | Gemma Terms | [google](https://ai.google.dev/gemma) |
| **Code Llama** | 7B-34B | Code generation | Llama 2 | [meta](https://github.com/facebookresearch/codellama) |

### Model Routers & Gateways

**[LiteLLM](https://docs.litellm.ai/)**
```python
from litellm import completion

# Unified interface for all providers
response = completion(
    model="claude-3-5-sonnet-20241022",  # or gpt-4, gemini-pro
    messages=[{"role": "user", "content": "Hello"}]
)
```
- ✅ 100+ LLMs, one interface
- ✅ Load balancing, fallbacks
- ✅ Cost tracking
- ✅ Caching support

**[OpenRouter](https://openrouter.ai/)**
- Access 150+ models through one API
- Auto-routing to cheapest/fastest
- Pay-per-use, no subscriptions
- [Documentation](https://openrouter.ai/docs)

**[Portkey](https://portkey.ai/)**
- Gateway for LLM applications
- Automatic failover
- Cost & latency optimization
- [Documentation](https://docs.portkey.ai/)

---

## 🤖 Agent Frameworks

### LangChain / LangGraph

**[LangChain](https://python.langchain.com/)** - Most popular LLM framework

```python
from langchain.chat_models import ChatAnthropic
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool

# Create agent with tools
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
tools = [Tool(name="Calculator", func=calculator, description="Do math")]
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
```

**Key Features**:
- ✅ 1000+ integrations
- ✅ Memory management
- ✅ Tool/function calling
- ✅ RAG components
- ✅ Multi-modal support

**[LangGraph](https://langchain-ai.github.io/langgraph/)** - Build agent workflows as graphs

```python
from langgraph.graph import StateGraph

# Define agent graph
workflow = StateGraph()
workflow.add_node("researcher", research_agent)
workflow.add_node("writer", writer_agent)
workflow.add_edge("researcher", "writer")
app = workflow.compile()
```

**Ecosystem Tools**:
- **[LangSmith](https://smith.langchain.com/)** - Debug and monitor
- **[LangServe](https://github.com/langchain-ai/langserve)** - Deploy as APIs
- **[LangChain Templates](https://github.com/langchain-ai/langchain/tree/master/templates)** - Pre-built apps

### LlamaIndex

**[LlamaIndex](https://docs.llamaindex.ai/)** - RAG-focused framework

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader

# Build RAG system
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is this about?")
```

**Key Features**:
- ✅ Best-in-class RAG
- ✅ 160+ data connectors
- ✅ Advanced retrieval strategies
- ✅ Query optimization
- ✅ Graph-based retrieval

**Related Tools**:
- **[LlamaParse](https://github.com/run-llama/llama_parse)** - Parse complex documents
- **[LlamaHub](https://llamahub.ai/)** - Data loaders

### Other Agent Frameworks

**[Semantic Kernel (Microsoft)](https://learn.microsoft.com/en-us/semantic-kernel/)**
```csharp
var kernel = Kernel.Builder.Build();
kernel.ImportSkill(new MySkills(), "MySkills");
var result = await kernel.RunAsync("Summarize this", myFunction);
```
- C#, Python, Java support
- Enterprise-focused
- Azure integration

**[AutoGen (Microsoft)](https://microsoft.github.io/autogen/)**
```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent("assistant")
user_proxy = UserProxyAgent("user")
user_proxy.initiate_chat(assistant, message="Plot stock prices")
```
- Multi-agent conversations
- Human-in-the-loop
- Code execution

**[CrewAI](https://github.com/joaomdmoura/crewAI)**
```python
from crewai import Agent, Task, Crew

researcher = Agent(role="Researcher", goal="Research topics")
writer = Agent(role="Writer", goal="Write articles")
task = Task(description="Write about AI", agent=writer)
crew = Crew(agents=[researcher, writer], tasks=[task])
result = crew.kickoff()
```
- Role-based agents
- Task delegation
- Simple API

**[Haystack](https://haystack.deepset.ai/)**
- NLP-focused framework
- Advanced RAG
- Question answering
- Document search

---

## 🗄️ Vector Databases

### Managed Solutions

**[Pinecone](https://www.pinecone.io/)**
```python
import pinecone

pinecone.init(api_key="...")
index = pinecone.Index("my-index")
index.upsert(vectors=[("id1", [0.1, 0.2, ...], {"text": "..."})])
results = index.query(vector=[0.1, 0.2, ...], top_k=5)
```
- ✅ Fully managed
- ✅ Auto-scaling
- ✅ Hybrid search
- ✅ Metadata filtering
- 💰 $0.096/GB/month

**[Weaviate](https://weaviate.io/)**
```python
import weaviate

client = weaviate.Client("http://localhost:8080")
client.data_object.create(
    data_object={"text": "..."},
    class_name="Document"
)
result = client.query.get("Document", ["text"]).with_near_vector({
    "vector": [0.1, 0.2, ...]
}).do()
```
- ✅ Open source
- ✅ GraphQL API
- ✅ Multimodal support
- ✅ Managed cloud option

### Self-Hosted

**[Qdrant](https://qdrant.tech/)**
```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
client.upsert(
    collection_name="docs",
    points=[{
        "id": 1,
        "vector": [0.1, 0.2, ...],
        "payload": {"text": "..."}
    }]
)
results = client.search(collection_name="docs", query_vector=[0.1, 0.2, ...])
```
- ✅ Rust-based (fast)
- ✅ Rich filtering
- ✅ Quantization
- ✅ Managed cloud available

**[Milvus](https://milvus.io/)**
- Built for scale (billions of vectors)
- GPU acceleration
- Kubernetes-native
- Zilliz Cloud (managed)

**[ChromaDB](https://www.trychroma.com/)**
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("docs")
collection.add(
    documents=["doc1", "doc2"],
    ids=["id1", "id2"]
)
results = collection.query(query_texts=["search"], n_results=5)
```
- ✅ Embedded (no server)
- ✅ Python-native
- ✅ Great for prototyping
- ✅ Auto-embedding

### PostgreSQL Extensions

**[pgvector](https://github.com/pgvector/pgvector)**
```sql
CREATE EXTENSION vector;
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(1536));
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops);
SELECT * FROM items ORDER BY embedding <-> '[0.1,0.2,...]' LIMIT 5;
```
- ✅ Use existing Postgres
- ✅ ACID guarantees
- ✅ Join with relational data
- ✅ Familiar SQL interface

### Comparison Matrix

| Database | Type | Best For | Complexity | Scaling |
|----------|------|----------|------------|---------|
| Pinecone | Managed | Production, no ops | Low | Auto |
| Weaviate | Open/Managed | Flexibility | Medium | Manual/Auto |
| Qdrant | Open/Managed | Performance | Medium | Manual/Auto |
| Milvus | Open/Managed | Massive scale | High | Manual/Auto |
| ChromaDB | Embedded | Prototyping | Very Low | Limited |
| pgvector | Extension | Existing Postgres | Low | Postgres scaling |

---

## 📊 Embedding Models

### Closed Source (APIs)

**[OpenAI text-embedding-3](https://platform.openai.com/docs/guides/embeddings)**
```python
from openai import OpenAI

client = OpenAI()
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Your text here"
)
embedding = response.data[0].embedding  # 3072 dimensions
```
- Small: 1536 dims, $0.02/MTok
- Large: 3072 dims, $0.13/MTok
- SOTA performance

**[Cohere Embed v3](https://docs.cohere.com/docs/embeddings)**
```python
import cohere

co = cohere.Client("...")
response = co.embed(
    texts=["text1", "text2"],
    model="embed-english-v3.0",
    input_type="search_document"
)
embeddings = response.embeddings
```
- Multilingual (100+ languages)
- Input type optimization
- $0.10/MTok

**[Voyage AI](https://docs.voyageai.com/)**
- Domain-specific models
- Code, finance, law
- Better than OpenAI for specialized domains

### Open Source Models

**[Sentence Transformers](https://www.sbert.net/)**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["sentence 1", "sentence 2"])
```
- 5000+ models on Hugging Face
- Easy fine-tuning
- CPU-friendly options

**Top Performers** (MTEB Leaderboard):
1. **[gte-Qwen2-7B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-7B-instruct)** - 7B params, SOTA
2. **[bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5)** - 335M params, excellent
3. **[e5-mistral-7b-instruct](https://huggingface.co/intfloat/e5-mistral-7b-instruct)** - 7B params, very strong
4. **[all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)** - 110M params, balanced

**Specialized Embeddings**:
- **[nomic-embed-text](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)** - Long context (8192 tokens)
- **[jina-embeddings-v2](https://huggingface.co/jinaai/jina-embeddings-v2-base-en)** - 8192 context, multilingual
- **[instructor-xl](https://huggingface.co/hkunlp/instructor-xl)** - Instruction-based

### Choosing an Embedding Model

| Priority | Recommendation |
|----------|----------------|
| **Best Quality** | OpenAI text-embedding-3-large |
| **Best Value** | OpenAI text-embedding-3-small |
| **Open Source SOTA** | gte-Qwen2-7B-instruct |
| **Balanced** | bge-large-en-v1.5 |
| **Fast/Lightweight** | all-MiniLM-L6-v2 |
| **Multilingual** | Cohere embed-multilingual-v3.0 |
| **Long Context** | nomic-embed-text-v1.5 |

---

## 💻 Development Frameworks

### Backend Frameworks

**[FastAPI](https://fastapi.tiangolo.com/)** (Python)
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/chat")
async def chat(query: Query):
    response = llm.complete(query.text)
    return {"response": response}
```
- ✅ Async support
- ✅ Auto OpenAPI docs
- ✅ Type safety
- ✅ Great for AI APIs

**[Hono](https://hono.dev/)** (TypeScript)
```typescript
import { Hono } from 'hono'

const app = new Hono()

app.post('/chat', async (c) => {
  const { text } = await c.req.json()
  const response = await llm.complete(text)
  return c.json({ response })
})
```
- ✅ Ultra-fast
- ✅ Edge runtime support
- ✅ TypeScript-first
- ✅ Cloudflare Workers

### Frontend Frameworks

**[Vercel AI SDK](https://sdk.vercel.ai/)**
```typescript
import { useChat } from 'ai/react'

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat()

  return (
    <form onSubmit={handleSubmit}>
      {messages.map(m => <div key={m.id}>{m.content}</div>)}
      <input value={input} onChange={handleInputChange} />
    </form>
  )
}
```
- ✅ React hooks for AI
- ✅ Streaming support
- ✅ Tool/function calling
- ✅ Edge runtime

**[Chatbot UI](https://github.com/mckaywrigley/chatbot-ui)**
- Open source ChatGPT clone
- Next.js + Tailwind
- Supabase backend
- Fork and customize

**[Streamlit](https://streamlit.io/)**
```python
import streamlit as st

st.title("My AI App")
prompt = st.text_input("Enter prompt")
if st.button("Generate"):
    response = llm.complete(prompt)
    st.write(response)
```
- ✅ Python-only, no JS
- ✅ Rapid prototyping
- ✅ Built-in components
- ✅ Easy deployment

---

## 📊 Observability & Monitoring

### LLM-Specific Observability

**[LangSmith](https://smith.langchain.com/)**
```python
import langsmith

client = langsmith.Client()
with langsmith.trace("my-chain") as run:
    result = my_chain.run(input)
```
- Debug LangChain apps
- Trace every LLM call
- Evaluate outputs
- $39/month after free tier

**[Helicone](https://www.helicone.ai/)**
```python
# Just change the base URL
import openai

openai.api_base = "https://oai.hconeai.com/v1"
openai.default_headers = {"Helicone-Auth": "Bearer sk-..."}
```
- Zero code changes
- Cost tracking
- Latency monitoring
- Caching support
- Free tier available

**[Phoenix by Arize](https://phoenix.arize.com/)**
```python
import phoenix as px

px.launch_app()
# Auto-instruments LangChain, LlamaIndex
```
- Open source
- Embedding visualization
- Trace analysis
- Local-first

**[LangFuse](https://langfuse.com/)**
```python
from langfuse import Langfuse

langfuse = Langfuse()
trace = langfuse.trace(name="my-generation")
trace.generation(name="gpt-4", input="...", output="...")
```
- Open source alternative to LangSmith
- Self-hostable
- Cost tracking
- Prompt management

### Traditional Monitoring

**[Datadog](https://www.datadoghq.com/)**
- Full-stack observability
- LLM cost tracking
- Custom dashboards
- Alerting

**[Grafana + Prometheus](https://grafana.com/)**
- Open source
- Time-series metrics
- Custom dashboards
- Self-hosted

**[Sentry](https://sentry.io/)**
- Error tracking
- Performance monitoring
- Release tracking
- Great free tier

---

## 🧪 Testing & Evaluation

### LLM Evaluation Frameworks

**[RAGAS](https://docs.ragas.io/)**
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

result = evaluate(
    dataset=my_dataset,
    metrics=[faithfulness, answer_relevancy]
)
```
- RAG-specific metrics
- Faithfulness, relevancy, context recall
- Works with any RAG system

**[DeepEval](https://docs.confident-ai.com/)**
```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(threshold=0.7)
assert_test(test_case, [metric])
```
- Unit testing for LLMs
- Pytest integration
- 14+ metrics
- CI/CD friendly

**[TruLens](https://www.trulens.org/)**
```python
from trulens_eval import TruChain, Feedback

feedback = Feedback(provider.relevance).on_output()
tru_recorder = TruChain(my_chain, feedbacks=[feedback])
```
- Track app quality
- Ground truth comparison
- Dashboard for analysis

### Prompt Testing

**[Promptfoo](https://www.promptfoo.dev/)**
```yaml
# promptfooconfig.yaml
prompts:
  - "Summarize: {{text}}"
providers:
  - openai:gpt-4
  - anthropic:claude-3-5-sonnet
tests:
  - vars:
      text: "Long article..."
    assert:
      - type: contains
        value: "summary"
```
- Test prompts systematically
- Compare models
- Regression testing
- CLI and web UI

**[Giskard](https://github.com/Giskard-AI/giskard)**
- ML model testing
- Detect vulnerabilities
- Bias detection
- Performance testing

### Load Testing

**[Locust](https://locust.io/)**
```python
from locust import HttpUser, task

class AIUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/chat", json={"message": "Hello"})
```
- Python-based load testing
- Distributed testing
- Real-time web UI

---

## 🚀 Deployment Platforms

### Serverless / PaaS

**[Vercel](https://vercel.com/)**
- Next.js native
- Edge functions
- AI SDK support
- $20/month hobby

**[Railway](https://railway.app/)**
- Any language/framework
- PostgreSQL, Redis included
- $5/month starter
- Easy Docker deployment

**[Render](https://render.com/)**
- Web services, databases
- Auto-deploy from Git
- Free tier available
- Background workers

**[Modal](https://modal.com/)**
```python
import modal

stub = modal.Stub()

@stub.function(gpu="A10G")
def run_llm(prompt):
    # Your code here with GPU
    pass
```
- Run code in cloud with GPUs
- Pay per second
- Great for ML workloads

### Container Platforms

**[Fly.io](https://fly.io/)**
- Global app deployment
- Docker-based
- Edge locations
- GPU support

**[Google Cloud Run](https://cloud.google.com/run)**
- Serverless containers
- Auto-scaling
- Pay per request
- Easy CI/CD

**[AWS Lambda](https://aws.amazon.com/lambda/)**
- Serverless functions
- Huge free tier
- Complex pricing
- Cold start issues

### ML-Specific Platforms

**[Replicate](https://replicate.com/)**
```python
import replicate

output = replicate.run(
    "stability-ai/sdxl",
    input={"prompt": "a cat"}
)
```
- Run ML models via API
- 1000s of models
- Pay per second
- No infrastructure

**[Hugging Face Spaces](https://huggingface.co/spaces)**
- Host ML apps for free
- Gradio/Streamlit support
- GPU upgrades available
- Great for demos

---

## 💡 AI-Assisted Coding

### AI-Powered IDEs

**[Cursor](https://cursor.sh/)**
- VS Code fork with AI
- Cmd+K for inline edits
- Composer for multi-file
- $20/month

**[Windsurf](https://codeium.com/windsurf)**
- Agentic coding assistant
- Cascade mode (autonomous)
- Free for individuals
- VS Code alternative

### IDE Extensions

**[GitHub Copilot](https://github.com/features/copilot)**
```typescript
// Type comment, get code
// function to calculate fibonacci sequence
// [Copilot suggests implementation]
```
- $10/month individual
- Works in VS Code, JetBrains, etc.
- Code completion + chat
- Context from workspace

**[Codeium](https://codeium.com/)**
- Free Copilot alternative
- 70+ languages
- VS Code, JetBrains, etc.
- Chat + autocomplete

**[Continue.dev](https://continue.dev/)**
- Open source autopilot
- Any LLM (local or API)
- Highly customizable
- Free

**[Cody by Sourcegraph](https://sourcegraph.com/cody)**
- Code intelligence
- Explain code
- Generate tests
- Find references

### Terminal AI

**[Aider](https://aider.chat/)**
```bash
aider --model claude-3-5-sonnet-20241022
# Chat with your codebase in terminal
```
- AI pair programming in CLI
- Git integration
- Multiple file editing
- Works with any LLM

**[GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli)**
```bash
?? "find all large files"
# Suggests: find . -type f -size +100M
```
- AI for shell commands
- Explain commands
- Convert natural language to CLI

---

## 🔧 Utilities & Libraries

### PDF & Document Processing

**[LlamaParse](https://github.com/run-llama/llama_parse)**
- Best PDF parser
- Handles tables, images
- $0.003 per page
- API-based

**[Unstructured](https://unstructured.io/)**
```python
from unstructured.partition.auto import partition

elements = partition("document.pdf")
```
- Parse any document type
- PDF, Word, HTML, etc.
- Extract structure
- Open source

**[PyMuPDF](https://pymupdf.readthedocs.io/)**
- Fast PDF processing
- Text extraction
- Image extraction
- Free

### Prompt Management

**[PromptLayer](https://promptlayer.com/)**
- Version control for prompts
- A/B testing
- Analytics
- $50/month starter

**[Humanloop](https://humanloop.com/)**
- Prompt playground
- Evaluation tools
- Feedback collection
- $500/month starter

### Token Counting

**[tiktoken](https://github.com/openai/tiktoken)** (OpenAI)
```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
tokens = enc.encode("Your text here")
count = len(tokens)
```

**[anthropic-tokenizer](https://github.com/anthropics/anthropic-tokenizer-typescript)** (Anthropic)
```typescript
import { countTokens } from '@anthropic-ai/tokenizer'

const count = countTokens('Your text here')
```

### Structured Output

**[Pydantic](https://docs.pydantic.dev/)** (Python)
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

user = User(**llm_output)  # Validates automatically
```

**[Zod](https://zod.dev/)** (TypeScript)
```typescript
import { z } from 'zod'

const User = z.object({
  name: z.string(),
  age: z.number(),
  email: z.string().email()
})

const user = User.parse(llmOutput)
```

**[Instructor](https://github.com/jxnl/instructor)**
```python
import instructor
from openai import OpenAI

client = instructor.patch(OpenAI())

user = client.chat.completions.create(
    model="gpt-4",
    response_model=User,
    messages=[{"role": "user", "content": "Extract: John, 30, john@example.com"}]
)
```
- Structured outputs from LLMs
- Automatic retry on validation error
- Works with OpenAI, Anthropic, etc.

---

## 📦 Package Managers & Tools

### Python Environment

**[uv](https://github.com/astral-sh/uv)**
- 10-100x faster than pip
- Drop-in replacement
- Built in Rust
- `uv pip install langchain`

**[Poetry](https://python-poetry.org/)**
- Dependency management
- Virtual environments
- Package publishing
- `poetry add langchain`

### Node.js / TypeScript

**[pnpm](https://pnpm.io/)**
- Fast, disk-efficient
- Better than npm/yarn
- Monorepo support
- `pnpm add ai`

---

## 🎯 Choosing Your Stack

**Use this decision framework based on your stage and needs:**

### For Rapid Prototyping (Week 1-2)
**Goal:** Validate idea quickly, iterate fast, minimize setup

- **LLM**: Claude 3.5 Sonnet (best quality/speed balance)
- **Framework**: Raw API or LangChain (avoid over-engineering)
- **Vector DB**: ChromaDB (embedded, zero setup)
- **Frontend**: Streamlit (Python-only, instant UI)
- **Deployment**: None (local development)
- **Cost**: $20-50/month in API costs

**Why this stack:**
- ✅ Set up in < 1 hour
- ✅ No infrastructure management
- ✅ Focus on core logic, not devops
- ❌ Not production-ready
- ❌ Single-user only

### For Production MVP (Month 1-3)
**Goal:** Launch to real users, handle 100-1K users, stay reliable

- **LLM**: Claude 3.5 Sonnet + Haiku (quality + cost optimization)
- **Framework**: LangChain or LlamaIndex (battle-tested patterns)
- **Vector DB**: Pinecone or Qdrant Cloud (managed, scales automatically)
- **Backend**: FastAPI (fast, production-ready Python)
- **Frontend**: Next.js + Vercel AI SDK (modern, streaming support)
- **Deployment**: Vercel (frontend) + Railway (backend)
- **Monitoring**: Helicone (simple, affordable)
- **Cost**: $200-500/month (infra + API)

**Why this stack:**
- ✅ Production-ready out of the box
- ✅ Scales to 1K-10K users without changes
- ✅ Good monitoring and debugging
- ✅ Managed services = less operational burden
- ❌ Higher cost than self-hosted
- ❌ Vendor lock-in to some extent

### For Enterprise Scale (Month 6+)
**Goal:** Handle 10K+ users, multi-tenancy, compliance, high reliability

- **LLM**: Multiple providers with LiteLLM (redundancy + cost optimization)
- **Framework**: Custom or LangChain (more control at scale)
- **Vector DB**: Weaviate or Milvus (self-hosted for data sovereignty)
- **Backend**: FastAPI + Kubernetes (horizontal scaling)
- **Frontend**: Next.js (proven at scale)
- **Deployment**: AWS/GCP/Azure (full control, compliance)
- **Monitoring**: Datadog + LangSmith (enterprise features)
- **Queue**: Kafka or RabbitMQ (async processing)
- **Cost**: $2K-10K+/month (scales with usage)

**Why this stack:**
- ✅ Scales to millions of users
- ✅ Full control and customization
- ✅ Multi-region deployment
- ✅ Compliance-ready (SOC 2, HIPAA, etc.)
- ❌ Requires dedicated DevOps team
- ❌ High operational complexity
- ❌ Expensive infrastructure

### Quick Decision Tree

```
How many users?
├─ Just me / testing → Prototyping Stack
├─ 10-1K users → MVP Stack
└─ 10K+ users → Enterprise Stack

What's your budget?
├─ < $100/month → Prototyping Stack (local + free tiers)
├─ $100-1K/month → MVP Stack (managed services)
└─ $1K+/month → Enterprise Stack (self-hosted options)

What's your timeline?
├─ Launch in days → Prototyping Stack (Streamlit)
├─ Launch in weeks → MVP Stack (Next.js + managed services)
└─ Launch in months → Enterprise Stack (custom build)

What's your team size?
├─ Solo developer → Prototyping/MVP Stack
├─ 2-5 engineers → MVP Stack
└─ 10+ engineers → Enterprise Stack
```

---

## 🆚 Decision Matrices

### Agent Framework Selection

| Choose | If You Need |
|--------|-------------|
| **LangChain** | Widest ecosystem, most integrations |
| **LlamaIndex** | Best-in-class RAG, data connectors |
| **Custom** | Full control, specific requirements |
| **AutoGen** | Multi-agent conversations |
| **CrewAI** | Simple agent orchestration |

### Vector DB Selection

| Choose | If You Need |
|--------|-------------|
| **Pinecone** | Zero ops, managed, auto-scaling |
| **Weaviate** | Open source, GraphQL, flexibility |
| **Qdrant** | Best performance, self-hosted |
| **ChromaDB** | Embedded, prototyping, simple |
| **pgvector** | Already using Postgres |

### Deployment Platform Selection

| Choose | If You Need |
|--------|-------------|
| **Vercel** | Next.js, edge functions, simplicity |
| **Railway** | Any framework, PostgreSQL included |
| **Modal** | GPU access, ML workloads |
| **AWS/GCP** | Enterprise scale, existing cloud |

---

## 📚 Related Guides

- [RESOURCES.md](RESOURCES.md) - Links and documentation
- [LEARNING-PATHS.md](LEARNING-PATHS.md) - Structured learning roadmaps
- [RECOMMENDED-READING.md](RECOMMENDED-READING.md) - Papers and articles
- [COMMUNITY.md](COMMUNITY.md) - Communities and forums

---

**Last Updated**: 2026-01-08

*This ecosystem evolves rapidly. Check back regularly for updates!*
