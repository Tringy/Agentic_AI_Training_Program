# Free-Tier Strategy Guide

## Making This Training 100% Free for Students

This document outlines how to run the entire Agentic AI Intensive Training Program at **zero cost** using free tiers, open-source tools, and local models.

---

## Executive Summary: Cost Audit Results

### Current Cost Dependencies Identified

| Component | Current Approach | Est. Cost/Week | Free Alternative |
|-----------|------------------|----------------|------------------|
| LLM APIs | OpenAI/Anthropic paid | $20-60 | Google AI Studio, Groq, Ollama |
| Embeddings | OpenAI text-embedding-3-small | $2-5 | Sentence Transformers (local) |
| AI Coding Tools | Cursor Pro, GitHub Copilot | $20-40/mo | Cursor Free, Continue, Antigravity |
| Deployment (Backend) | Railway ($5-20/mo) | $5-20 | Render Free, HuggingFace Spaces |
| Deployment (Frontend) | Vercel (free tier OK) | $0 | Vercel Free, Netlify |
| Vector DB | ChromaDB (already free) | $0 | ChromaDB local |
| **Total Original** | | **$47-125/week** | |
| **Total Free** | | **$0** | |

---

## 1. Free LLM API Alternatives

### Tier 1: Recommended Free Options

#### Google AI Studio (Gemini) - BEST FREE OPTION
```
URL: https://aistudio.google.com/
Free Tier:
  - Gemini 1.5 Flash: 15 RPM, 1M TPM, 1500 RPD
  - Gemini 1.5 Pro: 2 RPM, 32K TPM, 50 RPD
  - FREE for development use
```

**Why it's ideal for training:**
- Most generous free tier
- High-quality models
- Works with standard OpenAI-compatible API patterns
- No credit card required

**Setup:**
```python
# Using Google AI Studio
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Your prompt here")
```

#### Groq - FASTEST FREE OPTION
```
URL: https://console.groq.com/
Free Tier:
  - Llama 3.1 70B: 30 RPM, 6000 TPM
  - Mixtral 8x7B: 30 RPM, 5000 TPM
  - FREE for development
```

**Why it's ideal for training:**
- Extremely fast inference (great for iterative learning)
- Runs Llama and Mixtral models
- OpenAI-compatible API
- No credit card required

**Setup:**
```python
# Using Groq (OpenAI-compatible)
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

#### Ollama - COMPLETELY LOCAL/OFFLINE
```
URL: https://ollama.ai/
Cost: FREE (runs on your machine)
Models: Llama 3.1, Mistral, CodeLlama, Gemma 2, etc.
Requirements: 8GB+ RAM for small models, 16GB+ for larger
```

**Why it's ideal for training:**
- Zero API costs ever
- Works offline
- Good for privacy-sensitive scenarios
- Great for teaching local deployment concepts

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b
ollama pull codellama:7b

# Run (OpenAI-compatible API on localhost:11434)
ollama serve
```

```python
# Using Ollama with OpenAI client
from openai import OpenAI

client = OpenAI(
    api_key="ollama",  # Can be anything
    base_url="http://localhost:11434/v1"
)

response = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

### Tier 2: Additional Free Options

| Provider | Free Tier | Models | Notes |
|----------|-----------|--------|-------|
| **Anthropic** | $5 credit (new accounts) | Claude 3 Haiku | Limited but good for demos |
| **OpenAI** | $5 credit (new accounts) | GPT-3.5 | Limited but familiar API |
| **Mistral** | Free tier available | Mistral Small | Good quality |
| **Cohere** | 1000 calls/month | Command | Good for embeddings too |
| **Together AI** | $25 free credit | Various | Many open models |
| **OpenRouter** | Pay-per-use with free models | Various | Aggregates many providers |

### Universal LLM Client (Free-Tier Compatible)

Replace the current `llm_client.py` with this free-tier compatible version:

```python
# llm_client_free.py
"""LLM client with free-tier providers."""
import os
from abc import ABC, abstractmethod
from typing import List, Dict

class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict]) -> str:
        pass

