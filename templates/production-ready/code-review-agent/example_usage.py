"""
Example Usage of Code Review Agent

Demonstrates how to use the agent programmatically (without webhooks).
"""
import os
from src.github_client import GitHubClient
from src.review_agent import ReviewAgent
from src.config import get_settings


def main():
    """Run a code review on a specific PR."""

    # Load settings
    settings = get_settings()

    # Initialize clients
    github_client = GitHubClient(token=settings.github_token)
    review_agent = ReviewAgent(
        github_client=github_client,
        anthropic_api_key=settings.anthropic_api_key
    )

    # Example: Review a specific PR
    # Replace with your actual repository and PR number
    owner = "your-username"
    repo = "your-repo"
    pr_number = 1

    print(f"Starting review for {owner}/{repo}#{pr_number}...")

    # Perform review
    result = review_agent.review_pull_request(owner, repo, pr_number)

    # Print results
    print("\n=== Review Results ===")
    print(f"Status: {result['status']}")

    if result["status"] == "completed":
        print(f"Cost: ${result['cost']:.4f}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Issues Found: {result['issues_found']}")
        print(f"High Severity: {result['high_severity_count']}")
        print(f"Files Reviewed: {result['files_reviewed']}")
        print(f"Elapsed Time: {result['elapsed_seconds']:.1f}s")

        if result.get("comment_url"):
            print(f"\nComment posted: {result['comment_url']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    # Get agent statistics
    stats = review_agent.get_stats()
    print("\n=== Agent Statistics ===")
    print(f"Total Reviews: {stats['reviews_completed']}")
    print(f"Total Cost: ${stats['total_cost']:.4f}")
    print(f"Average Cost: ${stats['average_cost']:.4f}")


def example_static_analysis():
    """Example: Run static analysis only (no AI review)."""
    from src.code_analyzer import CodeAnalyzer

    analyzer = CodeAnalyzer()

    # Example code to analyze
    code = '''
def authenticate_user(username, password):
    # Security issue: SQL injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)

    # Security issue: Hardcoded secret
    api_key = "sk-1234567890abcdefghijklmnop"

    # Quality issue: Long line
    result = some_very_long_function_name_that_takes_many_parameters(param1, param2, param3, param4, param5, param6, param7, param8)

    return result
    '''

    # Analyze
    results = analyzer.analyze_file("example.py", code)

    print("\n=== Static Analysis Results ===")
    for category, findings in results.items():
        print(f"\n{category.upper()} ({len(findings)} issues):")
        for finding in findings[:5]:  # Show first 5
            print(f"  - Line {finding.line}: [{finding.severity.value}] {finding.issue}")
            print(f"    Recommendation: {finding.recommendation}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "static":
        # Run static analysis example
        example_static_analysis()
    else:
        # Run full review (requires API keys)
        if not os.getenv("GITHUB_TOKEN") or not os.getenv("ANTHROPIC_API_KEY"):
            print("Error: Please set GITHUB_TOKEN and ANTHROPIC_API_KEY environment variables")
            print("\nYou can also run: python example_usage.py static")
            print("This will only run static analysis (no API keys needed)")
            sys.exit(1)

        main()
