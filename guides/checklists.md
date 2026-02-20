# Training Program Checklists

## Language Choice

This program supports both **Python** and **TypeScript**. Mark which language you're using:

- [ ] **Python** - Using `labs/labXX/python/` directories
- [ ] **TypeScript** - Using `labs/labXX/typescript/` directories

> See [docs/LANGUAGE-CHOICE-GUIDE.md](../docs/LANGUAGE-CHOICE-GUIDE.md) for help choosing.

---

## Table of Contents
1. [Daily Progress Checklists](#daily-progress)
2. [Environment Setup Checklist](#environment-setup)
3. [Deployment Checklist](#deployment)
4. [Security Checklist](#security)
5. [Code Review Checklist](#code-review)
6. [Production Readiness Checklist](#production-readiness)

---

<a name="daily-progress"></a>
## Daily Progress Checklists

### Day 1: GenAI Foundations & AI-First Engineering

#### Morning (09:00 - 12:30)
- [ ] Environment verified (Python or TypeScript, API keys)
- [ ] Completed LLM fundamentals module
- [ ] Understand tokens, context windows, parameters
- [ ] Completed model behavior module
- [ ] Know about hallucinations and constraints
- [ ] **Exercise 1 Complete**: Model comparison report

#### Afternoon (13:30 - 17:00)
- [ ] Understand Vibe Coding methodology
- [ ] Know when to use AI vs. traditional coding
- [ ] Reviewed tool landscape (Claude Code, Cursor, etc.)
- [ ] **Tool Matrix Complete**: Selected primary tools
- [ ] **Lab 01 Complete**: URL shortener deployed to Vercel

#### Day 1 Deliverables
- [ ] Model comparison report (saved)
- [ ] Tool selection matrix (filled out)
- [ ] Deployed URL shortener (URL: _____________)
- [ ] Environment fully configured (Python ▢ / TypeScript ▢)

---

### Day 2: Advanced Prompting for Engineering

#### Morning (09:00 - 12:30)
- [ ] Understand RCFG framework
- [ ] Know clarity principles for prompts
- [ ] Master CoT, few-shot, self-consistency patterns
- [ ] Created system prompts for code review
- [ ] **Exercise 1 Complete**: Prompt optimization

#### Afternoon (13:30 - 17:00)
- [ ] Know code-focused prompting patterns
- [ ] Understand multimodal prompting (images, PDFs)
- [ ] Understand migration and refactoring prompts
- [ ] Built personal prompt library
- [ ] **Lab 02 Complete**: Code analyzer agent deployed

#### Day 2 Deliverables
- [ ] Personal prompt library (10+ prompts saved)
- [ ] System prompt templates (3+ created)
- [ ] Deployed code analyzer (URL: _____________)
- [ ] Prompt optimization documentation

---

### Day 3: Agent Architectures

#### Morning (09:00 - 12:30)
- [ ] Understand agent fundamentals (loop, memory, state)
- [ ] Implement context management strategies
- [ ] Build long-term and episodic memory systems
- [ ] Know tool-use and function calling patterns
- [ ] Ensure structured output with schema validation
- [ ] Understand ReAct pattern
- [ ] Know planning and verification patterns
- [ ] **Exercise 1 Complete**: Agent architecture design

#### Afternoon (13:30 - 17:00)
- [ ] Understand multi-agent systems
- [ ] Know supervisor, pipeline, debate patterns
- [ ] Reviewed framework comparison (LangChain, CrewAI, etc.)
- [ ] **Lab 03 Complete**: Migration workflow agent deployed

#### Day 3 Deliverables
- [ ] Agent architecture diagrams (created)
- [ ] Framework decision matrix (filled out)
- [ ] Deployed migration agent (URL: _____________)
- [ ] Agent pattern reference sheet

---

### Day 4: RAG & Evaluation

#### Morning (09:00 - 12:30)
- [ ] Understand RAG pipeline (index, query, generate)
- [ ] Know embedding models and vector stores
- [ ] Understand chunking strategies
- [ ] Know RAG pitfalls and advanced patterns
- [ ] **Exercise 1 Complete**: RAG architecture design

#### Afternoon (13:30 - 17:00)
- [ ] Understand evaluation metrics (precision, recall, MRR)
- [ ] Know LLM-as-judge evaluation
- [ ] Implement comprehensive testing strategies
- [ ] Understand debugging and observability
- [ ] **Lab 04 Complete**: RAG system deployed with evaluation

#### Day 4 Deliverables
- [ ] RAG architecture documentation
- [ ] Chunking strategy comparison
- [ ] Deployed RAG system (URL: _____________)
- [ ] Evaluation dataset (10+ examples)

---

### Day 5: Production & Capstone

#### Morning (09:00 - 12:30)
- [ ] Understand rate limiting patterns
- [ ] Know caching strategies
- [ ] Understand fallback and retry patterns
- [ ] Know security measures (prompt injection defense)
- [ ] Understand cost management
- [ ] Master advanced cost optimization (semantic caching, model routing)
- [ ] Implement integration patterns (webhooks, queues, events)
- [ ] Reviewed deployment platforms
- [ ] **Lab 05 Complete**: Multi-agent mini-lab

#### Afternoon (13:30 - 17:00)
- [ ] Selected capstone project
- [ ] Implemented core functionality
- [ ] Deployed capstone
- [ ] Prepared demo
- [ ] Presented capstone

#### Day 5 Deliverables
- [ ] Production patterns checklist (completed)
- [ ] Security audit checklist (completed)
- [ ] Multi-agent mini-lab (completed)
- [ ] **Capstone deployed** (URL: _____________)
- [ ] Capstone presentation (delivered)

---

<a name="environment-setup"></a>
## Environment Setup Checklist

### Choose Your Language Setup

<details>
<summary><b>Python Environment</b></summary>

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] pip updated to latest version
- [ ] Requirements installed successfully

**Verification:**
```bash
python --version        # Should be 3.10+
pip --version           # Any recent version
```

</details>

<details>
<summary><b>TypeScript Environment</b></summary>

- [ ] Node.js 18+ installed
- [ ] npm 9+ installed
- [ ] TypeScript packages installed

**Verification:**
```bash
node --version          # Should be 18+
npm --version           # Should be 9+
npx tsc --version       # Should show version
```

</details>

### API Keys Configured
- [ ] OPENAI_API_KEY set
- [ ] ANTHROPIC_API_KEY set
- [ ] GOOGLE_API_KEY set (optional)
- [ ] Keys tested and working

### Accounts Created
- [ ] OpenAI Platform account (or free alternative like Groq)
- [ ] Anthropic Console account (optional)
- [ ] GitHub account
- [ ] Vercel account (for TypeScript)
- [ ] Railway/Render account (for Python)

### Tools Installed
- [ ] Git installed and configured
- [ ] VS Code / Cursor installed
- [ ] Claude Code CLI installed (optional)
- [ ] Docker installed (optional)

### Global CLI Tools (Optional)
```bash
# Deployment tools
npm install -g vercel       # For Vercel deployments
npm install -g @railway/cli # For Railway deployments
```

---

<a name="deployment"></a>
## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] No console.log/print statements for debugging
- [ ] No hardcoded secrets in code
- [ ] .env.example file created
- [ ] README updated with setup instructions
- [ ] Dependencies pinned to specific versions

### Environment Variables
- [ ] All required env vars documented
- [ ] Env vars set in deployment platform
- [ ] Secrets not committed to repo
- [ ] Different values for dev/staging/prod

### Vercel Deployment
- [ ] vercel.json configured
- [ ] Environment variables set
- [ ] Domain configured (if custom)
- [ ] Preview deployments working
- [ ] Production deployment successful

### Railway Deployment
- [ ] railway.toml or Procfile configured
- [ ] Environment variables set
- [ ] Health check endpoint works
- [ ] Logs accessible
- [ ] Deployment successful

### Render Deployment
- [ ] render.yaml configured
- [ ] Environment variables set
- [ ] Health check configured
- [ ] Auto-deploy configured
- [ ] Deployment successful

### Post-Deployment
- [ ] Application accessible via URL
- [ ] All features working
- [ ] Error handling working
- [ ] Logs being captured
- [ ] Monitoring in place

---

<a name="security"></a>
## Security Checklist

### Input Security
- [ ] All user inputs validated
- [ ] Input length limits enforced
- [ ] Special characters sanitized
- [ ] Prompt injection patterns checked
- [ ] Suspicious inputs logged

### Output Security
- [ ] Outputs scanned for sensitive data
- [ ] API keys/passwords redacted
- [ ] PII handled appropriately
- [ ] Output format validated
- [ ] Error messages don't leak info

### API Security
- [ ] API keys in environment variables
- [ ] Keys have minimal necessary permissions
- [ ] Rate limiting implemented
- [ ] Authentication required
- [ ] CORS configured correctly

### Data Security
- [ ] Sensitive data encrypted at rest
- [ ] Data encrypted in transit (HTTPS)
- [ ] Access controls implemented
- [ ] Audit logging enabled
- [ ] Data retention policy defined

### LLM-Specific Security
- [ ] System prompts protected
- [ ] User input isolated in prompts
- [ ] Output validation before display
- [ ] Cost limits enforced
- [ ] Model responses logged for review

---

<a name="code-review"></a>
## AI Code Review Checklist

### Before Generating Code
- [ ] Clear requirements specified
- [ ] Language and framework defined
- [ ] Existing patterns/conventions provided
- [ ] Edge cases identified
- [ ] Security requirements noted

### After Generating Code
- [ ] Code compiles/runs without errors
- [ ] Logic is correct for requirements
- [ ] Error handling is appropriate
- [ ] Edge cases are handled
- [ ] No security vulnerabilities
- [ ] Code follows project style
- [ ] Documentation is adequate
- [ ] Tests are included/working

### Red Flags to Check
- [ ] Hardcoded values that should be config
- [ ] Missing input validation
- [ ] SQL/command injection risks
- [ ] Sensitive data in logs
- [ ] Infinite loops or recursion
- [ ] Resource leaks
- [ ] Race conditions
- [ ] Missing error handling

---

<a name="production-readiness"></a>
## Production Readiness Checklist

### Functionality
- [ ] All features working as specified
- [ ] Error handling covers edge cases
- [ ] Graceful degradation implemented
- [ ] Fallbacks configured for LLM failures

### Reliability
- [ ] Rate limiting active
- [ ] Retry logic with exponential backoff
- [ ] Circuit breakers configured
- [ ] Health check endpoints working
- [ ] Timeout limits set

### Performance
- [ ] Response times acceptable (<5s typical)
- [ ] Caching implemented where appropriate
- [ ] Cold start optimized
- [ ] Streaming enabled for long responses
- [ ] Resource limits configured

### Observability
- [ ] Structured logging implemented
- [ ] Request tracing enabled
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Metrics collection enabled
- [ ] Dashboards created

### Cost Control
- [ ] Budget limits configured
- [ ] Cost tracking enabled
- [ ] Alerts for unusual spending
- [ ] Model selection optimized for cost
- [ ] Caching reduces redundant calls

### Operations
- [ ] Deployment documented
- [ ] Rollback procedure defined
- [ ] On-call procedures documented
- [ ] Incident response plan exists
- [ ] Runbooks for common issues

---

## Quick Reference: Model Constraints Checklist

Before sending any prompt to an LLM:

- [ ] Is my request clear and unambiguous?
- [ ] Have I provided necessary context?
- [ ] Am I asking for something within the model's capabilities?
- [ ] Have I considered potential hallucination risks?
- [ ] Is critical information at the start AND end (for long contexts)?
- [ ] Have I specified the output format?
- [ ] Will I verify/test the response?

---

## Troubleshooting Checklist

### "Model Returns Wrong Answer"
- [ ] Check if question is clear
- [ ] Verify context is sufficient
- [ ] Try chain-of-thought prompting
- [ ] Test with different models
- [ ] Check for ambiguity in requirements

### "RAG Returns Irrelevant Results"
- [ ] Check chunk sizes
- [ ] Verify embeddings working
- [ ] Test with exact phrase from documents
- [ ] Check similarity threshold
- [ ] Try hybrid search

### "Agent Stuck in Loop"
- [ ] Check max iterations limit
- [ ] Verify tool descriptions are clear
- [ ] Look for circular dependencies
- [ ] Add loop detection
- [ ] Review agent output for patterns

### "Deployment Fails"
- [ ] Check environment variables
- [ ] Verify all dependencies listed
- [ ] Check build logs
- [ ] Test locally first
- [ ] Review platform-specific requirements

### "High Costs"
- [ ] Check for unnecessary API calls
- [ ] Verify caching is working
- [ ] Use cheaper models for simple tasks
- [ ] Review context sizes
- [ ] Check for duplicate requests
