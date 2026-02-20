# Agentic AI Intensive Training Program

## 1-Week Full-Time Training for Senior Contractors

```
 _____ _____ _____ _____ _____ _____ _____    _____ _____
|  _  |   __|   __|   | |_   _|     |     |  |  _  |     |
|     |  |  |   __| | | | | | |-   -|   --|  |     |-   -|
|__|__|_____|_____|_|___| |_| |_____|_____|  |__|__|_____|

From Zero GenAI Experience to Production-Ready in 5 Days
```

---

## Program Overview

This intensive 40-hour training program transforms experienced software engineers into productive agentic AI practitioners. Designed for contractors who work with multiple clients, this program emphasizes:

- **LLM-Agnostic Skills**: Work with Claude, GPT-4, Gemini, or any model
- **Real-World Engineering**: Production patterns, not toy examples
- **Immediate Applicability**: Skills you can use on client projects tomorrow

### What You'll Build

| Day | Project | Deployment |
|-----|---------|------------|
| 1 | AI-Assisted Full-Stack App | Vercel |
| 2 | Code Analyzer Agent | Railway |
| 3 | Migration Workflow System | Railway |
| 4 | RAG System with Evaluation | Railway |
| 5 | Capstone Project (your choice) | Multiple options |

---

## Prerequisites

### Required Skills
- [ ] Proficient in at least one programming language (Python preferred, JavaScript/TypeScript also used)
- [ ] Experience building web applications and APIs
- [ ] Familiarity with Git, CLI tools, and cloud deployments
- [ ] Understanding of REST APIs and HTTP protocols
- [ ] Basic understanding of JSON and data structures

### Required Accounts (100% FREE Options Available!)

> **Note:** This training can be completed at **zero cost** using free tiers. See [FREE-TIER-STRATEGY.md](./guides/free-tier-strategy.md) for complete details.

**LLM APIs (choose one - all free):**
- [ ] **Google AI Studio** (RECOMMENDED): https://aistudio.google.com/ - Most generous free tier
- [ ] **Groq**: https://console.groq.com/ - Fastest free inference
- [ ] **Ollama** (local): https://ollama.ai/ - 100% free, runs on your machine

**Deployment (free):**
- [ ] **GitHub**: https://github.com
- [ ] **Vercel** (frontend): https://vercel.com - Free tier
- [ ] **Render** (backend): https://render.com - Free tier

**Optional (paid, but NOT required):**
- [ ] OpenAI API: https://platform.openai.com/signup
- [ ] Anthropic API: https://console.anthropic.com/

### Required Software
```bash
# Check your versions
python --version    # 3.10+ required
node --version      # 18+ required
npm --version       # 9+ required
git --version       # Any recent version
```

---

## Choose Your Language

All labs are available in **Python** and **TypeScript**. Choose based on your preference:

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Directory | `labs/labXX/python/` | `labs/labXX/typescript/` |
| Web Framework | FastAPI | Hono |
| Validation | Pydantic | Zod |
| Run Command | `uvicorn main:app` | `npm run dev` |
| Strengths | ML ecosystem, AI libraries | Type safety, frontend integration |

> **Recommendation**: If you're undecided, Python has more mature AI tooling. TypeScript is ideal if you're building full-stack web applications. See [docs/LANGUAGE-CHOICE-GUIDE.md](./docs/LANGUAGE-CHOICE-GUIDE.md) for detailed guidance.

---

## Quick Start

### 1. Clone and Navigate
```bash
cd /path/to/AI_Training
```

### 2. Setup Your Language

<details>
<summary><b>Python Setup</b></summary>

```bash
# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

</details>

<details>
<summary><b>TypeScript Setup</b></summary>

```bash
# Install Node.js dependencies
npm install

# For individual labs
cd labs/lab02-code-analyzer-agent/typescript
npm install
```

</details>

### 3. Configure API Keys
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
```

### 4. Verify Setup

Run the universal setup verification script:

```bash
# Verify all environments (Python + TypeScript)
./scripts/verify-setup.sh

# Verify Python only
./scripts/verify-setup.sh python

# Verify TypeScript only
./scripts/verify-setup.sh typescript
```

