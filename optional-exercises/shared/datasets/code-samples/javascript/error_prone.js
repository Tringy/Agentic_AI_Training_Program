/**
 * WARNING: This file contains intentional security vulnerabilities for educational purposes.
 * DO NOT use this code in production. These are examples of what NOT to do.
 */

// VULNERABILITY 1: Cross-Site Scripting (XSS)
function displayUserComment_UNSAFE(comment) {
  // Bad: Directly inserting user input into HTML without sanitization
  document.getElementById('comments').innerHTML += `
    <div class="comment">${comment}</div>
  `;
  // An attacker could inject: <script>alert('XSS')</script>
}

// VULNERABILITY 2: Insecure Direct Object Reference
function getUserData_UNSAFE(userId) {
  // Bad: No authorization check - anyone can access any user's data
  return fetch(`/api/users/${userId}`)
    .then(response => response.json());
}

// VULNERABILITY 3: Eval with User Input
function calculateExpression_UNSAFE(expression) {
  // Bad: eval() executes arbitrary code
  return eval(expression);
  // An attacker could inject: "process.exit()" or worse
}

// VULNERABILITY 4: Weak Random Values for Security
function generateToken_UNSAFE() {
  // Bad: Math.random() is not cryptographically secure
  return Math.random().toString(36).substring(2);
}

// VULNERABILITY 5: SQL Injection (in server-side JavaScript)
function findUser_UNSAFE(username) {
  const db = require('some-db-library');
  // Bad: String concatenation allows SQL injection
  const query = `SELECT * FROM users WHERE username = '${username}'`;
  return db.execute(query);
}

// VULNERABILITY 6: Sensitive Data in Client-Side Code
const CONFIG_UNSAFE = {
  // Bad: API keys should never be in client-side code
  apiKey: 'sk-1234567890abcdef',
  secretToken: 'my-secret-token',
  adminPassword: 'admin123'
};

// VULNERABILITY 7: No CSRF Protection
function deleteAccount_UNSAFE(accountId) {
  // Bad: No CSRF token validation
  fetch(`/api/accounts/${accountId}`, {
    method: 'DELETE'
  });
}

// VULNERABILITY 8: Insecure Data Storage
function saveCredentials_UNSAFE(username, password) {
  // Bad: Storing sensitive data in localStorage without encryption
  localStorage.setItem('username', username);
  localStorage.setItem('password', password);
}

// VULNERABILITY 9: Missing Input Validation
function processPayment_UNSAFE(amount) {
  // Bad: No validation - amount could be negative or non-numeric
  return fetch('/api/payment', {
    method: 'POST',
    body: JSON.stringify({ amount })
  });
}

// VULNERABILITY 10: Prototype Pollution
function merge_UNSAFE(target, source) {
  // Bad: Can pollute Object prototype
  for (let key in source) {
    target[key] = source[key];
  }
  return target;
  // An attacker could inject: {"__proto__": {"isAdmin": true}}
}

// CORRECT EXAMPLES FOR COMPARISON:

/**
 * SAFE: Properly sanitize and use textContent instead of innerHTML
 */
function displayUserComment_SAFE(comment) {
  const commentDiv = document.createElement('div');
  commentDiv.className = 'comment';
  commentDiv.textContent = comment; // Safe - treats as text, not HTML
  document.getElementById('comments').appendChild(commentDiv);
}

/**
 * SAFE: Validate authorization before accessing data
 */
async function getUserData_SAFE(userId, currentUserId) {
  // Good: Check authorization
  if (userId !== currentUserId) {
    throw new Error('Unauthorized access');
  }

  const response = await fetch(`/api/users/${userId}`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user data');
  }

  return response.json();
}

/**
 * SAFE: Use crypto for cryptographically secure random values
 */
function generateToken_SAFE() {
  // Good: Use crypto.randomBytes for security-sensitive operations
  const crypto = require('crypto');
  return crypto.randomBytes(32).toString('hex');
}

/**
 * SAFE: Use parameterized queries
 */
function findUser_SAFE(username) {
  const db = require('some-db-library');
  // Good: Parameterized query prevents SQL injection
  const query = 'SELECT * FROM users WHERE username = ?';
  return db.execute(query, [username]);
}

/**
 * SAFE: Store sensitive data securely
 */
function saveCredentials_SAFE(username, password) {
  // Good: Never store passwords client-side
  // Only store a secure session token after authentication
  const sessionToken = generateToken_SAFE();
  sessionStorage.setItem('sessionToken', sessionToken);
  // Note: Even sessionStorage has risks; httpOnly cookies are better
}

/**
 * SAFE: Validate input thoroughly
 */
function processPayment_SAFE(amount) {
  // Good: Validate input
  if (typeof amount !== 'number' || amount <= 0 || !isFinite(amount)) {
    throw new Error('Invalid payment amount');
  }

  if (amount > 10000) {
    throw new Error('Amount exceeds maximum allowed');
  }

  return fetch('/api/payment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken()
    },
    body: JSON.stringify({ amount })
  });
}

/**
 * SAFE: Prevent prototype pollution
 */
function merge_SAFE(target, source) {
  // Good: Only copy own properties, exclude __proto__
  for (let key in source) {
    if (source.hasOwnProperty(key) && key !== '__proto__' && key !== 'constructor') {
      target[key] = source[key];
    }
  }
  return target;
}

// Helper functions for safe examples
function getAuthToken() {
  return sessionStorage.getItem('sessionToken');
}

function getCsrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content;
}

module.exports = {
  // Unsafe examples (for education only)
  displayUserComment_UNSAFE,
  getUserData_UNSAFE,
  calculateExpression_UNSAFE,
  generateToken_UNSAFE,

  // Safe examples
  displayUserComment_SAFE,
  getUserData_SAFE,
  generateToken_SAFE,
  processPayment_SAFE,
  merge_SAFE
};
