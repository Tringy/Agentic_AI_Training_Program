interface Params {
  params: { code: string }
}

export async function GET(_req: Request, { params }: Params) {
  try {
    const { code } = params
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const res = await fetch(`${backendUrl}/api/qrcode/${encodeURIComponent(code)}`)

    // Forward status and headers, stream body
    const headers: Record<string, string> = {}
    const contentType = res.headers.get('content-type')
    if (contentType) headers['content-type'] = contentType

    const arrayBuffer = await res.arrayBuffer()
    return new Response(arrayBuffer, { status: res.status, headers })
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Internal server error'
    return new Response(JSON.stringify({ detail: `Failed to connect to backend: ${msg}` }), { status: 502, headers: { 'content-type': 'application/json' } })
  }
}
