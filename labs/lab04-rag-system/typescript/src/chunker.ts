/**
 * Code Chunker - Intelligent code splitting
 */

import type { CodeChunk } from './types.js';

export class CodeChunker {
  private chunkSize: number;
  private chunkOverlap: number;

  constructor(chunkSize: number = 1000, chunkOverlap: number = 100) {
    this.chunkSize = chunkSize;
    this.chunkOverlap = chunkOverlap;
  }

  /**
   * Chunk a code file intelligently
   */
  chunkFile(content: string, filename: string, language?: string): CodeChunk[] {
    const detectedLanguage = language || this.detectLanguage(filename);

    if (detectedLanguage === 'python') {
      return this.chunkPython(content, filename);
    } else if (['javascript', 'typescript'].includes(detectedLanguage)) {
      return this.chunkJavaScript(content, filename, detectedLanguage);
    } else {
      return this.chunkGeneric(content, filename, detectedLanguage);
    }
  }

  /**
   * Chunk Python code by logical units
   */
  private chunkPython(content: string, filename: string): CodeChunk[] {
    const chunks: CodeChunk[] = [];

    // Pattern for Python functions and classes
    const pattern =
      /((?:^@\w+.*\n)*^(?:def|class|async def)\s+\w+[^:]*:.*?)(?=\n(?:@|\s*def|\s*class|\s*async def)|\Z)/gms;
    const matches = [...content.matchAll(pattern)];

    if (matches.length > 0) {
      // Add header (imports) first
      const firstMatchStart = matches[0].index || 0;
      if (firstMatchStart > 0) {
        const header = content.slice(0, firstMatchStart).trim();
        if (header) {
          chunks.push({
            content: header,
            metadata: {
              filename,
              language: 'python',
              type: 'header',
              lineStart: 1,
            },
            chunkId: `${filename}:header`,
          });
        }
      }

      // Add each function/class
      for (let i = 0; i < matches.length; i++) {
        const match = matches[i];
        const chunkContent = match[1].trim();
        const lineStart =
          content.slice(0, match.index).split('\n').length;

        // Extract name
        const nameMatch = chunkContent.match(/(?:def|class|async def)\s+(\w+)/);
        const name = nameMatch ? nameMatch[1] : `block_${i}`;

        chunks.push({
          content: chunkContent,
          metadata: {
            filename,
            language: 'python',
            type: chunkContent.includes('class ') ? 'class' : 'function',
            name,
            lineStart,
          },
          chunkId: `${filename}:${name}`,
        });
      }

      return chunks;
    }

    return this.chunkGeneric(content, filename, 'python');
  }

  /**
   * Chunk JavaScript/TypeScript code
   */
  private chunkJavaScript(
    content: string,
    filename: string,
    language: string
  ): CodeChunk[] {
    const chunks: CodeChunk[] = [];

    // Simple pattern for functions
    const pattern =
      /(?:export\s+)?(?:async\s+)?(?:function|class|const\s+\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*=>)/g;
    const matches = [...content.matchAll(pattern)];

    if (matches.length > 0 && matches[0].index !== undefined) {
      const firstMatchStart = matches[0].index;

      // Add imports first
      if (firstMatchStart > 0) {
        const header = content.slice(0, firstMatchStart).trim();
        if (header) {
          chunks.push({
            content: header,
            metadata: {
              filename,
              language,
              type: 'header',
              lineStart: 1,
            },
            chunkId: `${filename}:header`,
          });
        }
      }

      // Use generic chunking for the rest
      return [
        ...chunks,
        ...this.chunkGeneric(content.slice(firstMatchStart), filename, language),
      ];
    }

    return this.chunkGeneric(content, filename, language);
  }

  /**
   * Generic chunking by size with overlap
   */
  private chunkGeneric(
    content: string,
    filename: string,
    language: string
  ): CodeChunk[] {
    const chunks: CodeChunk[] = [];
    const lines = content.split('\n');

    let currentChunk: string[] = [];
    let currentSize = 0;
    let chunkStart = 1;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lineSize = line.length + 1;

      if (currentSize + lineSize > this.chunkSize && currentChunk.length > 0) {
        const chunkContent = currentChunk.join('\n');
        chunks.push({
          content: chunkContent,
          metadata: {
            filename,
            language,
            type: 'block',
            lineStart: chunkStart,
            lineEnd: chunkStart + currentChunk.length - 1,
          },
          chunkId: `${filename}:lines_${chunkStart}`,
        });

        // Keep overlap
        const overlapLines = Math.floor(this.chunkOverlap / 50);
        currentChunk =
          overlapLines > 0 ? currentChunk.slice(-overlapLines) : [];
        currentSize = currentChunk.reduce((sum, l) => sum + l.length + 1, 0);
        chunkStart = i + 1 - currentChunk.length;
      }

      currentChunk.push(line);
      currentSize += lineSize;
    }

    // Don't forget last chunk
    if (currentChunk.length > 0) {
      const chunkContent = currentChunk.join('\n');
      chunks.push({
        content: chunkContent,
        metadata: {
          filename,
          language,
          type: 'block',
          lineStart: chunkStart,
        },
        chunkId: `${filename}:lines_${chunkStart}`,
      });
    }

    return chunks;
  }

  /**
   * Detect language from filename
   */
  private detectLanguage(filename: string): string {
    const extMap: Record<string, string> = {
      '.py': 'python',
      '.js': 'javascript',
      '.ts': 'typescript',
      '.jsx': 'javascript',
      '.tsx': 'typescript',
      '.java': 'java',
      '.go': 'go',
      '.rs': 'rust',
      '.rb': 'ruby',
    };

    for (const [ext, lang] of Object.entries(extMap)) {
      if (filename.endsWith(ext)) {
        return lang;
      }
    }
    return 'unknown';
  }
}
