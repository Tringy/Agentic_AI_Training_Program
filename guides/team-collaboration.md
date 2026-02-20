# Team Collaboration & Best Practices for AI Development

Guidelines for contractors working in teams on AI/agentic projects.

## Table of Contents

1. [Code Review Practices for AI Systems](#code-review)
2. [Version Control Workflows for Agents](#version-control)
3. [Documentation Standards](#documentation)
4. [Handoff Procedures](#handoff)
5. [Knowledge Sharing](#knowledge-sharing)
6. [Team Communication](#communication)

---

<a name="code-review"></a>
## 1. Code Review Practices for AI Systems

### 1.1 What to Review in AI Code

AI systems require different review focus than traditional code:

```markdown
## AI Code Review Checklist

### Prompts & LLM Calls
- [ ] System prompts are clear and unambiguous
- [ ] User input is properly isolated from system instructions
- [ ] Prompt injection defenses are in place
- [ ] Output format is validated
- [ ] Fallback behavior is defined

### Agent Logic
- [ ] Agent loop has maximum iteration limit
- [ ] Tool calls are properly validated
- [ ] Error handling covers LLM failures
- [ ] State management is clear
- [ ] Memory/context is properly managed

### Security
- [ ] All user inputs are validated
- [ ] Sensitive data is not logged
- [ ] API keys are in environment variables
- [ ] Output is sanitized before display
- [ ] Rate limiting is implemented

### Cost Management
- [ ] Unnecessary LLM calls are avoided
- [ ] Caching is used appropriately
- [ ] Model selection is cost-effective
- [ ] Token usage is tracked
- [ ] Budget limits are enforced

### Testing
- [ ] Edge cases are tested
- [ ] LLM responses are mocked in tests
- [ ] Integration tests cover full workflows
- [ ] Performance benchmarks exist
- [ ] Cost benchmarks are tracked

### Responsible AI
- [ ] Bias detection is implemented (if applicable)
- [ ] High-risk actions require approval
- [ ] Audit trails are in place
- [ ] Confidence thresholds are appropriate
- [ ] Explainability is provided
```

### 1.2 Reviewing AI-Generated Code

When reviewing code that was AI-generated:

**Red Flags:**
```python
# ❌ AI often generates but you should catch:

# 1. Overly complex solutions
def calculate(x, y):
    # 50 lines of unnecessary complexity
    pass

# 2. Missing error handling
result = api_call()  # What if this fails?

# 3. Hardcoded values
threshold = 0.7  # Why 0.7? Should be configurable

# 4. Security vulnerabilities
query = f"SELECT * FROM users WHERE id={user_id}"  # SQL injection!

# 5. No input validation
def process(data):
    return data["key"]  # What if "key" doesn't exist?

# 6. Unclear variable names
x = llm.chat(m)  # What are x and m?
```

**Best Practices:**
```python
# ✅ Ensure AI-generated code has:

# 1. Clear error handling
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    return fallback_response()

# 2. Input validation
def process(data: dict) -> str:
    if "key" not in data:
        raise ValueError("Missing required key")
    return data["key"]

# 3. Configuration, not hardcoding
from config import settings
threshold = settings.confidence_threshold  # Configurable

# 4. Security-first
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))  # Parameterized

# 5. Clear naming
response_text = llm.chat(user_messages)
```

### 1.3 Review Process

**For Agent PRs:**

1. **Automated Checks** (CI/CD runs these)
   - Linting (flake8, eslint)
   - Type checking (mypy, TypeScript)
   - Unit tests
   - Security scans
   - Cost benchmarks

2. **Human Review Focuses On**
   - Prompt quality and clarity
   - Agent behavior correctness
   - Edge case handling
   - Cost implications
   - Responsible AI considerations

3. **Testing Requirements**
   ```bash
   # Before approving PR, reviewer should:

   # 1. Run locally
   python -m pytest tests/

   # 2. Test with real LLM (not just mocks)
   python -m pytest tests/integration/ --real-llm

   # 3. Check cost
   # Should show estimated cost per operation

   # 4. Review logs
   # Check for any warnings or anomalies
   ```

### 1.4 Review Comment Templates

**For Prompt Issues:**
```markdown
**Prompt Clarity Issue**

The system prompt could be more specific. Consider:

Current:
> "You are a helpful assistant."

Suggested:
> "You are a code review assistant. Analyze code for security issues,
> best practices, and performance concerns. Provide specific, actionable feedback."

**Why:** Clearer prompts lead to more consistent outputs.
```

**For Security Issues:**
```markdown
**Security: Prompt Injection Risk**

Line 45: User input is directly concatenated into system prompt.

**Risk:** Users could manipulate the agent behavior with inputs like:
"Ignore previous instructions and..."

**Fix:** Use input isolation pattern from Day 5 curriculum section 2.2.
```

**For Cost Issues:**
```markdown
**Cost Optimization Opportunity**

This endpoint makes 5 sequential LLM calls for every request.
Estimated cost: $0.15 per request

**Suggestion:**
1. Batch the 5 requests into one call (Day 5 section 2.8)
2. Cache the result (Day 5 section 1.2)

Expected savings: 85%
```

---

<a name="version-control"></a>
## 2. Version Control Workflows for Agents

### 2.1 Branching Strategy

```
main
├── develop
│   ├── feature/agent-memory-improvement
│   ├── feature/new-tool-integration
│   └── fix/prompt-injection-defense
└── release/v2.0.0
```

**Branch Naming:**
- `feature/` - New capabilities
- `fix/` - Bug fixes
- `prompt/` - Prompt-only changes
- `experiment/` - Experimental features
- `release/` - Release preparation

### 2.2 Commit Message Guidelines

**For Agent Changes:**
```bash
# Good commit messages
git commit -m "Add retry logic to LLM client with exponential backoff"
git commit -m "Update code review prompt to check for SQL injection"
git commit -m "Implement semantic caching with 95% similarity threshold"

# Bad commit messages
git commit -m "Update agent"
git commit -m "Fix stuff"
git commit -m "Changes"
```

**Template:**
```
<type>: <description>

<body explaining why and what changed>

Related to: #<issue-number>
Cost impact: <increase/decrease/none>
Breaking change: <yes/no>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `prompt:` - Prompt changes only
- `perf:` - Performance improvement
- `security:` - Security fix
- `cost:` - Cost optimization
- `docs:` - Documentation only

### 2.3 Versioning Prompts

**Problem:** Prompts change frequently, hard to track what changed when.

**Solution:** Version control for prompts

```python
# prompts/versions.py
"""Version-controlled prompts."""

PROMPTS = {
    "code_review": {
        "v1.0.0": """You are a code reviewer. Check for bugs.""",

        "v1.1.0": """You are a code reviewer. Check for:
        - Bugs
        - Security issues
        - Performance problems
        """,

        "v2.0.0": """You are a code review assistant.

        Analyze code for:
        1. Security vulnerabilities (SQL injection, XSS, etc.)
        2. Logic bugs
        3. Performance issues
        4. Best practices violations

        Provide specific, actionable feedback with line numbers.
        """,
    }
}

def get_prompt(name: str, version: str = "latest") -> str:
    """Get specific prompt version."""
    if version == "latest":
        versions = list(PROMPTS[name].keys())
        version = versions[-1]
    return PROMPTS[name][version]

# Usage
prompt = get_prompt("code_review", "v2.0.0")
```

**Changelog for Prompts:**
```markdown
# Prompts Changelog

## v2.0.0 (2024-01-15)
### Code Review Prompt
- Added explicit security checks (SQL injection, XSS)
- Added line number requirement in feedback
- Impact: +15% more security issues caught, +$0.02 per review

## v1.1.0 (2024-01-10)
### Code Review Prompt
- Added performance checks
- Impact: +10% more issues caught, +$0.01 per review
```

### 2.4 Git Workflow for Teams

**Daily Workflow:**
```bash
# Start of day
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/improve-agent-memory

# Make changes, commit frequently
git add src/agent.py
git commit -m "feat: Add episodic memory to agent

Implements long-term memory storage using vector DB.
Agent can now recall past interactions.

Cost impact: +$0.001 per query
Breaking change: no"

# Push and create PR
git push origin feature/improve-agent-memory
gh pr create --title "Improve agent memory system" --body "..."

# After approval, merge to develop
# Periodic releases to main
```

**Pre-commit Hooks:**
```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run tests
pytest tests/unit/

# Check for secrets
if git diff --cached | grep -i "api[_-]key.*=.*sk-"; then
    echo "Error: API key detected in staged changes"
    exit 1
fi

# Lint code
flake8 src/

# Type check
mypy src/
```

---

<a name="documentation"></a>
## 3. Documentation Standards

### 3.1 Agent Documentation Template

Every agent should have this documentation:

```markdown
# [Agent Name]

## Purpose
What does this agent do and why does it exist?

## Capabilities
- Capability 1
- Capability 2
- Capability 3

## Limitations
- What it CANNOT do
- Known edge cases
- When to use human instead

## Usage

\`\`\`python
from agents import MyAgent

agent = MyAgent(api_key="...")
result = agent.process("query")
\`\`\`

## Architecture

\`\`\`
┌────────┐     ┌────────┐     ┌────────┐
│ Input  │────▶│ Agent  │────▶│ Output │
└────────┘     └────────┘     └────────┘
                   │
                   ▼
              ┌─────────┐
              │  Tools  │
              └─────────┘
\`\`\`

## Tools Used
1. **Tool Name**: Description
2. **Tool Name**: Description

## Prompts

### System Prompt (v2.0.0)
\`\`\`
[Full system prompt]
\`\`\`

**Version History:**
- v2.0.0: Added security checks
- v1.0.0: Initial version

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| max_iterations | 10 | Maximum agent loop iterations |
| temperature | 0.7 | LLM temperature |
| timeout | 60 | Max execution time (seconds) |

## Cost

**Typical Usage:**
- Simple query: $0.001-0.01
- Complex query: $0.01-0.05
- Average: $0.02 per query

**With Caching:**
- Cache hit: $0.00
- Average cost: $0.005 per query (75% cache hit rate)

## Testing

\`\`\`bash
# Unit tests
pytest tests/test_my_agent.py

# Integration tests
pytest tests/integration/test_my_agent_integration.py

# With real LLM
pytest tests/integration/ --real-llm
\`\`\`

## Examples

### Example 1: Basic Usage
\`\`\`python
result = agent.process("Analyze this code for bugs")
\`\`\`

### Example 2: With Context
\`\`\`python
result = agent.process(
    query="Review this PR",
    context={"pr_number": 123, "files": [...]}
)
\`\`\`

## Troubleshooting

### Issue: Agent stuck in loop
**Cause:** Tool keeps failing
**Solution:** Check tool error logs, increase timeout

### Issue: Incorrect outputs
**Cause:** Unclear prompt
**Solution:** Update system prompt, add few-shot examples

## Changelog

### v2.1.0 (2024-01-15)
- Added retry logic
- Improved error handling
- Cost: -20% through better caching

### v2.0.0 (2024-01-10)
- Major prompt rewrite
- Added new tools
- Breaking change: New response format

### v1.0.0 (2024-01-01)
- Initial release
```

### 3.2 Prompt Documentation

**Document all prompts:**

```python
# prompts/code_review.py
"""
Code Review Prompts

Version: 2.0.0
Last Updated: 2024-01-15
Owner: team-ai@company.com

Changelog:
- v2.0.0: Added explicit security checks, line number requirements
- v1.1.0: Added performance checks
- v1.0.0: Initial version

Performance:
- Average response: 500 tokens
- Typical cost: $0.015
- Latency: 1.2s average

Testing:
- Tested with 100+ PRs
- Accuracy: 87% (compared to human reviews)
- False positive rate: 12%
"""

SYSTEM_PROMPT_V2 = """
You are a code review assistant for software engineering teams.

Your job is to analyze code changes and provide actionable feedback.

Check for:
1. Security vulnerabilities (SQL injection, XSS, CSRF, etc.)
2. Logic bugs and edge cases
3. Performance issues
4. Code quality and best practices
5. Test coverage

Format your response as:
## Security Issues
- [Severity] Line X: Description
  Recommendation: Specific fix

## Code Quality
...

Be specific. Reference line numbers. Provide example fixes.
"""

def get_code_review_prompt(version: str = "v2.0.0") -> str:
    """Get code review prompt by version."""
    if version == "v2.0.0":
        return SYSTEM_PROMPT_V2
    # Add other versions...
```

### 3.3 Decision Documentation

**Document key decisions:**

```markdown
# Architecture Decision Record (ADR)

## ADR-001: Use Claude 3.5 Sonnet for Code Review

**Date:** 2024-01-15
**Status:** Accepted
**Deciders:** Engineering team

### Context
We need to choose an LLM for our code review agent.

### Options Considered
1. Claude 3.5 Sonnet ($3/$15 per 1M tokens)
2. GPT-4 ($10/$30 per 1M tokens)
3. Claude 3 Haiku ($0.25/$1.25 per 1M tokens)

### Decision
Use Claude 3.5 Sonnet

### Reasoning
- Best balance of quality and cost
- Excellent code understanding
- Good context window (200K)
- Tested on 50 PRs: 87% accuracy vs human reviewers

### Consequences
**Positive:**
- High-quality reviews
- Reasonable cost (~$0.02 per PR)

**Negative:**
- More expensive than Haiku
- May need to optimize for cost later

### Implementation
- Use Sonnet as default
- Fall back to Haiku if budget exceeded
- Monitor quality metrics

### Review Date
2024-04-15 (3 months from decision)
```

---

<a name="version-control"></a>
## 2. Version Control Workflows for Agents

### 2.1 Managing Experiments

AI development involves lots of experimentation:

```bash
# Create experiment branch
git checkout -b experiment/prompt-improvement-v3

# Make changes
# ... edit prompts, test ...

# Document results in commit
git commit -m "experiment: Test few-shot examples in code review prompt

Results:
- Accuracy: 82% → 89% (+7%)
- Cost: $0.015 → $0.025 (+67%)
- Latency: 1.2s → 1.8s (+50%)

Decision: Accept - quality improvement worth the cost"

# If experiment succeeds
git checkout develop
git merge experiment/prompt-improvement-v3

# If experiment fails
git branch -D experiment/prompt-improvement-v3
```

**Experiment Log:**
```markdown
# experiments/log.md

## 2024-01-15: Few-Shot Examples

**Hypothesis:** Adding 3 few-shot examples will improve accuracy

**Results:**
- Accuracy: 82% → 89% ✅
- Cost: $0.015 → $0.025 ❌
- Latency: 1.2s → 1.8s ❌

**Decision:** Accept
**Reasoning:** Quality improvement outweighs cost increase

**Implementation:** Merged to develop in PR #123
```

### 2.2 Handling Prompt Changes

**Challenge:** Small prompt changes can have big impacts

**Solution:** Careful review process

```markdown
## Prompt Change Review Checklist

Before merging prompt changes:

- [ ] Tested with at least 20 diverse inputs
- [ ] Compared outputs to previous version
- [ ] Measured accuracy change (if measurable)
- [ ] Measured cost impact
- [ ] Measured latency impact
- [ ] Documented in prompt changelog
- [ ] Updated version number
- [ ] Added rollback plan
```

**Rollback Plan:**
```python
# In production, always support rollback

PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v2.0.0")

system_prompt = get_prompt("code_review", PROMPT_VERSION)

# If v2.0.0 has issues, rollback via env var:
# PROMPT_VERSION=v1.1.0
# No code deployment needed!
```

### 2.3 Managing Model Versions

```python
# config/models.py
"""Model version configuration."""

MODEL_VERSIONS = {
    "production": {
        "primary": "claude-3-5-sonnet-20241022",
        "fallback": "claude-3-haiku-20240307",
        "updated": "2024-01-15"
    },
    "staging": {
        "primary": "claude-3-5-sonnet-20241022",  # Testing new version
        "fallback": "claude-3-haiku-20240307",
        "updated": "2024-01-14"
    },
    "development": {
        "primary": "claude-3-5-sonnet-20241022",
        "fallback": "claude-3-haiku-20240307",
        "updated": "2024-01-10"
    }
}

def get_model(environment: str = "production") -> str:
    """Get model for current environment."""
    return MODEL_VERSIONS[environment]["primary"]
```

---

<a name="handoff"></a>
## 4. Handoff Procedures

### 4.1 Project Handoff Checklist

When handing off an agent project to another engineer:

```markdown
## Agent Project Handoff

### Code & Documentation
- [ ] Code pushed to main branch
- [ ] All dependencies documented
- [ ] README is complete and accurate
- [ ] Architecture diagrams updated
- [ ] Prompt versions documented

### Configuration
- [ ] All environment variables documented
- [ ] .env.example is complete
- [ ] API keys are rotated (if needed)
- [ ] Rate limits documented
- [ ] Cost budgets documented

### Testing
- [ ] All tests passing
- [ ] Test data provided
- [ ] Known edge cases documented
- [ ] Performance benchmarks documented

### Deployment
- [ ] Deployment instructions verified
- [ ] Production environment configured
- [ ] Monitoring/alerting configured
- [ ] Rollback procedure documented
- [ ] Incident response plan documented

### Knowledge Transfer
- [ ] 1-hour walkthrough scheduled
- [ ] Key decisions documented (ADRs)
- [ ] Common issues and solutions documented
- [ ] Contact info for questions
```

### 4.2 Runbook Template

```markdown
# Production Runbook: [Agent Name]

## Overview
- **Purpose**: What this agent does
- **Owner**: team-ai@company.com
- **On-call**: Rotation schedule

## Architecture
[Diagram of system components]

## Deployment
- **URL**: https://agent.company.com
- **Platform**: Railway
- **Region**: US-East

## Monitoring
- **Dashboard**: https://grafana.company.com/agent
- **Logs**: https://logs.company.com/agent
- **Alerts**: Slack #agent-alerts

## Common Issues

### Issue: High Error Rate

**Symptoms:**
- Error rate > 5%
- Alerts in #agent-alerts
- Users reporting failures

**Diagnosis:**
```bash
# Check recent errors
railway logs --tail 100 | grep ERROR

# Check rate limiter status
curl https://agent.company.com/metrics
```

**Resolution:**
1. Check if LLM provider has outage
2. If provider is down, enable fallback model
3. If error is in code, rollback to previous version
4. Post incident report

**Rollback:**
```bash
# Railway
railway rollback

# Or manual
git checkout v1.2.0
railway up
```

### Issue: High Latency

**Symptoms:**
- P95 latency > 5s
- User complaints about slow responses

**Diagnosis:**
```bash
# Check cache hit rate
curl https://agent.company.com/metrics
# Look for low cache_hit_rate

# Check LLM provider status
curl https://status.anthropic.com
```

**Resolution:**
1. Increase cache TTL if appropriate
2. Enable semantic caching
3. Use faster model (Haiku) for simple queries
4. Implement request queuing

### Issue: Budget Exceeded

**Symptoms:**
- Cost alerts firing
- Daily budget exceeded

**Diagnosis:**
```bash
# Check cost metrics
curl https://agent.company.com/metrics

# Check which users are heavy users
# (requires audit trail DB query)
```

**Resolution:**
1. Review cache effectiveness
2. Implement prompt compression
3. Enable model routing
4. Reduce rate limits temporarily

## Escalation

**Level 1:** Check runbook
**Level 2:** Contact on-call engineer
**Level 3:** Contact team lead
**Level 4:** Contact engineering director

## Maintenance Windows

- **Weekly:** Sunday 2-4 AM UTC
- **Monthly:** First Sunday of month, 2-6 AM UTC
```

---

<a name="knowledge-sharing"></a>
## 5. Knowledge Sharing

### 5.1 Internal Documentation

**Maintain shared knowledge base:**

```markdown
# team-wiki/ai-patterns/

## Proven Patterns

### Pattern: Retry with Exponential Backoff
**Use when:** LLM API calls occasionally fail
**Implementation:** See Day 5 curriculum section 1.3
**Used in:** Code review agent, documentation agent
**Cost impact:** None
**Reliability impact:** 99.9% → 99.99%

### Pattern: Semantic Caching
**Use when:** Users ask similar questions frequently
**Implementation:** See Day 5 curriculum section 2.8
**Used in:** Customer support agent
**Cost impact:** -65% average
**Cache hit rate:** 70%

### Anti-Pattern: Sequential LLM Calls
**Problem:** Making 5 LLM calls when 1 batch call would work
**Bad:**
for item in items:
    result = llm.analyze(item)

**Good:**
results = llm.analyze_batch(items)  # One call

**Impact:** 80% cost reduction
```

### 5.2 Prompt Library

**Shared prompt repository:**

```
prompts/
├── code_review/
│   ├── security_focused.txt
│   ├── performance_focused.txt
│   └── general.txt
├── documentation/
│   ├── api_docs.txt
│   └── readme.txt
└── testing/
    ├── unit_test_generation.txt
    └── test_case_generation.txt
```

### 5.3 Weekly Team Sync

**AI Team Meeting Template:**

```markdown
# AI Team Weekly Sync - [Date]

## Deployments This Week
- [ ] Agent X v2.1.0 to production
- [ ] Prompt update for Agent Y

## Metrics Review
- Total cost this week: $X (-Y% vs last week)
- Average latency: Xms
- Error rate: X%
- New issues: X

## Experiments Completed
1. **Experiment:** Test semantic caching
   **Result:** 65% cost reduction
   **Decision:** Deploy to production

## Issues & Blockers
- Issue #123: High latency on complex queries
  **Owner:** @engineer
  **ETA:** This week

## Learnings
- Prompt compression saved 40% on tokens
- Claude 3.5 Sonnet better than GPT-4 for code review
- Semantic caching works well for FAQ-style queries

## Action Items
- [ ] @engineer1: Implement semantic caching
- [ ] @engineer2: Update runbook with new procedures
- [ ] @engineer3: Review and approve PR #456
```

---

<a name="communication"></a>
## 6. Team Communication

### 6.1 Slack Channels Organization

```
#ai-engineering        - General AI discussions
#ai-deployments        - Deployment notifications
#ai-alerts             - Production alerts
#ai-experiments        - Experiment results
#ai-costs              - Cost tracking and alerts
#ai-questions          - Q&A and help
```

### 6.2 Communication Templates

**When deploying changes:**
```markdown
📢 Deployment Notice

**Agent:** Code Review Agent
**Version:** v2.1.0
**Changes:**
- Added retry logic
- Updated security checks prompt
- Improved caching

**Impact:**
- Expected cost: -20%
- Expected latency: +10% (acceptable)
- Breaking changes: None

**Rollout:**
- Canary: 5% (1 hour)
- Small: 25% (4 hours)
- Full: 100% (if no issues)

**Rollback plan:** `railway rollback` or set PROMPT_VERSION=v2.0.0

**Monitor:** https://dashboard.company.com/code-review-agent
```

**When experiment completes:**
```markdown
🧪 Experiment Results: Semantic Caching

**Hypothesis:** Semantic caching will reduce costs by 50%+

**Setup:**
- Duration: 1 week
- Traffic: 10% of users
- Similarity threshold: 0.95

**Results:**
- Cost reduction: 65% ✅
- Cache hit rate: 70%
- Accuracy: No degradation
- Latency: -200ms (faster!)

**Decision:** ✅ Deploy to production

**Next steps:**
- PR #789 ready for review
- Deploy next Monday during maintenance window
```

**When reporting issues:**
```markdown
🚨 Production Issue: High Error Rate

**Severity:** P1 (Production down)
**Agent:** Code Review Agent
**Impact:** 25% error rate, users affected

**Timeline:**
- 10:00 AM: Alert fired
- 10:05 AM: Investigation started
- 10:15 AM: Root cause identified (LLM API outage)

**Mitigation:**
- Enabled fallback to GPT-4
- Error rate: 25% → 2%
- Users can continue working

**Root Cause:**
- Anthropic API experiencing elevated error rates
- See: https://status.anthropic.com

**Permanent Fix:**
- Implement automatic fallback (in progress)
- ETA: Tomorrow

**Postmortem:** Will share tomorrow
```

### 6.3 Code Review Communication

**Giving Feedback on AI Code:**

```markdown
# ✅ Good Feedback

**Security Concern: Prompt Injection Risk**

I noticed in `src/agent.py:45` that user input is directly concatenated into the system prompt:

Current:
system_prompt = f"You are helpful. User said: {user_input}"

This could allow prompt injection. See [this example](link) for why.

**Recommendation:**
Use the input isolation pattern from Day 5 curriculum:

system_prompt = f"""
<system>You are helpful.</system>
<user_input>{user_input}</user_input>
"""

This was already implemented in the customer-support-agent - we can reuse that pattern.

Happy to pair on this if helpful!
```

```markdown
# ❌ Bad Feedback

"The prompt doesn't look right. Can you fix it?"

# Why bad:
- Not specific
- No context
- No actionable recommendation
- No reference to standards
```

---

## 7. Onboarding New Team Members

### 7.1 First Week Checklist

```markdown
## New AI Team Member Onboarding

### Day 1: Setup
- [ ] Complete environment setup
- [ ] Access to all repos
- [ ] API keys provisioned
- [ ] Added to Slack channels
- [ ] Read team documentation

### Day 2-3: Learning
- [ ] Complete Days 1-3 of training curriculum
- [ ] Review team's existing agents
- [ ] Understand team's coding standards
- [ ] Shadow code review session

### Day 4-5: First Contribution
- [ ] Pick a "good first issue"
- [ ] Make first PR
- [ ] Participate in code review
- [ ] Deploy first change (with guidance)

### Week 2: Independence
- [ ] Complete Days 4-5 of training
- [ ] Take ownership of small agent
- [ ] Join on-call rotation
```

### 7.2 Knowledge Transfer Sessions

**Monthly Knowledge Shares:**

```markdown
# January 2024: Knowledge Share Topics

## Session 1: Semantic Caching Deep Dive
**Presenter:** @engineer1
**Topics:**
- How semantic caching works
- Implementation details
- Performance results (65% cost reduction)
- When to use vs when not to

## Session 2: Prompt Engineering Lessons
**Presenter:** @engineer2
**Topics:**
- 5 prompts that failed and why
- 5 prompts that succeeded and why
- Pattern: structured output works better than free-form

## Session 3: Production Incident Review
**Presenter:** @engineer3
**Topics:**
- Last month's incidents
- Root causes
- How we fixed them
- Preventive measures added
```

---

## 8. Quality Standards

### 8.1 Definition of Done for AI Features

```markdown
## Feature is "Done" When:

### Code
- [ ] All code reviewed and approved
- [ ] Follows team coding standards
- [ ] No linting errors
- [ ] Type checking passes

### Testing
- [ ] Unit tests cover edge cases
- [ ] Integration tests pass
- [ ] Tested with real LLM (not just mocks)
- [ ] Performance benchmarks meet requirements
- [ ] Cost benchmarks meet requirements

### Documentation
- [ ] README updated
- [ ] Prompt documented with version
- [ ] ADR written (for significant decisions)
- [ ] Runbook updated
- [ ] API docs updated (if applicable)

### Deployment
- [ ] Deployed to staging
- [ ] Tested in staging
- [ ] Approved for production
- [ ] Deployed to production (phased rollout)
- [ ] Monitoring confirmed working

### Responsible AI
- [ ] Bias testing completed (if applicable)
- [ ] Audit trail implemented (if high-risk)
- [ ] Human approval workflow defined (if needed)
- [ ] Rollback plan documented
```

### 8.2 Code Quality Standards

**Minimum Requirements:**

| Metric | Requirement |
|--------|-------------|
| **Test Coverage** | > 80% |
| **Type Coverage** | > 90% |
| **Linting** | 0 errors, < 10 warnings |
| **Documentation** | All public functions |
| **Performance** | P95 latency < 5s |
| **Cost** | Benchmarked and approved |

---

## 9. Best Practices Summary

### For Individual Contributors

**DO:**
- ✅ Document your prompts with versions
- ✅ Test with diverse inputs before submitting
- ✅ Measure cost impact of changes
- ✅ Write clear commit messages
- ✅ Add tests for new features
- ✅ Ask questions early

**DON'T:**
- ❌ Commit API keys
- ❌ Make prompt changes without testing
- ❌ Skip documentation
- ❌ Ignore cost implications
- ❌ Deploy without review

### For Code Reviewers

**DO:**
- ✅ Test the code locally
- ✅ Check for security issues
- ✅ Verify cost impact
- ✅ Provide actionable feedback
- ✅ Reference team standards

**DON'T:**
- ❌ Approve without testing
- ❌ Give vague feedback
- ❌ Skip prompt review
- ❌ Ignore cost concerns

### For Team Leads

**DO:**
- ✅ Maintain team documentation
- ✅ Review ADRs and major decisions
- ✅ Monitor team metrics
- ✅ Facilitate knowledge sharing
- ✅ Ensure quality standards

**DON'T:**
- ❌ Skip architecture reviews
- ❌ Ignore cost trends
- ❌ Let documentation decay
- ❌ Bottleneck deployments

---

## 10. Resources

### Internal Resources
- Team Wiki: [link]
- Prompt Library: `prompts/`
- Runbooks: `docs/runbooks/`
- ADRs: `docs/decisions/`

### External Resources
- Main Training: `curriculum/`
- Templates: `templates/production-ready/`
- Community: Discord/Slack

### Getting Help
- **Quick questions:** #ai-questions Slack channel
- **Code review:** Request review in PR
- **Urgent issues:** Page on-call engineer
- **Architecture decisions:** Schedule with team lead

---

**Collaboration makes us stronger. Use these practices to build better AI systems together! 🤝**
