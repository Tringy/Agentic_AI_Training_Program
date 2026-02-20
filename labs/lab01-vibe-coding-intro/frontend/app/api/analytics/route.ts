import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const params = request.nextUrl.searchParams.toString()
    const url = params ? `${backendUrl}/api/analytics?${params}` : `${backendUrl}/api/analytics`

    const res = await fetch(url)
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upstream error' }))
      return NextResponse.json({ detail: err.detail || 'Failed to fetch analytics' }, { status: res.status })
    }

    const data = await res.json()
    return NextResponse.json(data, { status: 200 })
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Internal server error'
    return NextResponse.json({ detail: `Failed to connect to backend: ${msg}` }, { status: 502 })
  }
}
