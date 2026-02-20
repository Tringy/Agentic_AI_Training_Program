/**
 * Response Parsing Utilities - TypeScript
 *
 * Utilities for extracting structured data from LLM responses.
 * TypeScript mirror of Python shared_utils.parsing
 *
 * @example
 * ```typescript
 * import { extractJSON, extractCodeBlock } from '@ai-training/shared-utils/parsing';
 *
 * const response = await client.chat(messages);
 * const data = extractJSON(response);
 * const code = extractCodeBlock(response, 'python');
 * ```
 */

/**
 * Extract JSON from LLM response, handling markdown code blocks.
 *
 * @param response - Raw LLM response text
 * @param strict - If true, throw error on invalid JSON
 * @returns Parsed JSON object
 *
 * @example
 * ```typescript
 * const response = '```json\n{"key": "value"}\n```';
 * const data = extractJSON(response);
 * console.log(data.key); // 'value'
 * ```
 */
export function extractJSON(response: string, strict: boolean = false): Record<string, any> {
  let cleaned = response;

  // Step 1: Remove markdown code blocks
  if (cleaned.includes('```json')) {
    const parts = cleaned.split('```json');
    if (parts.length > 1) {
      cleaned = parts[1].split('```')[0];
    }
  } else if (cleaned.includes('```')) {
    const parts = cleaned.split('```');
    if (parts.length > 1) {
      cleaned = parts[1].split('```')[0];
    }
  }

  // Step 2: Strip whitespace
  cleaned = cleaned.trim();

  // Step 3: Try direct parse
  try {
    return JSON.parse(cleaned);
  } catch {
    // Continue to regex extraction
  }

  // Step 4: Try regex extraction for {...} or [...]
  const jsonMatch = cleaned.match(/(\{.*\}|\[.*\])/s);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[1]);
    } catch {
      // Continue to error handling
    }
  }

  // Step 5: Handle failure
  if (strict) {
    throw new Error(
      `Could not extract valid JSON from response. ` +
      `First 200 chars: ${response.substring(0, 200)}...`
    );
  }

  return {};
}

/**
 * Extract JSON array from LLM response.
 *
 * @param response - Raw LLM response
 * @param strict - Throw error if not valid array
 * @returns Array of objects
 */
export function extractJSONArray(response: string, strict: boolean = false): any[] {
  const result = extractJSON(response, strict);

  if (Array.isArray(result)) {
    return result;
  } else if (typeof result === 'object' && result !== null) {
    return [result];
  }

  return [];
}

/**
 * Extract code block from markdown response.
 *
 * @param response - Raw LLM response
 * @param language - Specific language to extract (optional)
 * @param fallbackToFull - Return full response if no code block found
 * @returns Extracted code string
 *
 * @example
 * ```typescript
 * const response = '```python\ndef hello():\n    pass\n```';
 * const code = extractCodeBlock(response, 'python');
 * console.log(code); // 'def hello():\n    pass'
 * ```
 */
export function extractCodeBlock(
  response: string,
  language?: string,
  fallbackToFull: boolean = true
): string {
  const pattern = language
    ? new RegExp(`\`\`\`${language}\\n(.*?)\`\`\``, 's')
    : /```(?:\w+)?\n(.*?)```/s;

  const match = response.match(pattern);
  if (match) {
    return match[1].trim();
  }

  return fallbackToFull ? response.trim() : '';
}

/**
 * Extract all code blocks from response with language tags.
 *
 * @param response - LLM response with multiple code blocks
 * @returns Array of code blocks with language info
 */
export function extractAllCodeBlocks(response: string): Array<{ language: string; code: string }> {
  const blocks: Array<{ language: string; code: string }> = [];
  const pattern = /```(\w+)?\n(.*?)```/gs;

  let match;
  while ((match = pattern.exec(response)) !== null) {
    blocks.push({
      language: match[1] || 'unknown',
      code: match[2].trim()
    });
  }

  return blocks;
}

/**
 * Clean LLM response by removing common artifacts.
 *
 * @param response - Raw LLM response
 * @returns Cleaned response text
 */
export function cleanResponse(response: string): string {
  let cleaned = response.trim();

  // Remove common preambles
  const preambles = [
    /^Sure,?\s+here(?:'s| is)\s+/i,
    /^Here(?:'s| is)\s+/i,
    /^Certainly,?\s+/i,
    /^Of course,?\s+/i
  ];

  for (const pattern of preambles) {
    cleaned = cleaned.replace(pattern, '');
  }

  return cleaned.trim();
}

/**
 * Validate that JSON has required keys.
 *
 * @param data - Parsed JSON data
 * @param requiredKeys - Keys that must exist
 * @returns True if all required keys present
 */
export function validateJSONSchema(data: any, requiredKeys: string[]): boolean {
  if (typeof data !== 'object' || data === null) {
    return false;
  }

  return requiredKeys.every(key => key in data);
}
