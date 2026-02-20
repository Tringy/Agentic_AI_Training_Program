# Template Structure Reference

Visual guide to understanding the template organization.

## Directory Overview

```
templates/
├── README.md                    # Main templates guide
├── QUICKSTART.md               # 5-minute setup guide
├── STRUCTURE.md                # This file
├── fastapi-template/           # Python backend template
└── nextjs-template/            # TypeScript frontend template
```

---

## FastAPI Template Structure

```
fastapi-template/
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Container configuration
├── README.md                    # FastAPI-specific docs
├── requirements.txt             # Python dependencies
│
├── app/                         # Main application package
│   ├── __init__.py             # Package marker
│   ├── main.py                 # FastAPI app & middleware (164 lines)
│   │   • App initialization
│   │   • CORS configuration
│   │   • Request logging
│   │   • Error handlers
│   │   • Health endpoints
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   └── api.py              # Example endpoints
│   │       • POST /api/chat    (chat with AI)
│   │       • GET /api/models   (list models)
│   │       • GET /api/status   (API status)
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   │       • ChatRequest       (request validation)
│   │       • ChatResponse      (response schema)
│   │       • ErrorResponse     (error format)
│   │
│   └── services/               # Business logic
│       ├── __init__.py
│       └── llm_service.py      # LLM integration (173 lines)
│           • chat()            (single message)
│           • chat_with_context() (conversation)
│           • Error handling
│           • Retry logic
│
└── tests/                      # Test suite
    └── test_api.py             # API tests
        • Health check tests
        • Validation tests
        • Integration tests
```

### Key Files Explained

**app/main.py** (Core application)
- FastAPI app setup with production settings
- CORS middleware for cross-origin requests
- Request/response logging middleware
- Global exception handlers
- Health check at `/health`
- Routes included from `routers/`

**app/routers/api.py** (API endpoints)
- POST `/api/chat` - Send message, get AI response
- GET `/api/models` - List available models
- GET `/api/status` - Check API status
- Input validation with Pydantic
- Error handling per endpoint

**app/models/schemas.py** (Type definitions)
- ChatRequest - Validates incoming messages
- ChatResponse - Structures AI responses
- Auto-generated OpenAPI docs
- Type safety with Python type hints

**app/services/llm_service.py** (AI integration)
- Anthropic SDK wrapper
- Async chat methods
- Token counting
- Error handling for API failures
- Rate limit handling

**Dockerfile** (Container config)
- Python 3.11 slim base
- Non-root user for security
- Health check endpoint
- Production-ready settings

---

## Next.js Template Structure

```
nextjs-template/
├── .env.example                # Environment variables template
├── .eslintrc.json             # ESLint configuration
├── .gitignore                 # Git ignore rules
├── README.md                  # Next.js-specific docs
├── next.config.js             # Next.js configuration
├── package.json               # Node dependencies
├── postcss.config.js          # PostCSS for Tailwind
├── tailwind.config.ts         # Tailwind CSS config
├── tsconfig.json              # TypeScript configuration
│
├── app/                       # Next.js App Router
│   ├── layout.tsx            # Root layout (fonts, metadata)
│   ├── page.tsx              # Home page with chat
│   ├── globals.css           # Global styles + Tailwind
│   │
│   └── api/                  # API Routes (server-side)
│       └── chat/
│           └── route.ts      # POST /api/chat (121 lines)
│               • Message handling
│               • Anthropic API calls
│               • Error handling
│               • Response formatting
│
├── components/               # React components
│   └── ChatInterface.tsx     # Chat UI component (176 lines)
│       • Message display
│       • Input handling
│       • Loading states
│       • Error display
│       • Auto-scroll
│       • Markdown rendering
│
└── lib/                      # Utilities
    └── llm-client.ts         # Client helpers
        • sendChatMessage()   (API wrapper)
        • buildChatHistory()  (context builder)
        • estimateTokens()    (token counting)
        • formatErrorMessage() (error formatting)
```

### Key Files Explained

**app/layout.tsx** (Root layout)
- HTML structure
- Font configuration (Inter)
- Metadata for SEO
- Global styling wrapper

**app/page.tsx** (Home page)
- Chat interface component
- Header and footer
- Responsive container
- Gradient background

**app/globals.css** (Styles)
- Tailwind directives
- Custom scrollbar styles
- Markdown content styling
- Code block formatting

