"""
GitHub API Client with Rate Limiting and Retry Logic

Handles all GitHub API interactions including:
- Fetching PR details and files
- Posting review comments
- Managing rate limits
- Exponential backoff retry
"""
import time
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information."""
    limit: int
    remaining: int
    reset_time: float


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    pass


class RateLimitExceeded(GitHubAPIError):
    """Raised when rate limit is exceeded."""
    pass


class GitHubClient:
    """
    GitHub API client with rate limiting and retry logic.

    Features:
    - Automatic rate limit handling
    - Exponential backoff retry
    - Request caching
    - Error recovery
    """

    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token
            base_url: GitHub API base URL
        """
        self.token = token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Code-Review-Agent/1.0"
        })
        self._rate_limit_info: Optional[RateLimitInfo] = None

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request details.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request data

        Raises:
            GitHubAPIError: If API request fails
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        return self._request("GET", url)

    def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        max_files: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get files changed in a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            max_files: Maximum number of files to fetch

        Returns:
            List of file objects with diffs

        Raises:
            GitHubAPIError: If API request fails
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        params = {"per_page": min(max_files, 100)}

        files = self._request("GET", url, params=params)

        # Limit files
        files = files[:max_files]

        logger.info(f"Retrieved {len(files)} files for PR #{pr_number}")
        return files

    def post_review_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        commit_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a review comment on a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            body: Comment body (markdown)
            commit_id: Optional commit ID to associate with

        Returns:
            Created comment data

        Raises:
            GitHubAPIError: If API request fails
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        data = {"body": body}

        logger.info(f"Posting review comment to PR #{pr_number}")
        result = self._request("POST", url, json=data)
        logger.info(f"Successfully posted comment: {result.get('html_url')}")

        return result

    def post_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_id: str,
        body: str,
        event: str = "COMMENT"
    ) -> Dict[str, Any]:
        """
        Post a full review (with possible approval/request changes).

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            commit_id: Commit SHA to review
            body: Review body
            event: Review event (COMMENT, APPROVE, REQUEST_CHANGES)

        Returns:
            Created review data

        Raises:
            GitHubAPIError: If API request fails
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        data = {
            "commit_id": commit_id,
            "body": body,
            "event": event
        }

        logger.info(f"Posting review to PR #{pr_number} with event {event}")
        return self._request("POST", url, json=data)

    def get_rate_limit(self) -> RateLimitInfo:
        """
        Get current rate limit information.

        Returns:
            Rate limit info

        Raises:
            GitHubAPIError: If API request fails
        """
        url = f"{self.base_url}/rate_limit"
        data = self._request("GET", url, skip_rate_limit_check=True)

        core = data.get("resources", {}).get("core", {})
        return RateLimitInfo(
            limit=core.get("limit", 5000),
            remaining=core.get("remaining", 0),
            reset_time=core.get("reset", time.time())
        )

    def _request(
        self,
        method: str,
        url: str,
        skip_rate_limit_check: bool = False,
        max_retries: int = 3,
        **kwargs
    ) -> Any:
        """
        Make HTTP request with retry logic and rate limiting.

        Args:
            method: HTTP method
            url: Request URL
            skip_rate_limit_check: Skip rate limit check
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON data

        Raises:
            GitHubAPIError: If request fails after retries
            RateLimitExceeded: If rate limit is exceeded
        """
        # Check rate limit before making request
        if not skip_rate_limit_check:
            self._check_rate_limit()

        last_exception = None

        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, **kwargs)

                # Update rate limit info from headers
                self._update_rate_limit_from_headers(response.headers)

                # Handle rate limiting
                if response.status_code == 403 and 'rate limit' in response.text.lower():
                    reset_time = float(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                    wait_time = max(reset_time - time.time(), 0)

                    logger.warning(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds...")

                    if wait_time > 300:  # Don't wait more than 5 minutes
                        raise RateLimitExceeded(f"Rate limit reset in {wait_time:.0f} seconds")

                    time.sleep(wait_time + 1)
                    continue

                # Handle other errors with exponential backoff
                if response.status_code >= 500:
                    wait_time = (2 ** attempt) * 1.0  # Exponential backoff
                    logger.warning(
                        f"Server error {response.status_code}. "
                        f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()

                # Return JSON data
                return response.json() if response.content else {}

            except requests.exceptions.RequestException as e:
                last_exception = e
                wait_time = (2 ** attempt) * 1.0

                logger.warning(
                    f"Request failed: {str(e)}. "
                    f"Retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})"
                )

                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue

        # All retries failed
        error_msg = f"Request failed after {max_retries} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg)

    def _check_rate_limit(self):
        """Check if we're approaching rate limits."""
        if not self._rate_limit_info:
            try:
                self._rate_limit_info = self.get_rate_limit()
            except Exception as e:
                logger.warning(f"Failed to get rate limit info: {e}")
                return

        if self._rate_limit_info.remaining < 10:
            reset_time = self._rate_limit_info.reset_time
            wait_time = max(reset_time - time.time(), 0)

            if wait_time > 0:
                logger.warning(
                    f"Approaching rate limit. "
                    f"{self._rate_limit_info.remaining} requests remaining. "
                    f"Reset in {wait_time:.0f}s"
                )

    def _update_rate_limit_from_headers(self, headers: Dict[str, str]):
        """Update rate limit info from response headers."""
        try:
            if 'X-RateLimit-Remaining' in headers:
                self._rate_limit_info = RateLimitInfo(
                    limit=int(headers.get('X-RateLimit-Limit', 5000)),
                    remaining=int(headers.get('X-RateLimit-Remaining', 0)),
                    reset_time=float(headers.get('X-RateLimit-Reset', time.time()))
                )
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse rate limit headers: {e}")


def parse_repo_info(repo_url: str) -> tuple[str, str]:
    """
    Parse owner and repo from GitHub URL.

    Args:
        repo_url: GitHub repository URL

    Returns:
        Tuple of (owner, repo)

    Examples:
        >>> parse_repo_info("https://github.com/owner/repo")
        ('owner', 'repo')
    """
    parts = repo_url.rstrip('/').split('/')
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    raise ValueError(f"Invalid GitHub URL: {repo_url}")
