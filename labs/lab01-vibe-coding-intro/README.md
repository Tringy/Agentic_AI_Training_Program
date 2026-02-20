# Lab 01: Vibe Coding Introduction

## Objective
Build and deploy a URL shortener using AI-assisted development to experience the "Vibe Coding" workflow.

**Time Allotted**: 1 hour 15 minutes

## Learning Goals
- Practice AI-assisted scaffolding
- Experience iterative development with AI
- Deploy to Vercel
- Understand the human-AI collaboration loop

---

## Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- Anthropic/OpenAI API key configured
- Vercel account created

---

## Project Overview

You'll build a URL shortener with:
- **Backend**: Python FastAPI (generates short codes, stores mappings)
- **Frontend**: TypeScript Next.js (simple UI)
- **Deployment**: Vercel (both frontend and API)

```
┌─────────────────────────────────────────────────────────────┐
│                    URL Shortener Architecture               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User → [Next.js Frontend] → [FastAPI Backend] → [SQLite]  │
│                                                             │
│  1. User enters long URL                                    │
│  2. Frontend calls /api/shorten                             │
│  3. Backend generates short code                            │
│  4. Backend stores mapping in SQLite                        │
│  5. Frontend displays short URL                             │
│                                                             │
│  Redirect Flow:                                             │
│  User visits short URL → Backend looks up → Redirects       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Instructions

### Step 1: Understand the Starter Code (5 min)

Examine the provided files:
- `backend/main.py` - FastAPI skeleton
- `frontend/` - Next.js project structure
- `requirements.txt` - Python dependencies
- `package.json` - Node dependencies

### Step 2: Use AI to Implement the Backend (20 min)

**Task**: Use your AI coding assistant to complete the backend.

**Prompt to use**:
```
I'm building a URL shortener backend with FastAPI. Here's my current code:

[paste contents of backend/main.py]

Please implement:
1. POST /shorten - accepts {"url": "https://..."} and returns {"short_code": "abc123", "short_url": "http://localhost:8000/abc123"}
2. GET /{short_code} - redirects to the original URL
3. Use SQLite for storage (file: urls.db)
4. Generate 6-character alphanumeric codes
5. Add input validation for URLs
6. Handle duplicate URLs (return existing short code)

Use Python best practices and type hints.
```

**What to look for in the AI response**:
- Proper async/await usage
- Input validation with Pydantic
- Error handling for invalid URLs and missing codes
- Clean code structure

### Step 3: Test the Backend Locally (5 min)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload

# Test with curl
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url/path"}'

# Should return something like:
# {"short_code": "abc123", "short_url": "http://localhost:8000/abc123"}

# Test redirect
curl -I http://localhost:8000/abc123
# Should show 307 redirect to original URL
```

### Step 4: Use AI to Build the Frontend (20 min)

**Task**: Use AI to create a simple frontend.

**Prompt to use**:
```
Create a simple Next.js 14 frontend for a URL shortener.

Requirements:
1. Single page with input field for URL
2. Submit button that calls POST /api/shorten
3. Display the shortened URL with copy button
4. Show loading state during API call
5. Handle errors gracefully
6. Use Tailwind CSS for styling
7. Make it responsive

The API endpoint is: POST /api/shorten with body {"url": "..."}
Returns: {"short_code": "...", "short_url": "..."}
```

### Step 5: Connect Frontend to Backend (10 min)

Update the frontend to call the correct API endpoint:
- For local development: `http://localhost:8000`
- For production: Use environment variable

**Prompt to use**:
```
Update this frontend code to:
1. Use an environment variable NEXT_PUBLIC_API_URL for the backend URL
2. Default to http://localhost:8000 for local development
3. Add proper error handling for network failures
```

### Step 6: Deploy to Vercel (15 min)

#### Backend Deployment (Railway alternative for Python)

Since Vercel works best with Node.js, we'll deploy the backend to Railway:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize and deploy
cd backend
railway init
railway up

# Set environment variables if needed
railway variables set DATABASE_URL=./urls.db

# Get the URL
railway status
# Note the URL for frontend configuration
```

#### Frontend Deployment (Vercel)

```bash
# From frontend directory
cd frontend

# Deploy to Vercel
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter your Railway backend URL

# Deploy to production
vercel --prod
```

### Step 7: Verify Deployment (5 min)

1. Open your Vercel URL
2. Enter a long URL
3. Click shorten
4. Verify the short URL works

---

## Deliverables Checklist

- [ ] Backend running locally and tests passing
- [ ] Frontend running locally and connecting to backend
- [ ] Backend deployed to Railway (or similar)
- [ ] Frontend deployed to Vercel
- [ ] End-to-end URL shortening works

---

## Starter Code Files

### backend/main.py
```python
"""URL Shortener Backend - Starter Code"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional

app = FastAPI(title="URL Shortener")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    short_code: str
    short_url: str

# TODO: Implement database connection
# TODO: Implement POST /shorten endpoint
# TODO: Implement GET /{short_code} redirect

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### backend/requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
aiosqlite==0.19.0
python-dotenv==1.0.0
```

### frontend/package.json
```json
{
  "name": "url-shortener-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "tailwindcss": "^3.4.1",
    "postcss": "^8",
    "autoprefixer": "^10"
  }
}
```

---

## Hints

### If Backend Isn't Working
- Check if SQLite database file was created
- Verify URL validation is accepting your test URLs
- Check CORS is allowing your frontend origin

### If Frontend Can't Connect
- Verify API URL in environment variables
- Check browser console for CORS errors
- Ensure backend is running before frontend calls it

### If Deployment Fails
- Check build logs for errors
- Verify all dependencies are listed
- Ensure environment variables are set in deployment platform

---

## Extension Challenges (If Time Permits)

1. **Analytics**: Track click counts for each short URL
2. **Custom Codes**: Allow users to specify custom short codes
3. **Expiration**: Add optional expiration dates for URLs
4. **QR Codes**: Generate QR code for short URLs

---

## Reflection Questions

After completing the lab, consider:

1. How did AI assistance change your development speed?
2. What did you have to manually adjust in the AI-generated code?
3. When did you need to provide more context to the AI?
4. What would you do differently next time?

---

**Next**: [Lab 02 - Code Analyzer Agent](../lab02-code-analyzer-agent/)
