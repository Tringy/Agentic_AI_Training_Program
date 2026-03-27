# Capstone Option E: Football Game Review Assistant

## Project Overview

Build a **full-stack, multi-agent** football game review platform combining:
- **Backend**: FastAPI multi-agent system with 4 specialist agents + Supervisor orchestrator for analyzing game performance from journalistic, tactical, technical, and fan perspectives
- **Frontend**: Next.js interactive interface for submitting game details and displaying comprehensive multi-perspective reviews
- **Integration**: Real-time review generation via REST API with structured JSON responses from all agents
- **Deployment**: Full stack on Fly.io with local Docker Compose development environment

**Complexity**: High  
**Estimated Time**: 2.5-3 hours  
**Stack**: Python/FastAPI backend, Next.js/TypeScript frontend, Docker Compose, Fly.io  
**Domain**: Multi-agent orchestration, full-stack development, domain reasoning, API design

---

## Architecture

```
┌──────────────────────────────────────────┐
│    Next.js Frontend (React, Tailwind)    │
│  Port 3000 | localhost:3000              │
├──────────────────────────────────────────┤
│ • GameForm: Game details input           │
│ • ReviewResult: Multi-agent display      │
│ • Sports-themed UI with team colors      │
└──────────────┬───────────────────────────┘
               │ POST /review (JSON)
               │ GET /health
               ▼
┌──────────────────────────────────────────┐
│  FastAPI Backend (Python, Pydantic)      │
│  Port 8000 | localhost:8000              │
├──────────────────────────────────────────┤
│ SupervisorAgent (Orchestrator)           │
│  ├─ JournalistAgent                      │
│  ├─ CoachAgent                           │
│  ├─ AssistantCoachAgent                  │
│  └─ FanAgent                             │
│                                          │
│ LLMClient → Google Generative AI (Gemini) │
└──────────────────────────────────────────┘
```

---

## Project Scope

### What You're Building
1. **Backend**: Multi-agent orchestration system that takes game details and review question, routes them through 4 specialist agents, synthesizes responses into structured JSON
2. **Frontend**: Beautiful, interactive UI for submitting games and displaying results in collapsible sections
3. **Integration**: Seamless frontend-to-backend communication with proper error handling and loading states
4. **Dev Environment**: Local Docker Compose for testing both services together
5. **Deployment**: Production-ready deployment to Fly.io

### What You're NOT Building
- Real statistics API integration (user-provided stats)
- Persistent database of game reviews (stateless per request)
- User authentication/profiles
- Review history or caching
- Mobile app (web-only for now)

---

## How It Works: User Journey

```
1. User opens frontend
   ↓
2. User fills form (game date, teams, score, review question)
   ↓
3. Frontend calls backend POST /review
   ↓
4. Backend Supervisor delegates to 4 specialists:
   - Journalist → highlights and key moments
   - Coach → tactical analysis and strategy
   - AssistantCoach → detailed performance insights
   - Fan → emotional perspective and hot takes
   ↓
5. Backend synthesizes unified game review
   ↓
6. Frontend displays results in collapsible sections
   ↓
7. User reads comprehensive multi-perspective review
```

---

## Requirements

### Must Have (Core - 70%)
- [ ] Four specialist agents:
  - **Journalist**: Analyzes match narrative and key moments
  - **Coach**: Provides tactical analysis and strategy insights
  - **AssistantCoach**: Offers detailed performance breakdown
  - **Fan**: Delivers emotional perspective and commentary
- [ ] Supervisor agent that:
  - Delegates game analysis tasks to specialists
  - Builds context from previous agent results
  - Coordinates iterative workflow
  - Synthesizes final unified review
- [ ] POST `/review` endpoint accepting game details and review question
- [ ] Iterative workflow (journalist → coach → assistant → fan → synthesis)
- [ ] Returns structured JSON with game review and metadata

### Should Have (Polish - 20%)
- [ ] Conversation history in API response (shows agent interactions)
- [ ] Configurable parameters (max_iterations, depth level)
- [ ] Error handling and timeout protection
- [ ] Progress tracking in response

### Nice to Have (Bonus - 10%)
- [ ] Streaming responses (show real-time progress)
- [ ] Web search tool for Researcher agent
- [ ] Reference tracking and citations
- [ ] Multiple report formats (brief, detailed, technical)
- [ ] Agent performance metrics (tokens used, time taken)

