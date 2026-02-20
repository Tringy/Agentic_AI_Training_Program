/**
 * Asynchronous JavaScript patterns using Promises and async/await.
 * Demonstrates modern async programming techniques.
 */

/**
 * Simulate an API call with delay
 * @param {string} url - The URL to fetch
 * @param {number} delay - Delay in milliseconds
 * @returns {Promise<Object>} Response data
 */
function simulateAPICall(url, delay = 1000) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (url.includes('error')) {
        reject(new Error(`Failed to fetch ${url}`));
      } else {
        resolve({
          url,
          data: `Response from ${url}`,
          timestamp: Date.now()
        });
      }
    }, delay);
  });
}

/**
 * Fetch data with retry logic
 * @param {string} url - URL to fetch
 * @param {number} maxRetries - Maximum number of retry attempts
 * @returns {Promise<Object>} Response data
 */
async function fetchWithRetry(url, maxRetries = 3) {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await simulateAPICall(url);
      return response;
    } catch (error) {
      lastError = error;
      if (attempt < maxRetries) {
        console.log(`Attempt ${attempt} failed, retrying...`);
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }

  throw new Error(`Failed after ${maxRetries} attempts: ${lastError.message}`);
}

/**
 * Fetch multiple URLs concurrently
 * @param {string[]} urls - Array of URLs to fetch
 * @returns {Promise<Object[]>} Array of responses
 */
async function fetchMultiple(urls) {
  const promises = urls.map(url => simulateAPICall(url));
  return await Promise.all(promises);
}

/**
 * Fetch URLs with individual error handling
 * @param {string[]} urls - Array of URLs to fetch
 * @returns {Promise<Object[]>} Array of results (success or error)
 */
async function fetchMultipleWithErrors(urls) {
  const promises = urls.map(url =>
    simulateAPICall(url)
      .then(data => ({ status: 'success', data }))
      .catch(error => ({ status: 'error', error: error.message }))
  );
  return await Promise.all(promises);
}

/**
 * Process items sequentially with async operations
 * @param {Array} items - Items to process
 * @param {Function} processor - Async function to process each item
 * @returns {Promise<Array>} Processed results
 */
async function processSequentially(items, processor) {
  const results = [];
  for (const item of items) {
    const result = await processor(item);
    results.push(result);
  }
  return results;
}

/**
 * Process items in batches
 * @param {Array} items - Items to process
 * @param {number} batchSize - Number of items per batch
 * @param {Function} processor - Async function to process each item
 * @returns {Promise<Array>} All results
 */
async function processBatches(items, batchSize, processor) {
  const results = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(item => processor(item))
    );
    results.push(...batchResults);
  }

  return results;
}

/**
 * Timeout wrapper for promises
 * @param {Promise} promise - Promise to wrap
 * @param {number} timeoutMs - Timeout in milliseconds
 * @returns {Promise} Promise that rejects on timeout
 */
function withTimeout(promise, timeoutMs) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Operation timed out')), timeoutMs)
    )
  ]);
}

// Example usage
async function exampleUsage() {
  try {
    // Single fetch with retry
    const data = await fetchWithRetry('https://api.example.com/data');
    console.log('Fetched:', data);

    // Multiple concurrent fetches
    const urls = [
      'https://api.example.com/users',
      'https://api.example.com/posts',
      'https://api.example.com/comments'
    ];
    const results = await fetchMultiple(urls);
    console.log('All results:', results);

    // With timeout
    const timeoutResult = await withTimeout(
      simulateAPICall('https://api.example.com/slow'),
      5000
    );
    console.log('Got result before timeout:', timeoutResult);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

module.exports = {
  simulateAPICall,
  fetchWithRetry,
  fetchMultiple,
  fetchMultipleWithErrors,
  processSequentially,
  processBatches,
  withTimeout
};
