# Capstone Option B: Legacy Code Documenter

## Project Overview

Build an AI-powered CLI tool that automatically generates comprehensive documentation for undocumented or poorly documented code.

**Complexity**: Medium
**Estimated Time**: 2-2.5 hours

---

## Requirements

### Must Have (Core - 70%)
- [ ] CLI command accepting file or directory path
- [ ] Parse code to identify functions, classes, and modules
- [ ] Generate inline docstrings for Python (Google/NumPy style)
- [ ] Generate JSDoc comments for JavaScript/TypeScript
- [ ] Generate markdown API documentation file
- [ ] Handle at least 2 programming languages (Python and JavaScript)

### Should Have (Polish - 20%)
- [ ] Generate project-level README.md with overview
- [ ] Include usage examples in generated documentation
- [ ] Error handling for unparseable or binary files
- [ ] Progress indicators for batch processing

### Nice to Have (Bonus - 10%)
- [ ] Generate TypeDoc/Sphinx-ready documentation
- [ ] Detect and preserve existing documentation
- [ ] Interactive mode to review before writing changes
- [ ] Support for custom documentation templates

---

## CLI Specification

### Commands

```bash
# Generate inline documentation
python main.py --input ./src/utils.py --format inline --output ./src/utils.py

# Generate markdown API docs
python main.py --input ./src --format markdown --output ./docs/api.md

# Generate README
python main.py --input ./my_project --format readme --output ./my_project/README.md

# Multiple formats at once
python main.py --input ./src --format inline,markdown,readme
```

### Arguments

- `--input` (required): File or directory path to document
- `--format` (required): Output format (inline, markdown, readme)
- `--output` (optional): Output path (default: same as input for inline, ./docs for others)
- `--language` (optional): Force language detection (python, javascript, typescript)

### Expected Output

**Inline format** - Adds docstrings directly to code:
```python
# Before
def calculate_total(items):
    return sum(item.price for item in items)

# After
def calculate_total(items):
    """Calculate the total price of all items.

    Args:
        items: List of items with price attributes.

    Returns:
        float: Sum of all item prices.
    """
    return sum(item.price for item in items)
```

**Markdown format** - Generates API reference:
```markdown
# API Documentation

## Functions

### calculate_total(items)

Calculate the total price of all items.

**Parameters:**
- `items` (List): List of items with price attributes

**Returns:**
- `float`: Sum of all item prices

**Example:**
```python
items = [Item(price=10), Item(price=20)]
total = calculate_total(items)  # Returns 30
```
```

**README format** - Generates project overview:
```markdown
# Project Name

## Overview
Brief description of what the project does based on code analysis.

## Features
- Feature 1 (extracted from code)
- Feature 2

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Example usage based on main entry points found in code.

## API Reference
See [api.md](docs/api.md) for complete API documentation.
```

---

## Starter Code

### main.py
```python
"""Legacy Code Documenter - Capstone Option B

CLI tool that generates comprehensive documentation for code.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from documenter import CodeDocumenter
from llm_client import LLMClient

def main():
    """Main entry point for the documenter CLI."""
    parser = argparse.ArgumentParser(
        description="Generate documentation for undocumented code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input ./src/utils.py --format inline
  python main.py --input ./src --format markdown --output ./docs/api.md
  python main.py --input ./project --format readme
        """
    )

    parser.add_argument(
        "--input",
        required=True,
        help="File or directory path to document"
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=["inline", "markdown", "readme"],
        help="Output format: inline (docstrings), markdown (API docs), readme (project overview)"
    )
    parser.add_argument(
        "--output",
        help="Output path (default: same as input for inline, ./docs for others)"
    )
    parser.add_argument(
        "--language",
        choices=["python", "javascript", "typescript"],
        help="Force language detection (auto-detect if not specified)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Path not found: {args.input}")
        sys.exit(1)

    # Initialize
    llm = LLMClient()
    documenter = CodeDocumenter(llm, verbose=args.verbose)

    # TODO: Implement documentation generation based on format
    try:
        if args.format == "inline":
            result = documenter.generate_inline_docs(
                input_path,
                output_path=args.output,
                language=args.language
            )
            print(f"✅ Generated inline documentation: {result}")

        elif args.format == "markdown":
            output_path = args.output or "./docs/api.md"
            result = documenter.generate_markdown_docs(
                input_path,
                output_path=output_path,
                language=args.language
            )
            print(f"✅ Generated markdown documentation: {result}")

        elif args.format == "readme":
            output_path = args.output or input_path / "README.md"
            result = documenter.generate_readme(
                input_path,
                output_path=output_path
            )
            print(f"✅ Generated README: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### documenter.py
```python
"""Code documentation generator using LLM."""
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from parser import CodeParser, CodeElement
from prompts import (
    DOCSTRING_SYSTEM_PROMPT,
    DOCSTRING_USER_PROMPT,
    MARKDOWN_SYSTEM_PROMPT,
    README_SYSTEM_PROMPT
)