class GoogleAIClient(LLMClient):
    """Google AI Studio client - Best free option."""

    def __init__(self, model: str = "gemini-1.5-flash"):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)

    def chat(self, messages: List[Dict]) -> str:
        # Convert messages to Gemini format
        prompt_parts = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            prompt_parts.append({"role": role, "parts": [msg["content"]]})

        response = self.model.generate_content(prompt_parts)
        return response.text

class GroqClient(LLMClient):
    """Groq client - Fast free inference."""

    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = model

    def chat(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

class OllamaClient(LLMClient):
    """Ollama client - Completely local/free."""

    def __init__(self, model: str = "llama3.1:8b"):
        from openai import OpenAI
        self.client = OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )
        self.model = model

    def chat(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

def get_free_llm_client(provider: str = "google") -> LLMClient:
    """Get a free-tier LLM client."""
    providers = {
        "google": GoogleAIClient,
        "groq": GroqClient,
        "ollama": OllamaClient,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Use: {list(providers.keys())}")

    return providers[provider]()
```

---

## 2. Free Embedding Alternatives

### Current Problem
Labs use OpenAI's `text-embedding-3-small` ($0.02/1M tokens) which requires payment.

### Free Solutions

#### Option A: Sentence Transformers (Local - RECOMMENDED)
```python
# Free, local embeddings
from sentence_transformers import SentenceTransformer

# One-time download, then free forever
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
# OR for better quality:
model = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions

embeddings = model.encode(["Your text here"])
```

**ChromaDB Integration (Updated):**
```python
# rag/vector_store_free.py
import chromadb
from chromadb.utils import embedding_functions

class CodebaseVectorStoreFree:
    def __init__(self, collection_name: str = "codebase"):
        self.client = chromadb.PersistentClient(path="./chroma_db")

        # Use FREE local embeddings instead of OpenAI
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
```

#### Option B: HuggingFace Free Inference API
```python
# Limited free tier, but no local GPU needed
import requests

API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def get_embeddings(texts):
    response = requests.post(API_URL, headers=headers, json={"inputs": texts})
    return response.json()
```

#### Option C: Google's Free Embedding API
```python
# google-generativeai includes free embeddings
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

result = genai.embed_content(
    model="models/embedding-001",
    content="Your text here"
)
```

---

## 3. Free AI Coding Tools

### Completely Free Options

| Tool | Type | Cost | Features |
|------|------|------|----------|
| **Cursor (Free Tier)** | IDE | $0 | 2000 completions/month, 50 slow requests |
| **Continue** | VSCode Extension | $0 | Open source, use any model (including local) |
| **Antigravity** | CLI/VSCode | $0 | Free tier available, AI-powered coding |
| **Codeium** | IDE Extension | $0 | Free for individuals, unlimited completions |
| **Tabby** | Self-hosted | $0 | Open source, run locally |
| **Aider** | CLI | $0* | Open source, bring your own API key |
| **Claude Code** | CLI | $0* | Use with free API tier |

### Recommended Setup for Training

#### Option 1: Cursor Free Tier
- 2000 completions/month is sufficient for 1-week training
- Familiar IDE experience
- No setup required

#### Option 2: Continue + Ollama (100% Free Forever)
```bash
# Install Continue extension in VSCode
# Configure to use Ollama

# In Continue settings (~/.continue/config.json):
{
  "models": [
    {
      "title": "Ollama - Llama 3.1",
      "provider": "ollama",
      "model": "llama3.1:8b"
    },
    {
      "title": "Ollama - CodeLlama",
      "provider": "ollama",
      "model": "codellama:7b"
    }
  ]
}
```

#### Option 3: Codeium (Unlimited Free)
- Completely free for individuals
- Works in VSCode, JetBrains, Vim, etc.
- No token limits
- Good quality completions

---

## 4. Free Deployment Platforms

### Frontend Deployment (All Free)

| Platform | Free Tier | Limits | Best For |
|----------|-----------|--------|----------|
| **Vercel** | Yes | 100GB bandwidth, serverless limits | Next.js, React |
| **Netlify** | Yes | 100GB bandwidth, 300 build mins | Static sites, React |
| **Cloudflare Pages** | Yes | Unlimited bandwidth! | Any frontend |
| **GitHub Pages** | Yes | 100GB bandwidth | Static sites |

**Recommendation:** Vercel free tier is MORE than sufficient for training labs.

### Backend Deployment (Free Options)

| Platform | Free Tier | Limits | Best For |
|----------|-----------|--------|----------|
| **Render** | Yes | 750 hours/month, spins down after 15 min idle | FastAPI, Python |
| **HuggingFace Spaces** | Yes | 2 vCPU, 16GB RAM (CPU) | ML apps, Gradio |
| **Railway** | $5/month credit | Limited free resources | Full-stack |
| **Fly.io** | Yes | 3 shared VMs, 160GB bandwidth | Global distribution |
| **Deta Space** | Yes | Generous free tier | Python, Node.js |
| **Koyeb** | Yes | 1 nano instance | Simple deployments |

### Recommended: Render Free Tier

```yaml
# render.yaml
services:
  - type: web
    name: ai-training-backend
    env: python
    plan: free  # FREE PLAN!
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Note:** Free tier services spin down after 15 minutes of inactivity. First request after idle takes ~30 seconds. This is fine for training purposes.

### Alternative: HuggingFace Spaces (Great for AI Apps)

```yaml
# README.md in your HF Space
---
title: AI Training Lab
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio  # or docker
app_port: 7860
---
```

HuggingFace Spaces advantages:
- Built for ML/AI applications
- Free GPU for some models!
- Great community
- Easy sharing

---

## 5. Updated Environment File (.env.free)

```bash
# .env.free - 100% Free Tier Configuration
# ==========================================

# OPTION 1: Google AI Studio (RECOMMENDED - Most generous free tier)
GOOGLE_API_KEY=your-google-api-key
LLM_PROVIDER=google

# OPTION 2: Groq (Fastest free inference)
GROQ_API_KEY=your-groq-api-key
# LLM_PROVIDER=groq

# OPTION 3: Ollama (Completely local - no API needed)
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.1:8b

# Optional: HuggingFace (for embeddings API)
# HF_TOKEN=your-huggingface-token

# Embeddings - Use LOCAL (free)
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Deployment
# Render automatically sets PORT
# No Redis needed for training (use in-memory cache)
```

---

## 6. Lab-by-Lab Free Tier Modifications

### Lab 01: Vibe Coding Intro
**Changes needed:**
- Replace Railway backend deployment → Render free tier
- Use Google AI Studio or Groq for any LLM calls
- Vercel free tier already works for frontend

### Lab 02: Code Analyzer Agent
**Changes needed:**
```python
# Before (costs money)
llm = get_llm_client("anthropic")

# After (free)
llm = get_free_llm_client("google")  # or "groq" or "ollama"
```
- Deploy to Render instead of Railway

### Lab 03: Migration Workflow Agent
**Changes needed:**
- Same LLM client swap
- Deploy to Render free tier

### Lab 04: RAG System
**Changes needed:**
```python
# Before (costs money)
self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# After (free)
self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
```
- ChromaDB is already free (local)
- Deploy to HuggingFace Spaces (better for ML apps)

### Lab 05: Multi-Agent Orchestration
**Changes needed:**
- Same LLM client swap
- Consider using Ollama for faster local iteration

### Capstone Projects
**All capstone options work with free tiers:**
- Use Google AI Studio or Groq for LLM
- Use Sentence Transformers for embeddings
- Deploy to Render (backend) + Vercel (frontend)

---

## 7. Updated Requirements

```txt
# requirements-free.txt
# Core LLM Libraries (FREE providers)
google-generativeai>=0.3.0  # Google AI Studio - FREE
groq>=0.4.0                  # Groq - FREE

# Optional: For Ollama local setup
openai>=1.12.0              # Ollama uses OpenAI-compatible API

# Embeddings (FREE local)
sentence-transformers>=2.3.0

# Web Frameworks (unchanged)
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3

# Vector Database (FREE local)
chromadb>=0.4.22

# Data Processing (unchanged)
numpy>=1.24.0
pandas>=2.0.0

# HTTP & Async (unchanged)
httpx>=0.26.0
aiohttp>=3.9.0
aiofiles>=23.2.0

# Database (unchanged - SQLite is free)
aiosqlite>=0.19.0

# Utilities (unchanged)
python-dotenv>=1.0.0
pyyaml>=6.0
tenacity>=8.2.0

# Development (unchanged)
pytest>=7.4.0
pytest-asyncio>=0.23.0
black>=24.1.0
ruff>=0.1.0
```

---

## 8. Quick Start: Free Setup

### Step 1: Get Free API Keys (5 minutes)

1. **Google AI Studio** (recommended):
   - Go to https://aistudio.google.com/
   - Click "Get API Key"
   - Create key (no credit card needed)

2. **Groq** (optional, for speed):
   - Go to https://console.groq.com/
   - Sign up and get API key
   - No credit card needed

3. **Ollama** (optional, for local):
   - Install from https://ollama.ai/
   - Run `ollama pull llama3.1:8b`

### Step 2: Configure Environment

```bash
# Copy free environment template
cp .env.free .env

# Edit with your keys
nano .env
```

### Step 3: Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-free.txt
```

### Step 4: Verify Setup

```python
# test_free_setup.py
from llm_client_free import get_free_llm_client

def test_llm():
    client = get_free_llm_client("google")
    response = client.chat([
        {"role": "user", "content": "Say 'Hello, free AI!' in exactly those words."}
    ])
    print(f"LLM Response: {response}")
    assert "hello" in response.lower()
    print("✅ LLM working!")

def test_embeddings():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(["Test embedding"])
    assert len(embedding[0]) == 384
    print("✅ Embeddings working!")

if __name__ == "__main__":
    test_llm()
    test_embeddings()
    print("\n🎉 All free-tier components working!")
```

---

## 9. Free Tier Limitations & Workarounds

### Rate Limits

| Provider | Limit | Workaround |
|----------|-------|------------|
| Google AI Studio | 15 RPM (Flash) | Use batch processing, add delays |
| Groq | 30 RPM | Sufficient for training |
| Ollama | Unlimited (local) | Only limited by your hardware |

### Quality Considerations

| Task | Recommended Free Model | Quality vs GPT-4 |
|------|------------------------|------------------|
| Code generation | Gemini 1.5 Flash | ~90% |
| Code analysis | Llama 3.1 70B (Groq) | ~85% |
| RAG/Q&A | Gemini 1.5 Pro | ~95% |
| Multi-agent | Any of above | ~85% |

### Cold Start (Render Free Tier)

Free tier services spin down after inactivity:
```python
# Add to your app for faster wake-up
import httpx

@app.on_event("startup")
async def ping_self():
    """Keep service warm during active use."""
    # Health check endpoint responds quickly
    pass

# Or use external pinging service (UptimeRobot free tier)
```

---

## 10. Cost Comparison Summary

### Original Training Cost
```
LLM APIs:           $20-60/week
Embeddings:         $2-5/week
Deployment:         $5-20/week
AI Tools:           $20-40/month
─────────────────────────────
TOTAL:              $47-125/week
```

### Free Tier Training Cost
```
LLM APIs:           $0 (Google AI Studio/Groq/Ollama)
Embeddings:         $0 (Sentence Transformers local)
Deployment:         $0 (Render free + Vercel free)
AI Tools:           $0 (Cursor free/Continue/Codeium)
─────────────────────────────
TOTAL:              $0/week ✓
```

---

## 11. Recommended Free Stack

For the best training experience at zero cost:

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| **LLM Provider** | Google AI Studio | Groq, Ollama |
| **LLM Model** | Gemini 1.5 Flash | Llama 3.1 70B |
| **Embeddings** | Sentence Transformers (local) | Google Embedding API |
| **Vector DB** | ChromaDB (local) | - |
| **Backend Deploy** | Render Free | HuggingFace Spaces |
| **Frontend Deploy** | Vercel Free | Netlify, Cloudflare |
| **AI Coding Tool** | Cursor Free or Continue | Codeium |
| **Local Models** | Ollama | - |

---

## Appendix: Service Signup Links

- **Google AI Studio**: https://aistudio.google.com/
- **Groq**: https://console.groq.com/
- **Ollama**: https://ollama.ai/
- **Render**: https://render.com/
- **Vercel**: https://vercel.com/
- **HuggingFace**: https://huggingface.co/
- **Continue**: https://continue.dev/
- **Codeium**: https://codeium.com/
- **Cursor**: https://cursor.com/

---

*This guide ensures every student can complete the Agentic AI Intensive Training Program at absolutely zero cost.*
