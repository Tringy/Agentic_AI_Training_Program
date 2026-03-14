---
applyTo: "**/frontend/app/**,**/frontend/components/**,**/frontend/types.ts"
---

# Next.js Frontend Skill

You are working on a Next.js 14+ (App Router) frontend that is part of the Agentic AI Training Program.

## App Router Conventions

- All pages are in `app/` and export a default React component
- Interactive components must start with `'use client'`
- Use `NEXT_PUBLIC_API_URL` for all API calls — never hardcode backend URLs
- The API base is always `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"`

## Standard `fetch` Pattern

```tsx
'use client'
import { useState } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function MyComponent() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/endpoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: 'value' }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Request failed')
      }
      const data = await res.json()
      // handle data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }
}
```

## Cache Header Handling

Show whether a result was served from cache using the `X-Cache` response header:

```tsx
const res = await fetch(`${API_BASE}/analyze`, { method: 'POST', ... })
const cacheStatus = res.headers.get('X-Cache') // "HIT" | "MISS" | null
const data = await res.json()
```

## Tailwind CSS Conventions

Use Tailwind utility classes with the project's colour palette — white cards, gray text, blue/indigo accents:

```tsx
// Card container
<div className="bg-white rounded-lg shadow-lg p-8 space-y-4">

// Primary button
<button className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg transition-colors">

// Error message
<div className="text-red-600 text-sm mt-2">{error}</div>

// Badge: severity
const severityColors = {
  critical: 'bg-red-100 text-red-800',
  high:     'bg-orange-100 text-orange-800',
  medium:   'bg-yellow-100 text-yellow-800',
  low:      'bg-blue-100 text-blue-800',
}
```

## Standard Page Layout (`layout.tsx`)

```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navigation from '@/components/Navigation'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Lab Name',
  description: 'Description',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 min-h-screen`}>
        <Navigation />
        <main>{children}</main>
      </body>
    </html>
  )
}
```

## Navigation Component Pattern

Navigation links use `usePathname()` to highlight the active route:

```tsx
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Home' },
  { href: '/analytics', label: 'Analytics' },
  { href: '/manage', label: 'Manage' },
]

export default function Navigation() {
  const pathname = usePathname()
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-4xl mx-auto px-4 py-3 flex gap-4">
        {links.map(({ href, label }) => (
          <Link key={href} href={href}
            className={pathname === href ? 'text-blue-600 font-semibold' : 'text-gray-600 hover:text-gray-900'}>
            {label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
```

## TypeScript Type Conventions

Define all API response types in `types.ts` at the frontend root:

```ts
// types.ts
export interface AnalysisResult {
  summary: string
  issues: Issue[]
  suggestions: string[]
  metrics: Metrics
}

export interface Issue {
  severity: 'critical' | 'high' | 'medium' | 'low'
  line: number | null
  category: 'bug' | 'security' | 'performance' | 'style' | 'maintainability'
  description: string
  suggestion: string
}
```

## Environment Variable Rules

- Development: `NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000`
- Docker dev: set to `http://localhost:8000` (host network, not container name)
- Production (Fly.io): set in both `[build.args]` **and** `[env]` in `fly.toml`
- Never reference a backend container name (e.g., `http://backend:8000`) from the browser

## Windows/WSL Hot-Reload

The `docker-compose.yml` for frontend always includes:

```yaml
environment:
  WATCHPACK_POLLING: "true"
  CHOKIDAR_USEPOLLING: "true"
```

If hot-reload stops working, verify these vars are set.