---

## Directory Structure

```
option-e-football-review/
├── README.md (this file)
├── docker-compose.yml
├── .gitignore
│
├── python/
│   ├── main.py (FastAPI app)
│   ├── supervisor.py (SupervisorAgent)
│   ├── agents.py (4 specialist agents)
│   ├── llm_client.py (Google Generative AI integration)
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── fly.toml
│   └── .gitignore
│
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── next.config.js
    ├── tailwind.config.ts
    ├── postcss.config.js
    ├── types.ts
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── globals.css
    ├── components/
    │   ├── GameForm.tsx
    │   └── ReviewResult.tsx
    ├── public/
    ├── Dockerfile
    ├── fly.toml
    └── .gitignore
```

---

## Implementation Plan: 7 Phases

### Phase 1: Backend Setup (40 min)
- Create main.py with FastAPI, CORS middleware
- Define Pydantic models (Team, GameReviewRequest, GameReviewResponse)
- Implement /health and placeholder /review endpoints
- Test: `uvicorn python/main:app --reload`

### Phase 2: LLM & Agents (50 min)
- Create llm_client.py (Google Generative AI integration)
- Create agents.py with 4 specialist agents + system prompts
- Test each agent individually
- Set GOOGLE_API_KEY in .env

### Phase 3: Supervisor Orchestration (50 min)
- Create supervisor.py with SupervisorAgent
- Implement run() with delegation loop
- Parse DELEGATE/TASK responses
- Implement _parse_game_review()
- Test with sample games

### Phase 4: Frontend Setup (30 min)
- Initialize Next.js with TypeScript & Tailwind
- Create types.ts matching backend
- Set up layout.tsx with sports theme

### Phase 5: Form Component (40 min)
- Create GameForm with all inputs
- Implement form submission to backend
- Add loading & error states

### Phase 6: Results Component (50 min)
- Create ReviewResult with collapsible sections
- Display review data from all 4 perspectives
- Add sports-themed styling

### Phase 7: Integration & Deployment (50 min)
- Create docker-compose.yml & test locally
- Deploy backend & frontend to Fly.io
- Test end-to-end

**Total: ~310 minutes ≈ 5 hours theory → 2.5-3 hours practice**

---

## API Specification

### POST /review

**Request**:
```json
{
  "game_date": "2024-03-24",
  "home_team": "Manchester City",
  "away_team": "Arsenal",
  "final_score": "2-1",
  "home_score": 2,
  "away_score": 1,
  "review_question": "What was the turning point in this match?",
  "context": "Home team came from behind with a decisive second half performance"
}
```

**Response**:
```json
{
  "game_review": {
    "summary": "Manchester City edged Arsenal in a thrilling encounter with crucial second-half adjustments...",
    "key_moments": [
      "30' - Arsenal opens scoring with a well-worked move",
      "58' - City equalizes after pressing high in midfield",
      "78' - Decisive City goal breaks the deadlock"
    ],
    "tactical_analysis": "City's right flank dominance in second half exploited Arsenal's weakness...",
    "performance_insights": "Manchester City's pressing intensity increased significantly after 55 minutes...",
    "fan_perspective": "What a second half turnaround! City showed true champions' mentality...",
    "final_verdict": "Manchester City deserved winner. Tactical adjustments proved decisive."
  },
  "specialist_perspectives": {
    "journalist": "City stages dramatic comeback in thrilling title clash...",
    "coach": "The shift to 4-2-4 formation in minute 53 unlocked City's attacking potential...",
    "assistant_coach": "Arsenal's defensive setup was vulnerable to City's pressing triggers...",
    "fan": "Absolutely buzzing! City's second half was pure football poetry! 🏆"
  },
  "conversation_history": [
    {
      "iteration": 0,
      "agent": "Supervisor",
      "action": "DELEGATE",
      "content": "Analyzing Manchester City vs Arsenal match..."
    },
    {
      "iteration": 0,
      "agent": "Journalist",
      "action": "RESULT",
      "content": "Key narrative: City's comeback demonstrates resilience..."
    }
  ],
  "metadata": {
    "iterations": 4,
    "agents_used": ["Journalist", "Coach", "AssistantCoach", "Fan"],
    "game_info": ["Manchester City", "Arsenal", "2-1"],
    "duration_seconds": 35.2
  }
}
```