The script checks versions, API keys, and installed packages for your chosen language.

---

## Program Structure

```
AI_Training/
├── README.md                 # You are here
├── COURSE-OVERVIEW.md        # Marketing/sales document
├── requirements.txt          # Python dependencies
├── package.json              # Node.js/TypeScript dependencies
├── tsconfig.base.json        # TypeScript base configuration
├── .env.example              # Environment template
│
├── curriculum/               # 📚 Course content
│   ├── README.md             # Curriculum overview
│   ├── SCHEDULE.md           # Detailed daily/hourly schedule
│   ├── day1-foundations.md   # GenAI Foundations & Vibe Coding
│   ├── day2-prompting.md     # Advanced Prompting Engineering
│   ├── day3-agents.md        # Agent Architectures
│   ├── day4-rag-eval.md      # RAG & Evaluation
│   └── day5-production.md    # Production & Capstone
│
├── guides/                   # 📖 Student resources
│   ├── README.md             # Guides overview
│   ├── getting-started.md    # Setup & prerequisites
│   ├── learning-paths.md     # Personalized learning paths
│   ├── tools-ecosystem.md    # Tools guide
│   ├── free-tier-strategy.md # Budget-friendly approach
│   ├── checklists.md         # Daily progress tracking
│   ├── community.md          # Community resources
│   ├── team-collaboration.md # Team workflows & best practices
│   └── cicd-for-ai.md        # CI/CD patterns for AI systems
│
├── resources/                # 📑 Reference materials
│   ├── README.md             # Resources overview
│   ├── recommended-reading.md # Books, papers, articles
│   └── additional-resources.md # Extra materials
│
├── labs/                     # 🧪 Hands-on lab exercises
│   ├── lab01-vibe-coding-intro/
│   │   ├── README.md         # Lab instructions
│   │   ├── python/           # Python implementation
│   │   └── typescript/       # TypeScript implementation
│   ├── lab02-code-analyzer-agent/
│   ├── lab03-migration-workflow/
│   ├── lab04-rag-system/
│   └── capstone-options/
│
├── optional-exercises/       # 💪 Extra practice
│   ├── level-1-foundational/
│   ├── level-2-intermediate/
│   ├── level-3-advanced/
│   ├── level-4-expert/
│   ├── challenges/
│   └── shared/
│
├── templates/                # 📋 Reusable starter templates
│   ├── python-agent/         # Basic Python agent
│   ├── typescript-agent/     # Basic TypeScript agent
│   ├── rag-starter/          # RAG system starter
│   ├── deployment/           # Deployment configs
│   └── production-ready/     # Production templates with all patterns
│       ├── fullstack-production-agent/
│       └── code-review-agent/
│
├── docs/                     # 📝 Additional documentation
│   └── LANGUAGE-CHOICE-GUIDE.md
│
├── scripts/                  # 🔧 Utility scripts
└── slides/                   # 📊 Presentation slides
```

---

## Daily Schedule Overview

| Day | Theme | Hours | Key Outcome |
|-----|-------|-------|-------------|
| **Day 1** | GenAI Foundations & Vibe Coding | 8h | Understand LLMs, deploy first AI app |
| **Day 2** | Advanced Prompting | 8h | Master prompt engineering for code tasks |
| **Day 3** | Agent Architectures | 8h | Build and deploy agentic systems |
| **Day 4** | RAG & Evaluation | 8h | Implement RAG with proper evaluation |
| **Day 5** | Production & Capstone | 8h | Ship a complete AI-powered project |

---

## Tools Covered (LLM-Agnostic)

### AI Coding Assistants
| Tool | Type | Best For |
|------|------|----------|
| Claude Code | CLI | Terminal-based development |
| Cursor | IDE | Full IDE experience |
| Gemini CLI | CLI | Google ecosystem integration |
| GitHub Copilot | IDE Extension | Inline completions |
| Aider | CLI | Git-integrated coding |
| Continue | IDE Extension | Open-source alternative |

