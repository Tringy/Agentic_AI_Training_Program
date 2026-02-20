"""
Static Code Analysis and Security Scanning

Performs automated security scanning, code quality analysis, and best practices checking
before sending code to the LLM for deeper review.
"""
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


@dataclass
class Finding:
    """A code analysis finding."""
    severity: Severity
    category: str
    file: str
    line: int
    issue: str
    recommendation: str
    code_snippet: str = ""


class SecurityScanner:
    """Scans code for common security vulnerabilities."""

    # Security patterns to detect
    SECURITY_PATTERNS = {
        'sql_injection': {
            'pattern': r'(?:execute|query|cursor\.execute)\s*\(\s*["\'].*%s.*["\']|'
                      r'(?:execute|query)\s*\(\s*f["\'].*\{.*\}.*["\']|'
                      r'(?:SELECT|INSERT|UPDATE|DELETE).*\+.*\)',
            'severity': Severity.HIGH,
            'message': 'Potential SQL injection vulnerability',
            'recommendation': 'Use parameterized queries instead of string concatenation'
        },
        'hardcoded_secrets': {
            'pattern': r'(?:password|secret|api_key|token|key)\s*=\s*["\'][^"\']{8,}["\']',
            'severity': Severity.HIGH,
            'message': 'Hardcoded secret or credential detected',
            'recommendation': 'Use environment variables or secure secret management'
        },
        'xss_vulnerability': {
            'pattern': r'innerHTML\s*=|dangerouslySetInnerHTML|document\.write\(',
            'severity': Severity.HIGH,
            'message': 'Potential XSS vulnerability',
            'recommendation': 'Sanitize user input and use safe DOM manipulation methods'
        },
        'command_injection': {
            'pattern': r'(?:os\.system|subprocess\.call|exec|eval)\s*\([^)]*\+',
            'severity': Severity.HIGH,
            'message': 'Potential command injection vulnerability',
            'recommendation': 'Avoid dynamic command execution, use parameterized calls'
        },
        'path_traversal': {
            'pattern': r'open\s*\([^)]*\+|os\.path\.join\s*\([^)]*input|read\s*\([^)]*\+',
            'severity': Severity.MEDIUM,
            'message': 'Potential path traversal vulnerability',
            'recommendation': 'Validate and sanitize file paths, use allowlists'
        },
        'weak_crypto': {
            'pattern': r'md5|sha1|DES|RC4',
            'severity': Severity.MEDIUM,
            'message': 'Weak cryptographic algorithm detected',
            'recommendation': 'Use modern algorithms like SHA-256, AES-256, or bcrypt'
        }
    }

    def scan(self, filename: str, content: str) -> List[Finding]:
        """
        Scan file content for security vulnerabilities.

        Args:
            filename: Name of the file
            content: File content to scan

        Returns:
            List of security findings
        """
        findings = []
        lines = content.split('\n')

        for vuln_type, config in self.SECURITY_PATTERNS.items():
            pattern = re.compile(config['pattern'], re.IGNORECASE)

            for line_num, line in enumerate(lines, start=1):
                if pattern.search(line):
                    findings.append(Finding(
                        severity=config['severity'],
                        category='security',
                        file=filename,
                        line=line_num,
                        issue=config['message'],
                        recommendation=config['recommendation'],
                        code_snippet=line.strip()
                    ))

        return findings