**app/api/chat/route.ts** (API handler)
- Server-side API route
- Anthropic SDK integration
- Input validation
- Error handling
- Never exposes API key to client

**components/ChatInterface.tsx** (Chat UI)
- Message history management
- Real-time user input
- Loading indicators
- Error display
- Markdown rendering
- Keyboard shortcuts (Enter to send)

**lib/llm-client.ts** (Helpers)
- Client-side utilities
- API call wrapper
- Token estimation
- Error formatting
- Type-safe functions

**Configuration Files:**
- `next.config.js` - Next.js settings, security headers
- `tsconfig.json` - TypeScript strict mode, paths
- `tailwind.config.ts` - Custom colors, animations
- `package.json` - Dependencies, scripts

---

## Comparison: Request Flow

### FastAPI Request Flow

```
1. Client sends POST /api/chat
   ↓
2. FastAPI receives request
   ↓
3. CORS middleware checks origin
   ↓
4. Logging middleware starts timer
   ↓
5. Pydantic validates request body (ChatRequest)
   ↓
6. Router handler (api.py) processes
   ↓
7. LLMService.chat() calls Anthropic
   ↓
8. Response validated (ChatResponse)
   ↓
9. Logging middleware records metrics
   ↓
10. Client receives JSON response
```

### Next.js Request Flow

```
1. User types message in ChatInterface
   ↓
2. Component calls sendMessage()
   ↓
3. Fetch POST to /api/chat
   ↓
4. Next.js API route (route.ts) handles
   ↓
5. Validates request body
   ↓
6. Calls Anthropic SDK server-side
   ↓
7. Formats response
   ↓
8. Returns JSON to component
   ↓
9. Component updates message state
   ↓
10. UI re-renders with AI response
```

---

## Production Patterns

### FastAPI Patterns
- Async/await for non-blocking I/O
- Pydantic for request/response validation
- Dependency injection ready
- Automatic OpenAPI docs
- Type hints everywhere
- Middleware for cross-cutting concerns
- Structured error responses

### Next.js Patterns
- Server Components by default
- Client Components for interactivity
- API routes for backend logic
- TypeScript for type safety
- CSS-in-JS with Tailwind
- Automatic code splitting
- Image and font optimization

---

## Extension Points

### FastAPI Extension Points

**Add Database:**
```python
# app/database.py
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)

# Use in routers with dependency injection
```

**Add Authentication:**
```python
# app/routers/auth.py
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

**Add Background Tasks:**
```python
from fastapi import BackgroundTasks
@router.post("/send-email")
async def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_task)
```

### Next.js Extension Points

**Add Database (Server Side):**
```typescript
// lib/db.ts
import { PrismaClient } from '@prisma/client'
export const db = new PrismaClient()
```

**Add Authentication:**
```typescript
// Use NextAuth.js
import NextAuth from 'next-auth'
// Configure providers
```

**Add State Management:**
```typescript
// Use React Context or Zustand
import { create } from 'zustand'
```

---

## File Size Reference

| File | Lines | Purpose |
|------|-------|---------|
| fastapi-template/app/main.py | 164 | App setup & middleware |
| fastapi-template/app/services/llm_service.py | 173 | LLM integration |
| fastapi-template/app/routers/api.py | ~100 | API endpoints |
| fastapi-template/app/models/schemas.py | ~100 | Data models |
| nextjs-template/components/ChatInterface.tsx | 176 | Chat UI |
| nextjs-template/app/api/chat/route.ts | 121 | API handler |
| nextjs-template/lib/llm-client.ts | ~100 | Client utilities |

**Total Template Code:** ~1000 lines of production-ready code

---

## Dependencies

### FastAPI
- fastapi (0.109.0) - Web framework
- uvicorn (0.27.0) - ASGI server
- pydantic (2.5.3) - Validation
- anthropic (0.18.1) - AI SDK
- pytest (7.4.4) - Testing

### Next.js
- next (14.2.0) - Framework
- react (18.3.0) - UI library
- typescript (5.3.0) - Type safety
- @anthropic-ai/sdk (0.18.0) - AI SDK
- tailwindcss (3.4.0) - Styling
- react-markdown (9.0.0) - Markdown

---

## Quick Reference Commands

### FastAPI
```bash
# Run dev server
python -m app.main

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Run with Docker
docker build -t api . && docker run -p 8000:8000 api
```

### Next.js
```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Run production server
npm run start

# Type check
npm run type-check
```

---

This structure provides a solid foundation for building production-ready AI applications!
