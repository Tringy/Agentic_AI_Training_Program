"""
WARNING: This file contains intentional security vulnerabilities for educational purposes.
DO NOT use this code in production. These are examples of what NOT to do.
"""

import sqlite3
import pickle
import os


# VULNERABILITY 1: SQL Injection
def get_user_by_name_unsafe(username):
    """UNSAFE: Vulnerable to SQL injection attacks."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Bad: String concatenation allows SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


# VULNERABILITY 2: Command Injection
def ping_host_unsafe(host):
    """UNSAFE: Vulnerable to command injection."""
    # Bad: Using user input directly in shell command
    os.system(f"ping -c 1 {host}")


# VULNERABILITY 3: Insecure Deserialization
def load_user_data_unsafe(data):
    """UNSAFE: Pickle can execute arbitrary code during deserialization."""
    # Bad: Deserializing untrusted data
    return pickle.loads(data)


# VULNERABILITY 4: Path Traversal
def read_file_unsafe(filename):
    """UNSAFE: Allows path traversal attacks."""
    # Bad: No validation of file path
    with open(f"/app/uploads/{filename}", 'r') as f:
        return f.read()


# VULNERABILITY 5: Hardcoded Credentials
def connect_to_database_unsafe():
    """UNSAFE: Hardcoded credentials in source code."""
    # Bad: Credentials should never be hardcoded
    username = "admin"
    password = "password123"
    api_key = "sk-1234567890abcdef"
    return f"Connecting with {username}:{password}"


# VULNERABILITY 6: Weak Cryptography
def encrypt_password_unsafe(password):
    """UNSAFE: Using weak/broken cryptographic algorithms."""
    import hashlib
    # Bad: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()


# VULNERABILITY 7: Missing Input Validation
def calculate_discount_unsafe(price, discount_percent):
    """UNSAFE: No input validation."""
    # Bad: Doesn't validate that discount is reasonable
    return price * (1 - discount_percent / 100)


# CORRECT EXAMPLES FOR COMPARISON:

def get_user_by_name_safe(username):
    """SAFE: Uses parameterized queries to prevent SQL injection."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Good: Parameterized query
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    return result


def read_file_safe(filename):
    """SAFE: Validates file path to prevent traversal."""
    import pathlib
    # Good: Validate and sanitize file path
    safe_path = pathlib.Path(f"/app/uploads/{filename}").resolve()
    if not str(safe_path).startswith("/app/uploads/"):
        raise ValueError("Invalid file path")
    with open(safe_path, 'r') as f:
        return f.read()