class CodeDocumenter:
    """Agent that generates documentation in multiple formats."""

    def __init__(self, llm_client, verbose: bool = False):
        """Initialize documenter.

        Args:
            llm_client: LLM client for generating documentation
            verbose: Show detailed progress
        """
        self.llm = llm_client
        self.parser = CodeParser()
        self.verbose = verbose

    def generate_inline_docs(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        language: Optional[str] = None
    ) -> str:
        """Generate inline docstrings/JSDoc comments.

        Args:
            input_path: File or directory to document
            output_path: Where to write output (default: overwrite input)
            language: Force language detection

        Returns:
            Path to output file(s)
        """
        # TODO: Implement inline documentation generation
        # Steps:
        # 1. Parse file to extract functions/classes
        # 2. For each element, generate docstring using LLM
        # 3. Insert docstrings into code at correct positions
        # 4. Write updated code to output path

        if self.verbose:
            print(f"Parsing {input_path}...")

        # Parse code
        elements = self.parser.parse_file(input_path, language)

        if self.verbose:
            print(f"Found {len(elements)} code elements")

        # Generate docs for each element
        documented_code = input_path.read_text()

        for element in elements:
            if self.verbose:
                print(f"  Generating docs for {element.name}...")

            docstring = self._generate_docstring(element, language or element.language)
            # TODO: Insert docstring into code at correct position

        # Write output
        output = output_path or input_path
        Path(output).write_text(documented_code)

        return str(output)

    def generate_markdown_docs(
        self,
        input_path: Path,
        output_path: Path,
        language: Optional[str] = None
    ) -> str:
        """Generate markdown API documentation.

        Args:
            input_path: File or directory to document
            output_path: Where to write markdown file
            language: Force language detection

        Returns:
            Path to markdown file
        """
        # TODO: Implement markdown generation
        # Steps:
        # 1. Parse all files in directory
        # 2. Group by module/class
        # 3. Generate markdown for each
        # 4. Format as complete API reference

        if self.verbose:
            print(f"Generating markdown docs for {input_path}...")

        if input_path.is_file():
            files = [input_path]
        else:
            # Find all code files
            files = list(input_path.rglob("*.py")) + list(input_path.rglob("*.js"))

        all_elements = []
        for file in files:
            elements = self.parser.parse_file(file, language)
            all_elements.extend(elements)

        # Generate markdown
        markdown = self._build_markdown_docs(all_elements)

        # Write output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(markdown)

        if self.verbose:
            print(f"Generated {len(all_elements)} documented items")

        return str(output_path)

    def generate_readme(
        self,
        input_path: Path,
        output_path: Path
    ) -> str:
        """Generate project-level README.md.

        Args:
            input_path: Project directory to analyze
            output_path: Where to write README

        Returns:
            Path to README file
        """
        # TODO: Implement README generation
        # Steps:
        # 1. Analyze project structure
        # 2. Identify main entry points
        # 3. Extract key features from code
        # 4. Generate comprehensive README using LLM

        if self.verbose:
            print(f"Analyzing project structure: {input_path}...")

        # Analyze project
        project_info = self._analyze_project(input_path)

        # Generate README
        readme_content = self._generate_readme_content(project_info)

        # Write output
        Path(output_path).write_text(readme_content)

        if self.verbose:
            print(f"Generated README with {len(readme_content)} characters")

        return str(output_path)

    def _generate_docstring(self, element: CodeElement, language: str) -> str:
        """Generate docstring for a code element using LLM."""
        # Format user prompt
        user_prompt = DOCSTRING_USER_PROMPT.format(
            style="Google" if language == "python" else "JSDoc",
            language=language,
            element_type=element.type,
            name=element.name,
            signature=element.signature,
            code_context=element.code_context
        )

        # Call LLM
        response = self.llm.chat(DOCSTRING_SYSTEM_PROMPT, user_prompt)

        return response.strip()

    def _build_markdown_docs(self, elements: List[CodeElement]) -> str:
        """Build markdown documentation from code elements."""
        # TODO: Format elements into markdown
        # Group by file/module, create TOC, format each element

        prompt = f"""Generate a comprehensive API reference in markdown format for these code elements:

{self._format_elements_for_prompt(elements)}

Include:
1. Table of contents
2. Module/class groupings
3. Function signatures with parameters
4. Return values
5. Usage examples where helpful
"""

        response = self.llm.chat(MARKDOWN_SYSTEM_PROMPT, prompt)
        return response

    def _analyze_project(self, project_path: Path) -> Dict:
        """Analyze project structure and extract key information."""
        # TODO: Scan directory, identify key files, extract structure

        return {
            "name": project_path.name,
            "files": [],
            "entry_points": [],
            "dependencies": []
        }

    def _generate_readme_content(self, project_info: Dict) -> str:
        """Generate README content using LLM."""
        prompt = f"""Generate a comprehensive README.md for this project:

Project: {project_info['name']}
Files analyzed: {len(project_info['files'])}

Include:
1. Project title and description
2. Key features
3. Installation instructions
4. Usage examples
5. Project structure overview
6. API reference link
"""

        response = self.llm.chat(README_SYSTEM_PROMPT, prompt)
        return response

    def _format_elements_for_prompt(self, elements: List[CodeElement]) -> str:
        """Format code elements for LLM prompt."""
        parts = []
        for elem in elements[:20]:  # Limit to avoid token overflow
            parts.append(f"- {elem.type} `{elem.name}`: {elem.signature}")
        return "\n".join(parts)
