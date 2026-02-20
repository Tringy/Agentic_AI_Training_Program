/**
 * Reusable TypeScript Agent Template - Tool Definitions
 * =====================================================
 *
 * Base class and example tools for agent capabilities.
 */

import type { ParameterSchema, ToolDefinition } from './types.js';

// ============================================================================
// Tool Interface
// ============================================================================

/**
 * Abstract base class for agent tools.
 * Extend this class to create custom tools.
 */
export abstract class Tool {
  /**
   * Tool name for LLM reference
   */
  abstract get name(): string;

  /**
   * Description of what the tool does
   */
  abstract get description(): string;

  /**
   * JSON schema for tool parameters
   */
  abstract get parameters(): ParameterSchema;

  /**
   * Execute the tool and return result
   */
  abstract execute(args: Record<string, unknown>): Promise<string>;

  /**
   * Convert tool to definition format for LLM
   */
  toDefinition(): ToolDefinition {
    return {
      name: this.name,
      description: this.description,
      parameters: this.parameters,
    };
  }
}

// ============================================================================
// Example Tools
// ============================================================================

/**
 * Example: Simple calculator tool
 */
export class CalculatorTool extends Tool {
  get name(): string {
    return 'calculator';
  }

  get description(): string {
    return 'Perform basic arithmetic operations. Supports +, -, *, /, and parentheses.';
  }

  get parameters(): ParameterSchema {
    return {
      type: 'object',
      properties: {
        expression: {
          type: 'string',
          description: "Mathematical expression to evaluate (e.g., '2 + 2', '(10 * 5) / 2')",
        },
      },
      required: ['expression'],
    };
  }

  async execute(args: Record<string, unknown>): Promise<string> {
    const expression = args.expression as string;

    try {
      // Safe evaluation: only allow numbers and basic operators
      const sanitized = expression.replace(/[^0-9+\-*/.() ]/g, '');
      if (sanitized !== expression) {
        return 'Error: Expression contains invalid characters';
      }

      // Use Function constructor for safer evaluation than eval
      const result = new Function(`return ${sanitized}`)();
      return String(result);
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }
}

/**
 * Example: File reader tool (simulated)
 */
export class FileReaderTool extends Tool {
  get name(): string {
    return 'read_file';
  }

  get description(): string {
    return 'Read the contents of a file given its path.';
  }

  get parameters(): ParameterSchema {
    return {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the file to read',
        },
      },
      required: ['path'],
    };
  }

  async execute(args: Record<string, unknown>): Promise<string> {
    const path = args.path as string;

    try {
      // Dynamic import for Node.js fs module
      const fs = await import('node:fs/promises');
      const content = await fs.readFile(path, 'utf-8');
      return content;
    } catch (error) {
      return `Error reading file: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }
}

/**
 * Example: Shell command tool (use with caution!)
 */
export class ShellTool extends Tool {
  private allowedCommands: string[];

  constructor(allowedCommands: string[] = ['ls', 'pwd', 'cat', 'head', 'tail', 'wc']) {
    super();
    this.allowedCommands = allowedCommands;
  }

  get name(): string {
    return 'shell';
  }

  get description(): string {
    return `Execute shell commands. Allowed commands: ${this.allowedCommands.join(', ')}`;
  }

  get parameters(): ParameterSchema {
    return {
      type: 'object',
      properties: {
        command: {
          type: 'string',
          description: 'Shell command to execute',
        },
      },
      required: ['command'],
    };
  }

  async execute(args: Record<string, unknown>): Promise<string> {
    const command = args.command as string;
    const baseCommand = command.split(' ')[0];

    if (!this.allowedCommands.includes(baseCommand)) {
      return `Error: Command '${baseCommand}' is not allowed. Allowed: ${this.allowedCommands.join(', ')}`;
    }

    try {
      const { exec } = await import('node:child_process');
      const { promisify } = await import('node:util');
      const execAsync = promisify(exec);

      const { stdout, stderr } = await execAsync(command);
      return stderr ? `Error: ${stderr}` : stdout;
    } catch (error) {
      return `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }
}
