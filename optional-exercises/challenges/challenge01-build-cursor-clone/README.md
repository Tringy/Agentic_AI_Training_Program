# Challenge 01: Build a Cursor Clone

## Description

Build your own simplified version of Cursor editor - an IDE with integrated AI assistance. This is a complete project that integrates multiple advanced concepts.

**Difficulty**: Expert
**Estimated time**: 30-40 hours
**Stack**: Electron + React + Monaco Editor + LLM APIs

---

## Challenge Objectives

Upon completing this challenge, you will have built:

- ✅ Functional code editor (based on Monaco)
- ✅ AI chat sidebar
- ✅ Context-aware code completion
- ✅ Inline AI suggestions
- ✅ File tree navigation with semantic search
- ✅ Multi-file context management
- ✅ Diff viewer for AI changes

---

## Features Requeridas (MVP)

### 1. Code Editor Base
- Monaco Editor integration
- Syntax highlighting para 10+ lenguajes
- File tree navigation
- Multiple tabs
- Search & replace

### 2. AI Chat Interface
```typescript
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  context?: CodeContext[];
}

interface CodeContext {
  file: string;
  startLine: number;
  endLine: number;
  code: string;
}
```

### 3. Context-Aware Completion
```typescript
class AICompletionProvider {
  async provideCompletions(
    model: editor.ITextModel,
    position: Position
  ): Promise<CompletionList> {
    // 1. Get surrounding code context
    const context = this.getContext(model, position);

    // 2. Get relevant files
    const relatedFiles = await this.findRelatedFiles(context);

    // 3. Call LLM with full context
    const completion = await this.llm.complete({
      currentFile: model.getValue(),
      position,
      relatedFiles,
      recentChanges: this.getRecentChanges()
    });

    return this.parseCompletions(completion);
  }
}
```

### 4. Inline AI Edits
```typescript
// User selects code and presses Cmd+K
async function inlineEdit(selection: string, instruction: string) {
  const prompt = `
Current code:
${selection}

Instruction: ${instruction}

Provide only the modified code.
`;

  const edited = await llm.complete(prompt);

  // Show diff preview
  showDiff(selection, edited);

  // User accepts/rejects
  await waitForUserConfirmation();
}
```

### 5. Semantic File Search
```typescript
class SemanticFileSearch {
  async search(query: string): Promise<SearchResult[]> {
    // 1. Embed query
    const queryVector = await this.embedModel.embed(query);

    // 2. Search indexed files
    const results = await this.vectorDB.search(queryVector);

    // 3. Rank by relevance
    return this.rankResults(results);
  }

  // Index files on load
  async indexProject(directory: string) {
    const files = await this.scanFiles(directory);

    for (const file of files) {
      const chunks = this.chunkCode(file);
      const vectors = await this.embedModel.embedBatch(chunks);

      await this.vectorDB.upsert(file.path, vectors);
    }
  }
}
```

### 6. Multi-File Context

```typescript
class ContextManager {
  private maxContextTokens = 8000;

  async buildContext(
    currentFile: string,
    cursorPosition: Position
  ): Promise<string> {
    const context = [];
    let tokenCount = 0;

    // 1. Current file content (highest priority)
    const currentContent = this.getCurrentFileContext(
      currentFile,
      cursorPosition
    );
    context.push(currentContent);
    tokenCount += this.countTokens(currentContent);

    // 2. Open files
    const openFiles = this.getOpenFiles();
    for (const file of openFiles) {
      if (tokenCount >= this.maxContextTokens) break;

      const content = file.getContent();
      context.push(content);
      tokenCount += this.countTokens(content);
    }

    // 3. Related files (imports, etc)
    const relatedFiles = await this.findRelatedFiles(currentFile);
    for (const file of relatedFiles) {
      if (tokenCount >= this.maxContextTokens) break;

      const content = await this.readFile(file);
      context.push(content);
      tokenCount += this.countTokens(content);
    }

    return context.join('\n\n---\n\n');
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           Electron Main Process              │
│  - File system access                        │
│  - Window management                         │
│  - IPC with renderer                         │
└─────────────────────────────────────────────┘
                     │
                     │ IPC
                     ▼
┌─────────────────────────────────────────────┐
│         Electron Renderer Process            │
│                                              │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │   Monaco    │  │    AI Chat Panel     │  │
│  │   Editor    │  │  - Message history   │  │
│  │             │  │  - Code context      │  │
│  └─────────────┘  └──────────────────────┘  │
│                                              │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ File Tree   │  │  Completion Provider │  │
│  │             │  │  - Inline suggestions│  │
│  └─────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────┘
                     │
                     │ API calls
                     ▼
┌─────────────────────────────────────────────┐
│              Backend Services                │
│  - LLM API (Claude/GPT)                     │
│  - Vector DB (for semantic search)          │
│  - Embedding model                          │
└─────────────────────────────────────────────┘
```

---

## Implementation Guide

### Phase 1: Editor Foundation (8-10h)

**Tasks**:
1. Setup Electron + React project
2. Integrate Monaco Editor
3. Implement file tree
4. Add basic file operations (open/save/close)
5. Multiple tab support

**Validation**:
- Can open and edit files
- Syntax highlighting works
- File tree navigable