```

### parser.py
```python
"""Code parsing utilities for documentation generation."""
import ast
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class CodeElement:
    """Represents a code element (function, class, method, module)."""
    name: str
    type: str  # "function", "class", "method", "module"
    signature: str
    line_number: int
    language: str
    existing_doc: Optional[str]
    code_context: str  # Surrounding code for context

class CodeParser:
    """Parse code files to extract documentable elements."""

    def parse_file(
        self,
        filepath: Path,
        language: Optional[str] = None
    ) -> List[CodeElement]:
        """Parse file and extract code elements.

        Args:
            filepath: Path to code file
            language: Force language (auto-detect if None)

        Returns:
            List of code elements found in file
        """
        # Detect language
        if language is None:
            language = self._detect_language(filepath)

        # Read file
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return []

        # Parse based on language
        if language == "python":
            return self._parse_python(content, str(filepath))
        elif language in ["javascript", "typescript"]:
            return self._parse_javascript(content, str(filepath))
        else:
            print(f"Warning: Unsupported language {language}")
            return []

    def _detect_language(self, filepath: Path) -> str:
        """Detect programming language from file extension."""
        suffix = filepath.suffix.lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript"
        }

        return language_map.get(suffix, "unknown")

    def _parse_python(self, content: str, filepath: str) -> List[CodeElement]:
        """Parse Python file using AST.

        Args:
            content: File content
            filepath: File path (for error messages)

        Returns:
            List of functions and classes
        """
        elements = []

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Warning: Syntax error in {filepath}: {e}")
            return []

        # TODO: Implement AST traversal
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract function info
                elements.append(CodeElement(
                    name=node.name,
                    type="function",
                    signature=self._get_function_signature(node),
                    line_number=node.lineno,
                    language="python",
                    existing_doc=ast.get_docstring(node),
                    code_context=self._get_context(content, node.lineno)
                ))

            elif isinstance(node, ast.ClassDef):
                # Extract class info
                elements.append(CodeElement(
                    name=node.name,
                    type="class",
                    signature=f"class {node.name}",
                    line_number=node.lineno,
                    language="python",
                    existing_doc=ast.get_docstring(node),
                    code_context=self._get_context(content, node.lineno)
                ))

        return elements

    def _parse_javascript(self, content: str, filepath: str) -> List[CodeElement]:
        """Parse JavaScript/TypeScript using regex patterns.

        Args:
            content: File content
            filepath: File path

        Returns:
            List of functions and classes
        """
        elements = []

        # TODO: Implement JavaScript parsing
        # Use regex to find function declarations, class definitions

        # Function pattern: function name(...) or const name = (...) =>
        function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)'

        # Class pattern: class Name
        class_pattern = r'class\s+(\w+)'

        for match in re.finditer(function_pattern, content):
            name = match.group(1) or match.group(2)
            line_num = content[:match.start()].count('\n') + 1

            elements.append(CodeElement(
                name=name,
                type="function",
                signature=match.group(0),
                line_number=line_num,
                language="javascript",
                existing_doc=None,
                code_context=self._get_context(content, line_num)
            ))

        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            elements.append(CodeElement(
                name=name,
                type="class",
                signature=match.group(0),
                line_number=line_num,
                language="javascript",
                existing_doc=None,
                code_context=self._get_context(content, line_num)
            ))

        return elements

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature from AST node."""
        # TODO: Build signature string with parameters
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        return f"def {node.name}({', '.join(params)})"

    def _get_context(self, content: str, line_number: int, context_lines: int = 5) -> str:
        """Get surrounding code context for better documentation.

        Args:
            content: Full file content
            line_number: Line number of code element
            context_lines: Number of lines before/after to include

        Returns:
            Code context string
        """
        lines = content.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)

        context = '\n'.join(lines[start:end])
        return context
```

### prompts.py
```python
"""Prompts for documentation generation."""

DOCSTRING_SYSTEM_PROMPT = """You are an expert technical writer specializing in code documentation.

