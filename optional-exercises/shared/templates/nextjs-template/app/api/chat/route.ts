import { NextRequest, NextResponse } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || '',
});

// Configuration
const DEFAULT_MODEL = process.env.DEFAULT_MODEL || 'claude-3-5-sonnet-20241022';
const MAX_TOKENS = parseInt(process.env.MAX_TOKENS || '1024', 10);
const TEMPERATURE = parseFloat(process.env.TEMPERATURE || '1.0');

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body = await request.json();
    const { message, history = [] } = body;

    // Validate input
    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required and must be a string' },
        { status: 400 }
      );
    }

    if (message.length > 10000) {
      return NextResponse.json(
        { error: 'Message too long (max 10000 characters)' },
        { status: 400 }
      );
    }

    // Check API key
    if (!process.env.ANTHROPIC_API_KEY) {
      console.error('ANTHROPIC_API_KEY not configured');
      return NextResponse.json(
        { error: 'API key not configured' },
        { status: 500 }
      );
    }

    // Build messages array
    const messages: Anthropic.MessageParam[] = [
      ...history,
      {
        role: 'user' as const,
        content: message,
      },
    ];

    console.log(`Processing chat request: ${message.substring(0, 50)}...`);

    // Call Anthropic API
    const response = await anthropic.messages.create({
      model: DEFAULT_MODEL,
      max_tokens: MAX_TOKENS,
      temperature: TEMPERATURE,
      messages,
    });

    // Extract response text
    const responseText = response.content[0].type === 'text'
      ? response.content[0].text
      : '';

    console.log(`Response received: ${response.usage.input_tokens + response.usage.output_tokens} tokens`);

    // Return response
    return NextResponse.json({
      message: responseText,
      model: response.model,
      tokens: {
        input: response.usage.input_tokens,
        output: response.usage.output_tokens,
        total: response.usage.input_tokens + response.usage.output_tokens,
      },
      stop_reason: response.stop_reason,
    });

  } catch (error: any) {
    console.error('Chat API error:', error);

    // Handle specific error types
    if (error?.status === 401) {
      return NextResponse.json(
        { error: 'Invalid API key' },
        { status: 401 }
      );
    }

    if (error?.status === 429) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Please try again later.' },
        { status: 429 }
      );
    }

    if (error?.status === 500) {
      return NextResponse.json(
        { error: 'AI service error. Please try again.' },
        { status: 500 }
      );
    }

    // Generic error
    return NextResponse.json(
      { error: 'Failed to process request. Please try again.' },
      { status: 500 }
    );
  }
}

// Handle unsupported methods
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST.' },
    { status: 405 }
  );
}
