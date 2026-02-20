"""
Code Review Agent - Production-Ready Implementation

A GitHub-integrated code review agent that automatically reviews pull requests
and provides security, quality, and best practices feedback.

Components:
- webhook_server: FastAPI webhook receiver
- code_analyzer: Static analysis and security scanning
- github_client: GitHub API integration with rate limiting
- review_agent: AI-powered code review orchestrator
- config: Configuration and environment management
- prompts: LLM prompts for code review
"""

__version__ = "1.0.0"
