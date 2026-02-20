/**
 * Simple utility functions for common operations.
 * These are basic examples for testing code comprehension.
 */

/**
 * Reverse a string
 * @param {string} str - The string to reverse
 * @returns {string} The reversed string
 */
function reverseString(str) {
  return str.split('').reverse().join('');
}

/**
 * Find the maximum number in an array
 * @param {number[]} numbers - Array of numbers
 * @returns {number} The maximum number
 */
function findMax(numbers) {
  return Math.max(...numbers);
}

/**
 * Check if a string is a palindrome
 * @param {string} str - The string to check
 * @returns {boolean} True if palindrome, false otherwise
 */
function isPalindrome(str) {
  const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
  return cleaned === cleaned.split('').reverse().join('');
}

/**
 * Calculate sum of array elements
 * @param {number[]} arr - Array of numbers
 * @returns {number} Sum of all elements
 */
function sumArray(arr) {
  return arr.reduce((sum, num) => sum + num, 0);
}

/**
 * Remove duplicates from an array
 * @param {Array} arr - Array with potential duplicates
 * @returns {Array} Array with unique elements
 */
function removeDuplicates(arr) {
  return [...new Set(arr)];
}

module.exports = {
  reverseString,
  findMax,
  isPalindrome,
  sumArray,
  removeDuplicates
};
