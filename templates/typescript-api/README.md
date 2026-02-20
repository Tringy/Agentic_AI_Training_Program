# TypeScript API Template with Hono

A lightweight, production-ready TypeScript API template built with [Hono](https://hono.dev/) - an ultrafast web framework for the Edge.

## Features

- Fast and lightweight Hono framework
- TypeScript with strict mode enabled
- Request validation with Zod schemas
- Built-in middleware (CORS, logging, error handling)
- Example LLM integration with Anthropic Claude
- Hot reload development with tsx
- Production-ready error handling
- Health check endpoint
- Type-safe request/response handling

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
PORT=3000
```

### 3. Start Development Server

```bash
npm run dev
```

The server will start at `http://localhost:3000`

### 4. Test the API

**Health Check:**
```bash
curl http://localhost:3000/health
```

**Echo Endpoint:**
```bash
curl "http://localhost:3000/echo?message=Hello"

# Or POST
curl -X POST http://localhost:3000/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, API!"}'
```

**Process Endpoint (LLM):**
```bash
curl -X POST http://localhost:3000/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "model": "claude-3-5-sonnet-20241022",
    "maxTokens": 100
  }'
```

## Project Structure

```
typescript-api/
├── src/
│   ├── index.ts          # Main application entry point
│   ├── routes.ts         # Route handlers
│   ├── middleware.ts     # Custom middleware
│   └── types.ts          # TypeScript types and Zod schemas
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Run production build
- `npm run lint` - Lint code with ESLint
- `npm test` - Run tests with Vitest

## API Endpoints

### GET /
Root endpoint with API information

### GET /health
Health check endpoint
- Returns server status and uptime

### GET /echo?message=hello
Simple echo endpoint
- Query parameter: `message` (optional)

### POST /echo
Echo endpoint with validation
- Body: `{ "message": "string" }`

### POST /process
LLM processing endpoint
- Body:
  ```json
  {
    "prompt": "Your prompt here",
    "model": "claude-3-5-sonnet-20241022",
    "maxTokens": 1024
  }
  ```

## Adding New Routes

1. Define types in `src/types.ts`:
```typescript
export const MySchema = z.object({
  field: z.string(),
});

export type MyInput = z.infer<typeof MySchema>;
```

2. Create route handler in `src/routes.ts`:
```typescript
export const myRoute = [
  zValidator('json', MySchema),
  async (c: Context) => {
    const data = c.req.valid('json');
    return c.json({ result: data });
  },
];
```

3. Register route in `src/index.ts`:
```typescript
app.post('/my-route', ...myRoute);
```

## Deployment

### Build for Production

```bash
npm run build
npm start
```

### Deploy to Render/Railway

1. Push to GitHub
2. Connect your repository to Render/Railway
3. Set environment variables (ANTHROPIC_API_KEY, etc.)
4. Deploy using:
   - Build Command: `npm run build`
   - Start Command: `npm start`

### Environment Variables

Required for deployment:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `PORT` - Port to run server (auto-set by most platforms)
- `NODE_ENV` - Set to `production`

Optional:
- `CORS_ORIGIN` - Allowed CORS origins (default: `*`)
- `LOG_LEVEL` - Logging level (default: `info`)

## Customization

### Change LLM Provider

Replace Anthropic with OpenAI, Google, or Groq in `src/routes.ts`:

```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});
```

### Add Database

Install Prisma or Drizzle ORM:

```bash
npm install prisma @prisma/client
npx prisma init
```

### Add Authentication

Install JWT middleware:

```bash
npm install hono-jwt
```

```typescript
import { jwt } from 'hono/jwt';

app.use('/protected/*', jwt({
  secret: process.env.JWT_SECRET,
}));
```

## Why Hono?

- Ultrafast (faster than Express, Fastify, Koa)
- Edge-ready (works on Cloudflare Workers, Deno, Bun)
- Lightweight (< 20KB)
- TypeScript-first with excellent type inference
- Built-in middleware ecosystem
- Zero dependencies for core functionality

## License

MIT