### GET /health

**Response**:
```json
{
  "status": "healthy",
  "service": "football-game-review"
}
```

### Error Responses

**400 Bad Request**:
```json
{"detail": "Review question too short (minimum 10 characters)"}
```

**500 Internal Server Error**:
```json
{"detail": "Review failed: API key not configured"}
```

---

## Getting Started

### Quick Setup

```bash
# 1. Create project structure
mkdir -p option-e-football-review/{python,frontend}
cd option-e-football-review

# 2. Backend environment
cd python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn pydantic google-generativeai python-dotenv

# Create .env
echo "GOOGLE_API_KEY=your-key-here" > .env

# 3. Frontend environment
cd ../frontend
npm create next-app@latest . -- --typescript --tailwind
npm install
```

### Backend Build (Phases 1-3)

**Phase 1: Create main.py**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Football Game Review Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameReviewRequest(BaseModel):
    game_date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    final_score: str
    review_question: str
    context: Optional[str] = None

# TODO: Add GameReviewResponse Pydantic model

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "football-game-review"}

@app.post("/review")
async def review_game(request: GameReviewRequest):
    # TODO: Call SupervisorAgent
    if not request.review_question or len(request.review_question) < 10:
        raise HTTPException(status_code=400, detail="Review question too short")
    
    return {
        "game_review": {},
        "specialist_perspectives": {},
        "conversation_history": [],
        "metadata": {}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Phase 2: Create agents.py & llm_client.py**
```python
# llm_client.py
import os
import google.generativeai as genai

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def chat(self, system: str, user: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        return response.content[0].text

# agents.py - Create specialist agents with system prompts
class SpecialistAgent:
    def __init__(self, llm_client, system_prompt, name):
        self.llm = llm_client
        self.system_prompt = system_prompt
        self.name = name
    
    def execute(self, task: str, context: str = "") -> str:
        user_msg = f"{context}\n\nTask: {task}" if context else f"Task: {task}"
        return self.llm.chat(self.system_prompt, user_msg)

class JournalistAgent(SpecialistAgent):
    def __init__(self, llm_client):
        prompt = "You are a sports journalist. Analyze the match narrative, key moments, drama, and storylines..."
        super().__init__(llm_client, prompt, "Journalist")

class CoachAgent(SpecialistAgent):
    def __init__(self, llm_client):
        prompt = "You are a football coach. Analyze tactics, formations, strategy, and team decisions..."
        super().__init__(llm_client, prompt, "Coach")

# TODO: Add AssistantCoachAgent, FanAgent
```

**Phase 3: Create supervisor.py**

```python
# Key parts of SupervisorAgent
class SupervisorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.specialists = {
            "Journalist": JournalistAgent(llm_client),
            "Coach": CoachAgent(llm_client),
            "AssistantCoach": AssistantCoachAgent(llm_client),
            "Fan": FanAgent(llm_client),
        }
        self.results = {}
        self.conversation_history = []
    
    def run(self, game_date, home_team, away_team, home_score, away_score, review_question, context):
        # Orchestration loop:
        # 1. LLM decides which specialist to delegate to
        # 2. Parse DELEGATE: agent TASK: task format
        # 3. Call specialist
        # 4. Feed result back to LLM
        # 5. Repeat until FINAL: response
        
        # TODO: Implement iteration loop
        pass
    
    def _parse_game_review(self, review_text):
        # TODO: Extract structured response from review text
        pass
```

**Test**:
```bash
uvicorn main:app --reload
curl http://localhost:8000/health
```

### Frontend Build (Phases 4-6)

**Phase 4: Create types.ts**
```typescript
export type GameReviewRequest = {
  game_date: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  final_score: string;
  review_question: string;
  context?: string;
};

export type GameReview = {
  summary: string;
  key_moments: string[];
  tactical_analysis: string;
  performance_insights: string;
  fan_perspective: string;
  final_verdict: string;
};

export type GameReviewResponse = {
  game_review: GameReview;
  specialist_perspectives: Record<string, string>;
  conversation_history: any[];
  metadata: any;
};
```

**Phase 5: Create GameForm.tsx**
```typescript
export function GameForm({ onSubmit }) {
  const [gameDate, setGameDate] = useState("");
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [homeScore, setHomeScore] = useState(0);
  const [awayScore, setAwayScore] = useState(0);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question || question.length < 10) {
      alert("Review question too short");
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/review`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            game_date: gameDate,
            home_team: homeTeam,
            away_team: awayTeam,
            home_score: homeScore,
            away_score: awayScore,
            final_score: `${homeScore}-${awayScore}`,
            review_question: question,
          }),
        }
      );
      
      const result = await response.json();
      onSubmit(result);
    } finally {
      setLoading(false);
    }
  };
  
  return <form onSubmit={handleSubmit}>
    {/* Form inputs for game details */}
  </form>;
}
```

**Phase 6: Create ReviewResult.tsx**
```typescript
export function ReviewResult({ result }) {
  const [expandedSection, setExpandedSection] = useState(null);
  
  if (!result) return null;
  
  return <div className="space-y-4">
    <Section 
      title="Game Summary"
      content={result.game_review.summary}
      expanded={expandedSection === "summary"}
      onToggle={() => setExpandedSection(expandedSection === "summary" ? null : "summary")}
    />
    <Section 
      title="Key Moments"
      content={result.game_review.key_moments.join("\n")}
      expanded={expandedSection === "moments"}
      onToggle={() => setExpandedSection(expandedSection === "moments" ? null : "moments")}
    />
    {/* More sections for tactical, performance, fan perspective */}
  </div>;
}
```

### Integration & Deployment (Phase 7)

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  backend:
    build: ./python
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Test locally**:
```bash
docker-compose up
# http://localhost:3000 → http://localhost:8000/review
```

**Deploy**:
```bash
# Backend
cd python && fly launch && fly deploy && fly secrets set GOOGLE_API_KEY=$KEY

