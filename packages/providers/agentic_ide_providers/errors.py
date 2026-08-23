"""Normalized provider errors.

All adapters must raise subclasses of ProviderError so that callers
never need to handle vendor-specific exception types.
"""

from __future__ import annotations


class ProviderError(Exception):
    """Base class for all model-provider failures."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
        retryable: bool = False,
        raw: object | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.retryable = retryable
        self.raw = raw


class AuthenticationError(ProviderError):
    """Invalid or missing credentials."""

    def __init__(self, message: str = "Authentication failed", **kwargs: object) -> None:
        super().__init__(message, retryable=False, **kwargs)  # type: ignore[arg-type]


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs: object) -> None:
        super().__init__(message, retryable=True, **kwargs)  # type: ignore[arg-type]


class TimeoutError(ProviderError):
    """Request timed out."""

    def __init__(self, message: str = "Request timed out", **kwargs: object) -> None:
        super().__init__(message, retryable=True, **kwargs)  # type: ignore[arg-type]


class TransientError(ProviderError):
    """Temporary failure that may succeed on retry."""

    def __init__(self, message: str = "Transient provider error", **kwargs: object) -> None:
        super().__init__(message, retryable=True, **kwargs)  # type: ignore[arg-type]


class UnsupportedFeatureError(ProviderError):
    """Requested feature is not supported by this provider/model."""

    def __init__(self, message: str = "Feature not supported", **kwargs: object) -> None:
        super().__init__(message, retryable=False, **kwargs)  # type: ignore[arg-type]
