import { NextRequest, NextResponse } from 'next/server'

interface ShortenRequest {
  url: string
  custom_code?: string
  expires_at?: string
}

interface ShortenResponse {
  short_code: string
  short_url: string
}

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body: ShortenRequest = await request.json()

    // Validate request
    if (!body.url) {
      return NextResponse.json(
        { detail: 'URL is required' },
        { status: 400 }
      )
    }

    // Get backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    // Forward all fields to backend
    const backendBody: any = { url: body.url }
    if (body.custom_code) backendBody.custom_code = body.custom_code
    if (body.expires_at) backendBody.expires_at = body.expires_at

    // Call backend API
    const response = await fetch(`${backendUrl}/shorten`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendBody),
    })

    // Handle backend errors
    if (!response.ok) {
      const errorData = await response.json()
      return NextResponse.json(
        { detail: errorData.detail || 'Failed to shorten URL' },
        { status: response.status }
      )
    }

    // Return successful response
    const data: ShortenResponse = await response.json()
    return NextResponse.json(data, { status: 201 })
  } catch (error) {
    console.error('Error in /api/shorten:', error)

    // Network or parsing errors
    const errorMessage = error instanceof Error ? error.message : 'Internal server error'
    return NextResponse.json(
      { detail: `Failed to connect to backend: ${errorMessage}` },
      { status: 502 }
    )
  }
}