# Frontend
cd frontend && fly launch && fly deploy
# Set NEXT_PUBLIC_API_URL to deployed backend
```

---

## Evaluation Checklist

**Core Features (70%)**:
- [ ] Four specialist agents implemented with distinct system prompts (Journalist, Coach, AssistantCoach, Fan)
- [ ] SupervisorAgent orchestrates all 4 agents correctly
- [ ] Delegation works: parses DELEGATE/TASK format and routes tasks
- [ ] Context building: agents have access to previous results
- [ ] Game review synthesized: agents collaborate to produce unified output
- [ ] Form accepts and validates game input (date, teams, scores, question)
- [ ] API returns proper JSON response matching specification
- [ ] Results display with all 4 perspectives (summary, tactics, performance, fan view)
- [ ] Error handling works for invalid input
- [ ] Conversation history captured and displayed

**Polish (20%)**:
- [ ] Response completes in under 60 seconds
- [ ] Accordion/collapsible sections work smoothly
- [ ] Loading state shows during API call
- [ ] Error messages are clear and helpful
- [ ] Sports-themed styling applied consistently
- [ ] Form prevents empty/short questions
- [ ] Metadata displayed (iterations, duration, agents used)
- [ ] Responsive design (works on different screen sizes)

**Production Readiness (10%)**:
- [ ] Agents produce high-quality, insightful game analysis
- [ ] API handles edge cases gracefully
- [ ] Demo ready with realistic game scenarios
- [ ] Code is clean and well-commented
- [ ] Environment variables configured properly

---

## Extension Ideas

If you finish early:
- Add streaming responses (SSE) to show agent progress in real-time
- Implement review caching for frequently asked questions
- Create "what-if" simulation endpoint (tactical scenarios)
- Add real team data/logos to UI
- Build review history with localStorage persistence
- Integrate real sports API (ESPN, Sportmonks, etc.)
- Implement multi-turn conversations (follow-up questions to agents)
- Add agent performance metrics (response quality, speed)
- Create visualization of agent reasoning and decision flow
- Support multiple sports (basketball, American football, etc.)
- [ ] Responsive UI (works on different screen sizes)

**Production Readiness (10%)**:
- [ ] Agents produce high-quality, actionable coaching advice
- [ ] API handles edge cases gracefully
- [ ] Demo ready with realistic draft scenarios
- [ ] Code is clean and well-commented
- [ ] Environment variables configured properly

---

## Extension Ideas

---

Good luck with your capstone! ⚽🏆
