"""
Tests for Code Analyzer

Example tests to demonstrate functionality.
"""
import pytest
from src.code_analyzer import CodeAnalyzer, SecurityScanner, CodeQualityAnalyzer, Severity


def test_security_scanner_sql_injection():
    """Test SQL injection detection."""
    scanner = SecurityScanner()

    code_with_sql_injection = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id={user_id}"
    cursor.execute(query)
    '''

    findings = scanner.scan("test.py", code_with_sql_injection)

    assert len(findings) > 0
    assert any(f.severity == Severity.HIGH for f in findings)
    assert any("SQL injection" in f.issue for f in findings)


def test_security_scanner_hardcoded_secrets():
    """Test hardcoded secret detection."""
    scanner = SecurityScanner()

    code_with_secret = '''
api_key = "sk-1234567890abcdef"
password = "super_secret_password"
    '''

    findings = scanner.scan("test.py", code_with_secret)

    assert len(findings) >= 2
    assert all(f.severity == Severity.HIGH for f in findings)


def test_quality_analyzer_long_lines():
    """Test long line detection."""
    analyzer = CodeQualityAnalyzer()

    code_with_long_line = "x = " + "a" * 150  # 150+ character line

    findings = analyzer.analyze("test.py", code_with_long_line)

    assert len(findings) > 0
    assert any("exceeds" in f.issue for f in findings)


def test_quality_analyzer_function_length():
    """Test function length detection."""
    analyzer = CodeQualityAnalyzer()

    # Create a function with 60 lines
    long_function = "def long_function():\n" + "    pass\n" * 60

    findings = analyzer.analyze("test.py", long_function)

    assert len(findings) > 0
    assert any("lines long" in f.issue for f in findings)


def test_code_analyzer_integration():
    """Test full analyzer integration."""
    analyzer = CodeAnalyzer()

    test_code = '''
def process_user_input(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id={user_id}"
    cursor.execute(query)

    # Hardcoded secret
    api_key = "sk-1234567890abcdef"

    # Long line
    x = "a" * 150

    return result
    '''

    results = analyzer.analyze_file("test.py", test_code)

    assert "security" in results
    assert "quality" in results
    assert "best_practices" in results

    # Should find multiple issues
    total_issues = sum(len(findings) for findings in results.values())
    assert total_issues > 0


def test_code_analyzer_pr():
    """Test PR-level analysis."""
    analyzer = CodeAnalyzer()

    files = [
        {
            "filename": "app.py",
            "content": '''
def get_user(id):
    query = f"SELECT * FROM users WHERE id={id}"
    return query
            '''
        },
        {
            "filename": "config.py",
            "content": '''
password = "hardcoded_password"
api_key = "sk-test123456"
            '''
        }
    ]

    results = analyzer.analyze_pr(files)

    assert "findings" in results
    assert "summary" in results

    summary = results["summary"]
    assert summary["total_issues"] > 0
    assert summary["high_severity"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
