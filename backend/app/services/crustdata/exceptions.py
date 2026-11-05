"""
Crustdata Integration Exceptions.
"""


class CrustdataError(Exception):
    """Base exception for Crustdata operations."""
    pass


class CrustdataAPIError(CrustdataError):
    """Raised when Crustdata API returns an error status code."""
    def __init__(self, status_code: int, message: str, details: dict = None):
        super().__init__(f"Crustdata API Error [{status_code}]: {message}")
        self.status_code = status_code
        self.message = message
        self.details = details or {}


class CrustdataCreditDepletedError(CrustdataError):
    """Raised when an operation would violate the credit safety threshold."""
    def __init__(self, current_balance: float, required_credits: float, min_threshold: float):
        super().__init__(
            f"Insufficient Crustdata credits: current balance {current_balance:.1f}, "
            f"required {required_credits:.1f}, minimum safety threshold {min_threshold:.1f}"
        )
        self.current_balance = current_balance
        self.required_credits = required_credits
        self.min_threshold = min_threshold


class CrustdataRateLimitError(CrustdataError):
    """Raised when rate limits are exceeded (HTTP 429)."""
    def __init__(self, retry_after: int = 60):
        super().__init__(f"Crustdata rate limit reached. Retry after {retry_after} seconds.")
        self.retry_after = retry_after


class CrustdataAuthError(CrustdataError):
    """Raised when API key is missing, invalid, or unauthorized (HTTP 401/403)."""
    pass


class CrustdataAmbiguousEntityError(CrustdataError):
    """Raised when multiple candidates match and automated enrichment is forbidden."""
    def __init__(self, query: str, candidate_count: int, candidates: list):
        super().__init__(
            f"Ambiguous query '{query}' matched {candidate_count} candidates. "
            f"Explicit candidate selection required."
        )
        self.query = query
        self.candidate_count = candidate_count
        self.candidates = candidates