### Phase 2: AI Chat (8-10h)

**Tasks**:
1. Create chat UI component
2. Implement message state management
3. Integrate LLM API
4. Add code block rendering
5. Context selection mechanism

**Validation**:
- Chat interface functional
- Can send/receive messages
- Code blocks properly formatted

### Phase 3: Code Completion (10-12h)

**Tasks**:
1. Implement completion provider
2. Context extraction logic
3. LLM integration for completions
4. Debouncing and caching
5. UI for inline suggestions

**Validation**:
- Completions appear on keystroke
- Context-aware suggestions
- Performance acceptable (< 500ms)

### Phase 4: Advanced Features (8-10h)

**Tasks**:
1. Semantic file search
2. Diff viewer
3. Inline edit mode (Cmd+K)
4. Related file detection
5. Settings panel

---

## Technical Challenges

### 1. Performance Optimization

```typescript
// Debounce completion requests
const debouncedComplete = debounce(
  async (context) => {
    return await llm.complete(context);
  },
  300
);

// Cache completions
const completionCache = new LRUCache<string, Completion>(100);

async function getCompletion(context: string) {
  const cacheKey = hash(context);

  if (completionCache.has(cacheKey)) {
    return completionCache.get(cacheKey);
  }

  const completion = await debouncedComplete(context);
  completionCache.set(cacheKey, completion);

  return completion;
}
```

### 2. Token Management

```typescript
class TokenManager {
  private maxTokens = 8000;

  optimizeContext(context: CodeContext[]): CodeContext[] {
    // Prioritize by relevance
    const sorted = this.sortByRelevance(context);

    let totalTokens = 0;
    const optimized = [];

    for (const item of sorted) {
      const tokens = this.countTokens(item.code);

      if (totalTokens + tokens > this.maxTokens) {
        // Try to include partial content
        const remaining = this.maxTokens - totalTokens;
        if (remaining > 100) {
          optimized.push(this.truncate(item, remaining));
        }
        break;
      }

      optimized.push(item);
      totalTokens += tokens;
    }

    return optimized;
  }
}
```

### 3. Streaming Responses

```typescript
async function streamCompletion(prompt: string) {
  const stream = await llm.streamComplete(prompt);

  let buffer = '';

  for await (const chunk of stream) {
    buffer += chunk;

    // Update UI incrementally
    updateCompletionUI(buffer);

    // Check if user stopped typing
    if (userContinuedTyping()) {
      stream.cancel();
      break;
    }
  }

  return buffer;
}
```

---

## Testing Strategy

### Unit Tests
```typescript
describe('ContextManager', () => {
  it('should prioritize current file', () => {
    const context = contextManager.buildContext('file.ts', position);
    expect(context[0]).toContain('file.ts');
  });

  it('should respect token limits', () => {
    const context = contextManager.buildContext('large-file.ts', position);
    const tokens = countTokens(context.join(''));
    expect(tokens).toBeLessThan(8000);
  });
});
```

### Integration Tests
```typescript
describe('AI Completion', () => {
  it('should provide completions', async () => {
    const completions = await completionProvider.provideCompletions(
      model,
      new Position(10, 5)
    );

    expect(completions.length).toBeGreaterThan(0);
  });
});
```

### E2E Tests
```typescript
describe('Full workflow', () => {
  it('should complete code from chat instruction', async () => {
    // 1. Open file
    await app.openFile('src/index.ts');

    // 2. Send chat message
    await app.chat.send('Add a function to calculate fibonacci');

    // 3. Wait for response
    const response = await app.chat.waitForResponse();

    // 4. Apply code
    await app.editor.insertCode(response.code);

    // 5. Verify
    expect(app.editor.getText()).toContain('fibonacci');
  });
});
```

---

## Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Functionality** | 40% | All MVP features working |
| **UX/UI** | 20% | Clean, intuitive interface |
| **Performance** | 15% | Responsive, < 500ms completions |
| **Code Quality** | 15% | Well-structured, tested |
| **Innovation** | 10% | Unique features, polish |

**Passing score**: 75%

---

## Bonus Features (Optional)

- 🔥 Terminal integration
- 🔥 Git integration (blame, diff)
- 🔥 Collaborative editing
- 🔥 Plugin system
- 🔥 Custom keybindings
- 🔥 Workspace management
- 🔥 AI refactoring suggestions
- 🔥 Code explanation tooltips

---

## Submission Requirements

1. **GitHub Repository**
   - Clean README with setup instructions
   - Screenshots/GIFs of features
   - Architecture documentation

2. **Demo Video** (5-10 min)
   - Walkthrough of features
   - Code explanation
   - Challenges faced

3. **Deployment**
   - Build for macOS/Windows/Linux
   - Or: Web version deployed

4. **Documentation**
   - API documentation
   - User guide
   - Developer guide for contributors

---

## Resources

### Technical
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [Electron Documentation](https://www.electronjs.org/docs)
- [LSP Protocol](https://microsoft.github.io/language-server-protocol/)

### Inspiration
- [Cursor IDE](https://cursor.sh/)
- [GitHub Copilot](https://github.com/features/copilot)
- [VS Code](https://code.visualstudio.com/)

---

**¡Construye el futuro de los IDEs! 🚀**