class CodeQualityAnalyzer:
    """Analyzes code quality metrics."""

    def __init__(self):
        self.max_function_lines = 50
        self.max_complexity = 10
        self.max_line_length = 100

    def analyze(self, filename: str, content: str) -> List[Finding]:
        """
        Analyze code quality.

        Args:
            filename: Name of the file
            content: File content to analyze

        Returns:
            List of quality findings
        """
        findings = []
        lines = content.split('\n')

        # Check line length
        for line_num, line in enumerate(lines, start=1):
            if len(line) > self.max_line_length:
                findings.append(Finding(
                    severity=Severity.LOW,
                    category='quality',
                    file=filename,
                    line=line_num,
                    issue=f'Line exceeds {self.max_line_length} characters',
                    recommendation='Consider breaking long lines for better readability'
                ))

        # Check function length (simplified)
        findings.extend(self._check_function_length(filename, lines))

        # Check complexity indicators
        findings.extend(self._check_complexity(filename, lines))

        # Check naming conventions
        findings.extend(self._check_naming(filename, lines))

        # Check missing docstrings
        findings.extend(self._check_documentation(filename, lines))

        return findings

    def _check_function_length(self, filename: str, lines: List[str]) -> List[Finding]:
        """Check for overly long functions."""
        findings = []
        function_pattern = re.compile(r'^\s*def\s+\w+|^\s*function\s+\w+|^\s*(?:public|private|protected)?\s*\w+\s+\w+\s*\(')

        current_func_start = None
        current_func_name = None

        for line_num, line in enumerate(lines, start=1):
            if function_pattern.search(line):
                if current_func_start:
                    func_length = line_num - current_func_start
                    if func_length > self.max_function_lines:
                        findings.append(Finding(
                            severity=Severity.MEDIUM,
                            category='quality',
                            file=filename,
                            line=current_func_start,
                            issue=f'Function "{current_func_name}" is {func_length} lines long',
                            recommendation=f'Consider refactoring functions longer than {self.max_function_lines} lines'
                        ))

                match = re.search(r'(?:def|function)\s+(\w+)', line)
                current_func_name = match.group(1) if match else 'unknown'
                current_func_start = line_num

        return findings

    def _check_complexity(self, filename: str, lines: List[str]) -> List[Finding]:
        """Check for high cyclomatic complexity indicators."""
        findings = []
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']

        for line_num, line in enumerate(lines, start=1):
            # Count complexity keywords in a single line (nested conditions)
            keyword_count = sum(1 for keyword in complexity_keywords if re.search(r'\b' + keyword + r'\b', line))
            if keyword_count >= 3:
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    category='quality',
                    file=filename,
                    line=line_num,
                    issue='High complexity detected in single line',
                    recommendation='Consider simplifying nested conditions'
                ))

        return findings

    def _check_naming(self, filename: str, lines: List[str]) -> List[Finding]:
        """Check naming conventions."""
        findings = []

        # Check for single-letter variables (except common ones like i, j, x, y)
        var_pattern = re.compile(r'\b([a-z])\s*=\s*')

        for line_num, line in enumerate(lines, start=1):
            matches = var_pattern.findall(line)
            for var in matches:
                if var not in ['i', 'j', 'k', 'x', 'y', 'n']:
                    findings.append(Finding(
                        severity=Severity.LOW,
                        category='quality',
                        file=filename,
                        line=line_num,
                        issue=f'Single-letter variable name "{var}" reduces readability',
                        recommendation='Use descriptive variable names'
                    ))

        return findings

    def _check_documentation(self, filename: str, lines: List[str]) -> List[Finding]:
        """Check for missing documentation."""
        findings = []
        function_pattern = re.compile(r'^\s*def\s+(\w+)|^\s*function\s+(\w+)')

        for line_num, line in enumerate(lines, start=1):
            match = function_pattern.search(line)
            if match:
                func_name = match.group(1) or match.group(2)
                # Check if next non-empty line is a docstring
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if not next_line.startswith('"""') and not next_line.startswith("'''") and \
                       not next_line.startswith('//') and not next_line.startswith('/*'):
                        # Skip simple getters/setters and private functions
                        if not func_name.startswith('_') and not func_name.startswith('get') and not func_name.startswith('set'):
                            findings.append(Finding(
                                severity=Severity.LOW,
                                category='documentation',
                                file=filename,
                                line=line_num,
                                issue=f'Function "{func_name}" missing documentation',
                                recommendation='Add docstring explaining purpose, parameters, and return value'
                            ))

        return findings


