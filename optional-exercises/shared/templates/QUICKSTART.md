# Quick Start Guide

Get up and running with these templates in under 5 minutes.

## Prerequisites

### FastAPI Template
- Python 3.11+
- pip or pipenv

### Next.js Template
- Node.js 18+
- npm, pnpm, or yarn

### Both Templates
- Anthropic API key ([Get one here](https://console.anthropic.com/))

---

## FastAPI Quick Start

### 1. Copy Template
```bash
cp -r fastapi-template my-api-project
cd my-api-project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 5. Run Server
```bash
python -m app.main
```

### 6. Test It
Visit http://localhost:8000/docs

Try the `/api/chat` endpoint:
```json
{
  "message": "Hello! Explain quantum computing in one sentence.",
  "max_tokens": 100
}
```

**That's it!** You have a production-ready API running.

---

## Next.js Quick Start

### 1. Copy Template
```bash
cp -r nextjs-template my-web-project
cd my-web-project
```

### 2. Install Dependencies
```bash
npm install
# or
pnpm install
# or
yarn install
```

### 3. Configure Environment
```bash
cp .env.example .env.local
```

Edit `.env.local` and add your API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 4. Run Development Server
```bash
npm run dev
```

### 5. Open Browser
Visit http://localhost:3000

Start chatting with the AI!

**That's it!** You have a working chat interface.

---

## Fullstack Quick Start

Want both frontend and backend? Here's how to run them together.

### 1. Copy Both Templates
```bash
mkdir my-fullstack-project
cd my-fullstack-project

cp -r ../fastapi-template ./backend
cp -r ../nextjs-template ./frontend
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
```

### 3. Setup Frontend
```bash
cd ../frontend
npm install
cp .env.example .env.local
# Add ANTHROPIC_API_KEY to .env.local
```

### 4. Run Both (in separate terminals)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access Your App
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

---

## Next Steps

### FastAPI
1. Add new endpoints in `app/routers/api.py`
2. Create Pydantic models in `app/models/schemas.py`
3. Implement business logic in `app/services/`
4. Write tests in `tests/`

### Next.js
1. Add pages in `app/[page]/page.tsx`
2. Create components in `components/`
3. Add API routes in `app/api/[route]/route.ts`
4. Style with Tailwind CSS

### Production Deployment

**FastAPI:**
```bash
docker build -t my-api .
docker run -p 8000:8000 --env-file .env my-api
```

**Next.js:**
```bash
npm run build
npm run start
```

Or deploy to:
- Vercel (Next.js - one click)
- Railway (Both - connect GitHub)
- Render (Both - web services)

---

## Common Commands

### FastAPI
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Next.js
```bash
# Development
npm run dev

# Production build
npm run build
npm run start

# Linting
npm run lint

# Type checking
npm run type-check
```

---

## Troubleshooting

### "Module not found" Error

**FastAPI:**
```bash
pip install -r requirements.txt
```

**Next.js:**
```bash
rm -rf node_modules
npm install
```

### "API Key Invalid"

1. Check your `.env` or `.env.local` file
2. Ensure key starts with `sk-ant-`
3. Verify key is active in [Anthropic Console](https://console.anthropic.com/)
4. Restart the server after updating

### "Port Already in Use"

**FastAPI - Change port:**
```bash
# In .env
PORT=8001

# Or run directly
uvicorn app.main:app --port 8001
```

**Next.js - Change port:**
```bash
npm run dev -- -p 3001
```

### "CORS Error" (Fullstack)

Update FastAPI CORS settings in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Getting Help

1. Check the README in each template
2. Review curriculum materials in `/curriculum/`
3. Look at example projects in `/labs/`
4. Ask during office hours
5. Check Anthropic API docs

---

## Tips for Success

1. **Start Simple**: Get the basic template working first
2. **Test Often**: Make changes incrementally and test
3. **Read Docs**: Interactive API docs at `/docs` (FastAPI)
4. **Use Git**: Commit early and often
5. **Stay Organized**: Follow the folder structure
6. **Handle Errors**: Always show user-friendly error messages
7. **Log Everything**: Use logging for debugging
8. **Secure Keys**: Never commit `.env` files

---

**Ready to build something amazing?** Choose a template and start coding!

For detailed documentation, see the README.md in each template directory.
