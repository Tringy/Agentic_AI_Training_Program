import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const res = await fetch(`${backendUrl}/api/cache-stats`)

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upstream error' }))
      return NextResponse.json({ detail: err.detail || 'Failed to fetch cache stats' }, { status: res.status })
    }

    const data = await res.json()
    return NextResponse.json(data, { status: 200 })
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Internal server error'
    return NextResponse.json({ detail: `Failed to connect to backend: ${msg}` }, { status: 502 })
  }
}
