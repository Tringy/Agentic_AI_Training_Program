"""
LLM Prompts for Code Review

System prompts, user prompts, and formatting templates for AI-powered code review.
"""
from typing import List, Dict, Any


SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of:
- Security vulnerabilities (SQL injection, XSS, CSRF, etc.)
- Code quality and maintainability
- Best practices across multiple languages
- Performance optimization
- Testing strategies
- Documentation standards

Your role is to:
1. Identify security vulnerabilities with severity levels (High, Medium, Low)
2. Detect code quality issues (complexity, duplication, naming)
3. Suggest best practice improvements
4. Provide constructive, actionable feedback
5. Highlight positive aspects of the code

Be thorough but concise. Focus on issues that matter. Always provide:
- Specific line references
- Clear explanations of the problem
- Concrete recommendations with code examples
- Severity classification

Format your response as structured JSON for easy parsing."""


def create_review_prompt(
    pr_title: str,
    pr_description: str,
    files_changed: List[Dict[str, Any]],
    repository_context: str = ""
) -> str:
    """
    Create a comprehensive review prompt for the LLM.

    Args:
        pr_title: Pull request title
        pr_description: Pull request description
        files_changed: List of changed files with diffs
        repository_context: Optional repository context

    Returns:
        Formatted prompt string
    """
    files_summary = "\n\n".join([
        f"### File: {file['filename']}\n"
        f"Status: {file['status']}\n"
        f"Changes: +{file['additions']} -{file['deletions']}\n"
        f"```diff\n{file['patch'][:2000]}{'...' if len(file.get('patch', '')) > 2000 else ''}\n```"
        for file in files_changed[:10]  # Limit to first 10 files
    ])

    prompt = f"""Please review the following pull request:

## Pull Request
**Title:** {pr_title}
**Description:** {pr_description or 'No description provided'}

{f"## Repository Context\\n{repository_context}\\n" if repository_context else ""}

## Files Changed ({len(files_changed)} files)
{files_summary}

## Review Instructions
Provide a comprehensive code review covering:

1. **Security Issues** - Identify vulnerabilities with severity (High/Medium/Low)
2. **Code Quality** - Complexity, duplication, naming, structure
3. **Best Practices** - Language-specific conventions and patterns
4. **Performance** - Potential bottlenecks or inefficiencies
5. **Testing** - Test coverage and quality
6. **Documentation** - Comments and documentation quality
7. **Positive Feedback** - What was done well

## Output Format
Return your review as a JSON object with this structure:
{{
  "summary": "Brief overview of the review",
  "security_issues": [
    {{
      "severity": "High|Medium|Low",
      "file": "filename",
      "line": 123,
      "issue": "Description of the issue",
      "recommendation": "How to fix it",
      "code_example": "Example fix (if applicable)"
    }}
  ],
  "quality_issues": [
    {{
      "severity": "High|Medium|Low",
      "file": "filename",
      "line": 123,
      "issue": "Description",
      "recommendation": "How to improve"
    }}
  ],
  "best_practices": [
    {{
      "file": "filename",
      "line": 123,
      "suggestion": "Best practice recommendation"
    }}
  ],
  "positive_feedback": [
    "List of things done well"
  ],
  "overall_assessment": "Overall quality assessment",
  "confidence_score": 0.0-1.0
}}"""

    return prompt


def format_review_comment(review_data: Dict[str, Any]) -> str:
    """
    Format the review data into a GitHub-friendly markdown comment.

    Args:
        review_data: Parsed review data from LLM

    Returns:
        Formatted markdown comment
    """
    sections = []

    # Header
    sections.append("## AI Code Review\n")
    sections.append(f"**Summary:** {review_data.get('summary', 'No summary provided')}\n")

    # Security Issues
    security = review_data.get('security_issues', [])
    if security:
        high_count = len([s for s in security if s.get('severity') == 'High'])
        medium_count = len([s for s in security if s.get('severity') == 'Medium'])
        low_count = len([s for s in security if s.get('severity') == 'Low'])

        sections.append(f"\n### Security Issues ({high_count} High, {medium_count} Medium, {low_count} Low)\n")

        for issue in security:
            severity_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(issue.get('severity', 'Low'), "🔵")
            sections.append(f"\n{severity_emoji} **{issue.get('severity')} Priority** - {issue.get('file')}:{issue.get('line', '?')}")
            sections.append(f"\n**Issue:** {issue.get('issue')}")
            sections.append(f"\n**Recommendation:** {issue.get('recommendation')}")

            if issue.get('code_example'):
                sections.append(f"\n```{get_file_extension(issue.get('file', ''))}")
                sections.append(f"{issue.get('code_example')}")
                sections.append("```")

    # Quality Issues
    quality = review_data.get('quality_issues', [])
    if quality:
        sections.append(f"\n### Code Quality Issues ({len(quality)})\n")
        for issue in quality[:5]:  # Limit to top 5
            sections.append(f"\n- **{issue.get('file')}:{issue.get('line', '?')}** - {issue.get('issue')}")
            sections.append(f"  - Recommendation: {issue.get('recommendation')}")

    # Best Practices
    best_practices = review_data.get('best_practices', [])
    if best_practices:
        sections.append(f"\n### Best Practices Suggestions ({len(best_practices)})\n")
        for suggestion in best_practices[:5]:  # Limit to top 5
            sections.append(f"\n- **{suggestion.get('file')}:{suggestion.get('line', '?')}** - {suggestion.get('suggestion')}")

    # Positive Feedback
    positive = review_data.get('positive_feedback', [])
    if positive:
        sections.append("\n### Positive Feedback\n")
        for feedback in positive[:5]:
            sections.append(f"- ✅ {feedback}")

    # Overall Assessment
    sections.append(f"\n### Overall Assessment\n")
    sections.append(review_data.get('overall_assessment', 'No overall assessment provided'))

    # Confidence Score
    confidence = review_data.get('confidence_score', 0.0)
    sections.append(f"\n**Confidence Score:** {confidence:.2f}/1.0")

    # Footer
    sections.append("\n---")
    sections.append("\n🤖 *Generated by AI Code Review Agent*")

    return "\n".join(sections)


def get_file_extension(filename: str) -> str:
    """Get file extension for syntax highlighting."""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
    }

    for ext, lang in ext_map.items():
        if filename.endswith(ext):
            return lang

    return ''


FOLLOW_UP_PROMPT = """Based on the previous review, the developer has responded or made changes.

New context:
{context}

Please provide a brief follow-up assessment focusing only on:
1. Whether previous concerns were addressed
2. Any new issues introduced
3. Overall improvement or regression

Keep the response concise and focused."""