Your role:
1. Generate clear, concise documentation that explains what code does
2. Follow language-specific documentation conventions
3. Include parameter descriptions with types
4. Document return values
5. Add usage examples for complex functionality

Guidelines:
- Describe what the code does, not how it does it (avoid implementation details)
- Be concise but comprehensive
- Use proper formatting (Google style for Python, JSDoc for JavaScript)
- Focus on helping developers understand how to use the code

Always return ONLY the documentation text without code or markdown formatting."""

DOCSTRING_USER_PROMPT = """Generate a {style} docstring for this {language} {element_type}:

Name: {name}
Signature: {signature}

Code context:
```{language}
{code_context}
```

{existing_doc_note}

Return only the docstring text (no code, no markdown, no explanations)."""

MARKDOWN_SYSTEM_PROMPT = """You are a documentation expert generating API reference documentation in markdown format.

Create clear, well-structured API documentation that includes:
1. Hierarchical organization (modules → classes → functions)
2. Table of contents with links
3. Clear function signatures with type information
4. Parameter descriptions
5. Return value descriptions
6. Usage examples with code
7. Notes about exceptions or edge cases

Format as clean markdown suitable for GitHub, documentation sites, or static site generators."""

README_SYSTEM_PROMPT = """You are a technical writer creating comprehensive project README files.

Generate a professional README.md that includes:
1. Project title and concise description (1-2 sentences)
2. Key features list (bullet points)
3. Installation/setup instructions
4. Basic usage examples with code
5. Project structure overview
6. API reference (link to detailed docs)
7. Contributing guidelines (if applicable)
8. License information (if identifiable)