### LLM Providers
| Provider | Models | Strengths |
|----------|--------|-----------|
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | Reasoning, safety, long context |
| OpenAI | GPT-4o, GPT-4 Turbo, o1 | Broad capabilities, function calling |
| Google | Gemini Pro, Gemini Ultra | Multimodal, speed |
| Local | Llama, Mistral, Mixtral | Privacy, cost control |

### Agentic Frameworks
| Framework | Language | Best For |
|-----------|----------|----------|
| LangChain | Python/JS | Rapid prototyping |
| LangGraph | Python | Complex agent workflows |
| CrewAI | Python | Multi-agent teams |
| AutoGen | Python | Conversational agents |
| Semantic Kernel | Python/C# | Enterprise integration |

---

## Capstone Project Options

Choose one for your final project on Day 5:

### Option A: AI Code Review Bot (Medium)
Build a GitHub-integrated code review agent.
- Analyzes pull requests automatically
- Provides structured feedback
- Deploys as a GitHub webhook

### Option B: Legacy Code Documenter (Medium-High)
Create an agent that generates documentation for legacy code.
- Analyzes code structure and patterns
- Generates README, API docs, architecture diagrams
- Works with any language

### Option C: Tech Debt Analyzer (High)
Build a RAG-enhanced system for technical debt analysis.
- Indexes codebase with semantic search
- Identifies and prioritizes tech debt
- Generates remediation reports

### Option D: Multi-Agent Research Assistant (High)
Create an orchestrated multi-agent system.
- Multiple specialized agents working together
- Research, analysis, and report generation
- Complex workflow orchestration

---

## Learning Outcomes

By the end of this program, you will be able to:

### Technical Skills
- [ ] Explain how LLMs work and their practical limitations
- [ ] Write effective prompts for code generation, analysis, and refactoring
- [ ] Build and deploy agentic systems with tool-use capabilities
- [ ] Implement RAG systems with proper evaluation
- [ ] Apply production patterns (rate limiting, caching, fallbacks)

### Professional Skills
- [ ] Evaluate when to use AI vs. traditional approaches
- [ ] Estimate and scope AI-augmented features for clients
- [ ] Debug and troubleshoot AI system failures
- [ ] Communicate AI capabilities and limitations to stakeholders

---

## Support and Resources

### During Training
- All labs include step-by-step instructions
- Exercises include expected outputs for verification

