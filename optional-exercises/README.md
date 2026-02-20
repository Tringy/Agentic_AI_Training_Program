# Optional Exercises & Practice Labs

This directory contains optional practical exercises designed to deepen and expand your skills beyond the main training program. Each exercise is designed to be completed independently and progressively.

## Exercise Philosophy

These optional labs are designed to:

- **Reinforce concepts**: Practice what you learned in the main program
- **Explore advanced cases**: Go beyond the basic material
- **Build portfolio**: Create demonstrable projects for your portfolio
- **Self-directed learning**: Encourage independent research
- **Real-world preparation**: Simulate real production challenges

## How to Use This Resource

1. **Not mandatory**: Complete the ones that interest you or that you need
2. **No strict order**: Although there are levels, you can skip around based on your experience
3. **Learn by doing**: Try to solve before looking at solutions
4. **Share your work**: Use these projects in your portfolio
5. **Contribute**: If you improve an exercise, consider contributing back

---

## Difficulty Levels

### 🟢 Level 1: Foundational (4 exercises)
**Prerequisite**: Complete Day 1-2 of the main program

Fundamental exercises to consolidate basic LLM and prompting concepts.

| Exercise | Description | Estimated time | Skills |
|----------|-------------|----------------|--------|
| [Token Counter & Analyzer](./level-1-foundational/ex01-token-counter/) | Build a tool to analyze tokens and costs | 2-3h | Tokenization, API usage |
| [Hallucination Detector](./level-1-foundational/ex02-hallucination-detector/) | System to detect and measure hallucinations | 3-4h | Prompt engineering, Validation |
| [Prompt Testing Framework](./level-1-foundational/ex03-prompt-tester/) | Framework for A/B testing prompts | 3-4h | Testing, Metrics |
| [Cost Calculator Dashboard](./level-1-foundational/ex04-cost-calculator/) | Interactive LLM cost dashboard | 2-3h | APIs, Frontend |

**Goal**: Master the technical fundamentals of working with LLMs

---

### 🟡 Level 2: Intermediate (5 exercises)
**Prerequisite**: Complete Day 2-3 of the main program

Intermediate exercises focused on practical engineering applications.

| Exercise | Description | Estimated time | Skills |
|----------|-------------|----------------|--------|
| [Semantic Search Engine](./level-2-intermediate/ex05-semantic-search/) | Semantic search over documentation | 4-5h | Embeddings, Vector search |
| [Auto Code Documenter](./level-2-intermediate/ex06-code-documenter/) | Automatic documentation generator | 4-5h | Code parsing, Prompting |
| [Intelligent Test Generator](./level-2-intermediate/ex07-test-generator/) | Automatically generate unit tests | 5-6h | Code analysis, Test patterns |
| [Git Changelog Generator](./level-2-intermediate/ex08-changelog-generator/) | Generate intelligent changelogs from commits | 3-4h | Git integration, Summarization |
| [Multi-Provider API Wrapper](./level-2-intermediate/ex09-api-wrapper/) | Unified abstraction for multiple LLM APIs | 5-6h | API design, Abstraction |

**Goal**: Build useful productivity tools for developers

---

### 🟠 Level 3: Advanced (5 exercises)
**Prerequisite**: Complete Day 3-4 of the main program

Advanced exercises on agentic systems and optimized RAG.

| Exercise | Description | Estimated time | Skills |
|----------|-------------|----------------|--------|
| [Intelligent Caching System](./level-3-advanced/ex10-intelligent-caching/) | Semantic cache system for LLM calls | 6-7h | Caching, Embeddings |
| [Multi-Provider Router](./level-3-advanced/ex11-multi-provider-router/) | Intelligent router based on cost/quality | 6-8h | Routing logic, Optimization |
| [Autonomous Debugger Agent](./level-3-advanced/ex12-autonomous-debugger/) | Agent that automatically debugs code | 8-10h | Agents, Tool use |
| [Code Migration Planner](./level-3-advanced/ex13-code-migration-planner/) | Plan framework migrations | 7-9h | Code analysis, Planning |
| [Custom RAG Evaluator](./level-3-advanced/ex14-custom-rag-evaluator/) | Complete RAG evaluation suite | 6-8h | Evaluation, Metrics |

**Goal**: Build complex systems optimized for production

---

### 🔴 Level 4: Expert (4 exercises)
**Prerequisite**: Complete Day 4-5 of the main program

Expert-level exercises on complex architectures and production systems.

| Exercise | Description | Estimated time | Skills |
|----------|-------------|----------------|--------|
| [Multi-Agent Orchestrator](./level-4-expert/ex15-multi-agent-orchestrator/) | Multi-agent orchestration system | 10-12h | Multi-agent, Orchestration |
| [Custom LLM Router](./level-4-expert/ex16-custom-llm-router/) | Router with machine learning | 10-15h | ML, Routing, Analytics |
| [Production Monitoring System](./level-4-expert/ex17-production-monitoring/) | Complete observability system | 12-15h | Monitoring, Tracing, Alerts |
| [AI-Powered CI/CD Pipeline](./level-4-expert/ex18-ai-powered-cicd/) | CI/CD pipeline with AI analysis | 15-20h | DevOps, Automation |

