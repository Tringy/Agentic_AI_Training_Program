# Next.js Production Template

A production-ready Next.js template with TypeScript, Tailwind CSS, and AI integration.

## Features

- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- AI chat interface component
- API routes for LLM integration
- Environment variable configuration
- Production-ready build setup
- Responsive design

## Quick Start

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
# or
yarn install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```
ANTHROPIC_API_KEY=your-api-key-here
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### 3. Run Development Server

```bash
npm run dev
# or
pnpm dev
# or
yarn dev
```

Visit http://localhost:3000

### 4. Build for Production

```bash
# Build
npm run build

# Start production server
npm run start
```

## Project Structure

```
nextjs-template/
├── app/
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Home page with chat interface
│   └── api/
│       └── chat/
│           └── route.ts    # API endpoint for LLM
├── components/
│   └── ChatInterface.tsx   # Reusable chat component
├── lib/
│   └── llm-client.ts       # Client-side LLM utilities
├── public/                 # Static assets
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── next.config.js         # Next.js config
├── tailwind.config.ts     # Tailwind config
└── .env.example           # Environment template
```

## Components

### ChatInterface

A production-ready chat component with:
- Message history
- Loading states
- Error handling
- Markdown rendering
- Auto-scroll
- Responsive design

Usage:
```tsx
import ChatInterface from '@/components/ChatInterface';

export default function Page() {
  return <ChatInterface />;
}
```

## API Routes

### POST /api/chat

Send messages to AI and get responses.

Request:
```json
{
  "message": "Hello, how are you?",
  "history": []
}
```

Response:
```json
{
  "message": "I'm doing well, thank you for asking!",
  "model": "claude-3-5-sonnet-20241022"
}
```

## Environment Variables

### Required

- `ANTHROPIC_API_KEY`: Your Anthropic API key

### Optional

- `NEXT_PUBLIC_API_URL`: API base URL (default: current origin)
- `DEFAULT_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `MAX_TOKENS`: Maximum response tokens (default: 1024)

## Styling

This template uses Tailwind CSS. Customize colors and themes in `tailwind.config.ts`.

### Dark Mode

Dark mode is supported out of the box. Toggle with:
```tsx
<html className="dark">
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Other Platforms

This template works with:
- Netlify
- Railway
- Render
- AWS Amplify
- Cloudflare Pages

### Docker (Optional)

```bash
# Build
docker build -t nextjs-app .

# Run
docker run -p 3000:3000 nextjs-app
```

## Development Tips

### Adding New Pages

Create files in `app/` directory:
```
app/
  about/
    page.tsx      # /about route
  dashboard/
    page.tsx      # /dashboard route
```

### Adding New API Routes

Create files in `app/api/` directory:
```
app/
  api/
    users/
      route.ts    # /api/users endpoint
```

### Using TypeScript

All components use TypeScript. Example:
```tsx
interface Props {
  message: string;
}

export default function Component({ message }: Props) {
  return <div>{message}</div>;
}
```

### Client vs Server Components

- Use `'use client'` for interactive components
- Server components are default and more performant
- API calls in Server Components don't expose API keys

## Testing

Add testing with:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

## Performance

This template includes:
- Server-side rendering
- Static generation where possible
- Image optimization
- Font optimization
- Automatic code splitting

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Anthropic API Docs](https://docs.anthropic.com/)

## License

MIT - Use freely for your projects