### External Resources
- [Anthropic Documentation](https://docs.anthropic.com/)
- [OpenAI Documentation](https://platform.openai.com/docs/)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [Vercel AI SDK](https://sdk.vercel.ai/docs/)

---

## Quick Reference

### Common Commands

<details>
<summary><b>Python</b></summary>

```bash
# Activate environment
source .venv/bin/activate

# Run a lab
cd labs/lab02-code-analyzer-agent/python
uvicorn main:app --reload

# Run tests
pytest

# Deploy to Railway
railway up
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```bash
# Run a lab
cd labs/lab02-code-analyzer-agent/typescript
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Deploy to Vercel
vercel --prod
```

</details>

### Cost Options

#### FREE Option (Recommended for Students)
| Activity | Cost |
|----------|------|
| All Labs & Capstone | **$0** |

*Using Google AI Studio, Groq, or Ollama + Render free tier. See [FREE-TIER-STRATEGY.md](./guides/free-tier-strategy.md)*

#### Paid Option (If preferred)
| Activity | Estimated Cost |
|----------|----------------|
| Day 1 Labs | $2-5 |
| Day 2 Labs | $3-7 |
| Day 3 Labs | $5-10 |
| Day 4 Labs | $5-15 |
| Day 5 Capstone | $5-20 |
| **Total Week** | **$20-60** |

*Using OpenAI/Anthropic APIs. Costs vary based on model choice.*

---

## 📚 Additional Resources

Expand your learning beyond this 5-day intensive program with our curated collection of resources:

### 🗺️ [Learning Paths](guides/learning-paths.md)
Structured roadmaps for continuing your AI engineering journey. Choose from:
- **AI Product Engineer** (3-4 months) - Build and ship AI products
- **AI Infrastructure Engineer** (4-6 months) - Scale AI systems
- **Research Engineer** (6+ months) - Push the boundaries
- **AI Consultant/Architect** (3-4 months) - Design AI solutions
- **Specialized Paths** - Healthcare, Enterprise, Security, and more

### 📖 [Resources & References](resources/additional-resources.md)
Comprehensive collection of high-quality resources organized by topic:
- Official documentation for all major LLM providers
- Day-by-day resource guides aligned with training content
- Interactive playgrounds and tutorials
- Video courses and YouTube channels
- Essential blogs and newsletters
- Research papers and datasets

### 🛠️ [Tools & Ecosystem](guides/tools-ecosystem.md)
Complete toolkit for building AI applications:
- LLM providers comparison (Anthropic, OpenAI, Google, open source)
- Agent frameworks (LangChain, LlamaIndex, AutoGen, CrewAI)
- Vector databases (Pinecone, Weaviate, Qdrant, ChromaDB)
- Embedding models (OpenAI, Cohere, open source)
- Observability and monitoring tools
- Deployment platforms and infrastructure

### 📄 [Recommended Reading](resources/recommended-reading.md)
Essential papers and articles for AI engineers:
- **The Foundational 10** - Must-read papers every AI engineer should know
- Papers organized by topic (Transformers, Prompting, Agents, RAG, Evaluation)
- Difficulty levels (🟢 Beginner, 🟡 Intermediate, 🔴 Advanced)
- Technical blog posts from industry leaders
- 30-day and 90-day reading plans

### 🤝 [Community & Networking](guides/community.md)
Connect with fellow AI engineers and continue learning:
- Discord communities (AI Engineer, LangChain, OpenAI, Anthropic)
- Forums and discussion platforms (Reddit, Hugging Face)
- Twitter/X accounts to follow
- Podcasts and YouTube channels
- Conferences and events (AI Engineer Summit, NeurIPS, ICML)
- Hackathons and competitions
- Open source contribution opportunities
- Networking and community forums

### 👥 [Team Collaboration](guides/team-collaboration.md)
Best practices for contractors working in teams on AI projects:
- Code review practices for AI systems
- Version control workflows for agents and prompts
- Documentation standards and templates
- Project handoff procedures
- Knowledge sharing and team communication
- Quality standards and definition of done
- Onboarding new team members

### 🔄 [CI/CD for AI](guides/cicd-for-ai.md)
Continuous integration and deployment patterns for AI applications:
- Testing pipelines for AI systems
- Automated quality gates and LLM-as-judge
- Deployment automation (Railway, Render, Vercel)
- Rollback strategies and canary deployments
- Cost-aware testing and smart test selection
- Monitoring and alerting for production AI

### 📦 [Production-Ready Templates](templates/production-ready/)
Complete templates with all production patterns pre-integrated:
- **Fullstack Production Agent**: FastAPI with rate limiting, caching, monitoring, responsible AI
- **Code Review Agent**: GitHub-integrated automated PR reviews
- All security, observability, and governance patterns included
- Ready to deploy to Railway, Render, or Docker

### 🎯 Next Steps After Training

1. **Choose Your Path**: Review [LEARNING-PATHS.md](guides/learning-paths.md) and select a roadmap
2. **Join Communities**: Connect with others in [COMMUNITY.md](guides/community.md)
3. **Bookmark Resources**: Save [RESOURCES.md](resources/additional-resources.md) for quick reference
4. **Start Reading**: Begin with the Foundational 10 papers in [RECOMMENDED-READING.md](resources/recommended-reading.md)
5. **Explore Tools**: Experiment with new frameworks from [TOOLS-ECOSYSTEM.md](guides/tools-ecosystem.md)

---

## License and Usage

This training material is designed for educational purposes. You may:
- Use these materials for personal learning
- Adapt exercises for internal team training
- Reference patterns in client projects

---

**Ready to begin?** Start with [SCHEDULE.md](./curriculum/SCHEDULE.md) for the detailed daily breakdown, then proceed to [Day 1: Foundations](./curriculum/day1-foundations.md).