**Goal**: Master enterprise architectures and production systems

---

## Challenges (Major Projects)

Challenging capstone-type projects that integrate multiple concepts.

### Challenge 1: Build a Cursor Clone
**Time**: 30-40 hours | **Difficulty**: Expert

Build your own simplified version of Cursor IDE:
- Code editor with AI assistance
- Context-aware code completion
- Chat interface for pair programming
- File tree navigation with semantic search

[View details →](./challenges/challenge01-build-cursor-clone/)

---

### Challenge 2: AI Code Reviewer
**Time**: 25-35 hours | **Difficulty**: Advanced-Expert

Complete automated code review system:
- GitHub integration (PRs, comments)
- Multi-dimensional analysis (bugs, security, performance)
- Improvement suggestions with diffs
- Learning system that improves with feedback

[View details →](./challenges/challenge02-ai-code-reviewer/)

---

### Challenge 3: Intelligent Search Engine
**Time**: 35-45 hours | **Difficulty**: Expert

Intelligent search engine for codebases:
- Hybrid search (vector + keyword + graph)
- Natural language queries
- Code context understanding
- Real-time indexing
- Automatic query expansion

[View details →](./challenges/challenge03-intelligent-search-engine/)

---

## Exercise Selection Guide

### By Learning Objective

**I want to master advanced prompting**:
- ex02-hallucination-detector
- ex03-prompt-tester
- ex06-code-documenter
- ex13-code-migration-planner

**I want to work with embeddings and RAG**:
- ex05-semantic-search
- ex10-intelligent-caching
- ex14-custom-rag-evaluator
- challenge03-intelligent-search-engine

**I want to build autonomous agents**:
- ex12-autonomous-debugger
- ex13-code-migration-planner
- ex15-multi-agent-orchestrator
- challenge02-ai-code-reviewer

**I want to optimize costs and performance**:
- ex01-token-counter
- ex04-cost-calculator
- ex10-intelligent-caching
- ex11-multi-provider-router
- ex16-custom-llm-router

**I want to build productivity tools**:
- ex06-code-documenter
- ex07-test-generator
- ex08-changelog-generator
- ex18-ai-powered-cicd

**I want to prepare systems for production**:
- ex09-api-wrapper
- ex11-multi-provider-router
- ex17-production-monitoring
- challenge01-build-cursor-clone

---

### By Preferred Tech Stack

**Python Enthusiasts**:
- ex05-semantic-search (FastAPI + Qdrant)
- ex12-autonomous-debugger (LangGraph)
- ex14-custom-rag-evaluator (pytest)
- ex17-production-monitoring (Prometheus)

**TypeScript/Node.js Fans**:
- ex01-token-counter (Next.js)
- ex04-cost-calculator (React + Recharts)
- ex09-api-wrapper (tRPC)
- challenge01-build-cursor-clone (Electron)

**Full-Stack Projects**:
- ex03-prompt-tester (React + FastAPI)
- ex08-changelog-generator (Node.js + GitHub API)
- challenge02-ai-code-reviewer (Full-stack)

**DevOps/Infrastructure**:
- ex10-intelligent-caching (Redis + PostgreSQL)
- ex17-production-monitoring (Grafana + Prometheus)
- ex18-ai-powered-cicd (GitHub Actions + Docker)

---

## Shared Resources

All exercises use shared resources located in `./shared/`:

- **Templates**: Base code templates
- **Utils**: Reusable helper functions
- **Datasets**: Test data and examples
- **Docker**: Shared Docker configurations
- **Scripts**: Setup and deployment scripts

---

## Badge System

By completing exercises, you earn badges that demonstrate your expertise:

- 🟢 **Foundational Master**: Complete all Level 1 exercises
- 🟡 **Intermediate Builder**: Complete 4 of 5 Level 2 exercises
- 🟠 **Advanced Engineer**: Complete 4 of 5 Level 3 exercises
- 🔴 **Expert Architect**: Complete 3 of 4 Level 4 exercises
- 🏆 **Challenge Champion**: Complete any Challenge
- 💎 **Grand Master**: Complete all levels + 2 challenges

Share your badges on LinkedIn or your professional portfolio.

---

## Contributing

Did you improve an exercise or create a new one? Contribute!

1. Fork the repository
2. Create your exercise following the existing structure
3. Include tests and reference solution
4. Submit a Pull Request

**Template for new exercises**: [./EXERCISE-TEMPLATE.md](./EXERCISE-TEMPLATE.md)

---

## Support and Community

- **Issues**: Report problems on GitHub Issues
- **Community**: Share your solutions in community forums

---

## FAQ

**Should I complete all exercises?**
No, they're optional. Choose the ones that align with your goals.

**Are solutions available?**
Yes, each exercise includes a reference solution, but try to solve it first.

**Can I use these projects in my portfolio?**
Absolutely! They're designed for that.

**How much time should I invest?**
Whatever you need. Some complete 2-3 per week, others take more time.

**Do I need to complete the main program first?**
Recommended, but if you have prior experience, you can start directly.

---

**Navigation**: [← Back to main README](../README.md)

**Let's start building! 🚀**