Write in clear, professional markdown. Make it easy for developers to quickly understand and start using the project."""
```

### llm_client.py
```python
"""LLM client abstraction."""
import os
from anthropic import Anthropic

class LLMClient:
    """Simple LLM client for documentation generation."""

    def __init__(self):
        """Initialize LLM client with API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Set it in .env or export it."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def chat(self, system: str, user: str) -> str:
        """Send messages to LLM and get response.

        Args:
            system: System prompt
            user: User message

        Returns:
            LLM response text
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}]
        )

        return response.content[0].text
```

### requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
anthropic==0.18.0
python-dotenv==1.0.0
```

---

## Implementation Steps

1. **Setup** (10 min)
   - Copy starter files to your working directory
   - Install dependencies: `pip install -r requirements.txt`
   - Set ANTHROPIC_API_KEY in .env file
   - Test LLM connection: `python -c "from llm_client import LLMClient; c = LLMClient(); print('OK')"`

2. **Code Parser - Python** (30 min)
   - Complete `_parse_python()` method in parser.py
   - Use AST to extract all functions and classes
   - Extract function signatures with parameters and return types
   - Test on sample Python file
   - Verify `CodeElement` objects are created correctly

3. **Code Parser - JavaScript** (20 min)
   - Complete `_parse_javascript()` method in parser.py
   - Use regex to find function and class declarations
   - Handle arrow functions and class methods
   - Test on sample JavaScript file

4. **Inline Documentation** (40 min)
   - Complete `generate_inline_docs()` in documenter.py
   - Implement docstring insertion logic at correct line positions
   - Handle indentation correctly
   - Test with undocumented Python and JavaScript files
   - Verify docstrings are properly formatted

5. **Markdown Generation** (30 min)
   - Complete `generate_markdown_docs()` in documenter.py
   - Implement `_build_markdown_docs()` to format elements
   - Create table of contents
   - Group by module/file
   - Test output is valid markdown

6. **README Generation** (20 min)
   - Complete `generate_readme()` in documenter.py
   - Implement `_analyze_project()` to scan directory structure
   - Complete `_generate_readme_content()` with LLM call
   - Test on sample project directory

7. **CLI Polish & Testing** (20 min)
   - Test all CLI arguments work correctly
   - Add progress indicators for verbose mode
   - Test error handling (missing files, parse errors)
   - Verify all three formats work end-to-end

---

## Testing

### Test inline docstring generation

```bash
# Create test file
cat > test_undocumented.py << 'EOF'
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    def add(self, a, b):
        return a + b
EOF

# Generate inline docs
python main.py --input test_undocumented.py --format inline --verbose

# Expected: File now has Google-style docstrings for function and class
```

### Test markdown API documentation

```bash
# Generate markdown docs for directory
python main.py --input ./test_code --format markdown --output ./docs/api.md

# Expected: docs/api.md contains:
# - Table of contents
# - Function documentation with parameters
# - Class documentation
# - Usage examples
```

### Test README generation

```bash
# Generate README for project
python main.py --input ./my_project --format readme

# Expected: my_project/README.md contains:
# - Project title and description
# - Features list
# - Installation instructions
# - Usage examples
# - Project structure
```

### Test error handling

```bash
# Test with nonexistent file
python main.py --input ./nonexistent.py --format inline

# Expected: Clear error message "Error: Path not found"

# Test with binary file
python main.py --input ./image.png --format inline

# Expected: Graceful handling or skip with warning
```

---

## Evaluation Checklist

- [ ] CLI command accepts file/directory path
- [ ] Parses Python code successfully
- [ ] Parses JavaScript code successfully
- [ ] Generates Google-style docstrings for Python
- [ ] Generates JSDoc comments for JavaScript
- [ ] Generates markdown API documentation
- [ ] Generates project README
- [ ] Error handling works correctly
- [ ] Progress indicators show status
- [ ] Tool is ready for demo

---

## TypeScript Version (Optional)

For students who prefer TypeScript, a similar implementation using:
- `commander` for CLI parsing
- `@babel/parser` for JavaScript AST parsing
- `ts-morph` for TypeScript AST parsing
- Same prompts and LLM client patterns

See `typescript/` directory for equivalent implementation.

---

## Extension Ideas

If you finish early:
- Add support for more languages (Go, Rust, Java)
- Implement diff mode (only document changed functions)
- Add configuration file support (.documenterrc)
- Generate changelog from git history
- Create HTML output format with syntax highlighting
