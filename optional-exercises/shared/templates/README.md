# Production-Ready Project Templates

Copy-paste ready templates for building AI-powered applications with industry best practices.

## Available Templates

### 1. FastAPI Template
**Location:** `fastapi-template/`

A production-ready Python backend with:
- FastAPI with async support
- Anthropic Claude integration
- CORS middleware
- Pydantic validation
- Error handling
- Docker support
- Basic testing

**Quick Start:**
```bash
cd fastapi-template
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
python -m app.main
```

Visit: http://localhost:8000/docs

**Best For:**
- AI agents and assistants
- Data processing APIs
- Microservices
- Backend services

---

### 2. Next.js Template
**Location:** `nextjs-template/`

A production-ready React frontend with:
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Chat interface component
- API routes for LLM
- Responsive design

**Quick Start:**
```bash
cd nextjs-template
npm install
cp .env.example .env.local
# Add your ANTHROPIC_API_KEY to .env.local
npm run dev
```

Visit: http://localhost:3000

**Best For:**
- Chat applications
- AI-powered web apps
- Fullstack projects
- User interfaces

---

## Template Features Comparison

| Feature | FastAPI | Next.js |
|---------|---------|---------|
| Language | Python | TypeScript |
| Type Safety | Pydantic | TypeScript |
| API Docs | Automatic | Manual |
| Frontend | None | React |
| SSR/SSG | N/A | Yes |
| Docker | Included | Optional |
| Testing | Pytest | Jest (add) |
| LLM Integration | Server-side | Client + Server |

## Usage Patterns

### Standalone Backend (FastAPI only)
Use when building:
- APIs consumed by mobile apps
- Microservices
- Data processing services
- Integrations with existing frontends

### Standalone Frontend (Next.js only)
Use when:
- Building UI for existing API
- Creating static sites
- Deploying to Vercel/Netlify

### Fullstack (Both templates)
Use when building:
- Complete web applications
- Chat interfaces
- AI-powered SaaS products

**Setup:**
1. Run FastAPI backend on port 8000
2. Run Next.js frontend on port 3000
3. Configure CORS in FastAPI
4. Update Next.js API URLs

## Production Deployment

### FastAPI Deployment Options
- **Docker:** Use included Dockerfile
- **Railway:** Connect GitHub repo
- **Render:** Deploy as web service
- **AWS/GCP/Azure:** Container services

### Next.js Deployment Options
- **Vercel:** Push to GitHub (recommended)
- **Netlify:** Connect repository
- **Cloudflare Pages:** Git integration
- **Docker:** Build static export

## Customization Guide

### Adding Database (FastAPI)
1. Add SQLAlchemy to requirements.txt
2. Create `app/database.py` with connection
3. Add models in `app/models/`
4. Use in routers with dependency injection

### Adding Authentication
**FastAPI:**
- Use python-jose for JWT
- Add OAuth2 with Password Bearer
- Create auth router

**Next.js:**
- Use NextAuth.js
- Add auth providers
- Protect API routes

### Adding Features

#### FastAPI
- **New endpoints:** Add to `app/routers/`
- **New models:** Add to `app/models/schemas.py`
- **Business logic:** Add to `app/services/`

#### Next.js
- **New pages:** Add to `app/[page]/page.tsx`
- **New API routes:** Add to `app/api/[route]/route.ts`
- **New components:** Add to `components/`

## Learning Resources

### FastAPI
- [Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)

### Next.js
- [Official Docs](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### AI Development
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- Course curriculum in `/curriculum/`

## Examples Built With These Templates

Students have built:
- Code review assistants
- Documentation generators
- Data analysis chatbots
- Customer support agents
- Content creation tools
- Research assistants

## Support

### Common Issues

**"Module not found"**
- FastAPI: Run `pip install -r requirements.txt`
- Next.js: Run `npm install`

**"API key not configured"**
- Check `.env` (FastAPI) or `.env.local` (Next.js)
- Ensure ANTHROPIC_API_KEY is set
- Restart the server after adding

**"CORS errors"**
- Update `allow_origins` in FastAPI main.py
- Ensure Next.js URL is in allowed origins

**"Port already in use"**
- FastAPI: Change PORT in .env
- Next.js: Run `npm run dev -- -p 3001`

## Contributing

Found a bug or want to improve these templates?
- Report issues in course repository
- Suggest improvements during office hours
- Share your customizations with the class

## License

MIT - Use freely for your projects and portfolio

---

**Ready to build?** Choose a template above and start coding!
