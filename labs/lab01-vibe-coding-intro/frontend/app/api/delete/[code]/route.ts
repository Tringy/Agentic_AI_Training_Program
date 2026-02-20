interface Params {
  params: { code: string }
}

export async function DELETE(_req: Request, { params }: Params) {
  try {
    const { code } = params
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const res = await fetch(`${backendUrl}/${encodeURIComponent(code)}`, { method: 'DELETE' })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upstream error' }))
      return new Response(JSON.stringify({ detail: err.detail || 'Failed to delete URL' }), {
        status: res.status,
        headers: { 'content-type': 'application/json' },
      })
    }

    const data = await res.json()
    return new Response(JSON.stringify(data), { status: 200, headers: { 'content-type': 'application/json' } })
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Internal server error'
    return new Response(JSON.stringify({ detail: `Failed to connect to backend: ${msg}` }), {
      status: 502,
      headers: { 'content-type': 'application/json' },
    })
  }
}