class BestPracticesChecker:
    """Checks for language-specific best practices."""

    def check(self, filename: str, content: str) -> List[Finding]:
        """
        Check for best practices violations.

        Args:
            filename: Name of the file
            content: File content to check

        Returns:
            List of best practice findings
        """
        findings = []
        extension = self._get_extension(filename)

        if extension == 'py':
            findings.extend(self._check_python_practices(filename, content))
        elif extension in ['js', 'ts']:
            findings.extend(self._check_javascript_practices(filename, content))

        return findings

    def _get_extension(self, filename: str) -> str:
        """Get file extension."""
        parts = filename.split('.')
        return parts[-1] if len(parts) > 1 else ''

    def _check_python_practices(self, filename: str, content: str) -> List[Finding]:
        """Check Python-specific best practices."""
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Check for bare except
            if re.search(r'except\s*:', line):
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    category='best_practices',
                    file=filename,
                    line=line_num,
                    issue='Bare except clause catches all exceptions',
                    recommendation='Catch specific exceptions or use "except Exception:"'
                ))

            # Check for mutable default arguments
            if re.search(r'def\s+\w+\([^)]*=\s*[\[\{]', line):
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    category='best_practices',
                    file=filename,
                    line=line_num,
                    issue='Mutable default argument detected',
                    recommendation='Use None as default and initialize inside function'
                ))

        return findings

    def _check_javascript_practices(self, filename: str, content: str) -> List[Finding]:
        """Check JavaScript/TypeScript best practices."""
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Check for var usage
            if re.search(r'\bvar\s+\w+', line):
                findings.append(Finding(
                    severity=Severity.LOW,
                    category='best_practices',
                    file=filename,
                    line=line_num,
                    issue='Use of "var" keyword',
                    recommendation='Use "const" or "let" instead of "var"'
                ))

            # Check for == instead of ===
            if re.search(r'[^=!<>]==[^=]', line):
                findings.append(Finding(
                    severity=Severity.LOW,
                    category='best_practices',
                    file=filename,
                    line=line_num,
                    issue='Loose equality operator (==) used',
                    recommendation='Use strict equality (===) instead'
                ))

        return findings


class CodeAnalyzer:
    """
    Main code analyzer that coordinates all analysis components.
    """

    def __init__(self):
        self.security_scanner = SecurityScanner()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.best_practices_checker = BestPracticesChecker()

    def analyze_file(self, filename: str, content: str) -> Dict[str, List[Finding]]:
        """
        Perform comprehensive analysis on a file.

        Args:
            filename: Name of the file
            content: File content

        Returns:
            Dictionary of findings by category
        """
        security_findings = self.security_scanner.scan(filename, content)
        quality_findings = self.quality_analyzer.analyze(filename, content)
        best_practices_findings = self.best_practices_checker.check(filename, content)

        return {
            'security': security_findings,
            'quality': quality_findings,
            'best_practices': best_practices_findings
        }

    def analyze_pr(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all files in a pull request.

        Args:
            files: List of file objects with filename and content/patch

        Returns:
            Aggregated analysis results
        """
        all_findings = {
            'security': [],
            'quality': [],
            'best_practices': []
        }

        for file_obj in files:
            filename = file_obj.get('filename', '')
            content = file_obj.get('content', '') or file_obj.get('patch', '')

            if not content:
                continue

            findings = self.analyze_file(filename, content)

            for category, finding_list in findings.items():
                all_findings[category].extend(finding_list)

        # Sort by severity
        for category in all_findings:
            all_findings[category].sort(
                key=lambda x: ['HIGH', 'MEDIUM', 'LOW', 'INFO'].index(x.severity.name)
            )

        return {
            'findings': all_findings,
            'summary': self._create_summary(all_findings)
        }

    def _create_summary(self, findings: Dict[str, List[Finding]]) -> Dict[str, Any]:
        """Create a summary of findings."""
        total = sum(len(f) for f in findings.values())
        high = sum(1 for category in findings.values() for f in category if f.severity == Severity.HIGH)
        medium = sum(1 for category in findings.values() for f in category if f.severity == Severity.MEDIUM)
        low = sum(1 for category in findings.values() for f in category if f.severity == Severity.LOW)

        return {
            'total_issues': total,
            'high_severity': high,
            'medium_severity': medium,
            'low_severity': low,
            'by_category': {
                category: len(finding_list)
                for category, finding_list in findings.items()
            }
        }
