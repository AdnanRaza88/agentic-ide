"""Provider configuration and retry policy."""

from __future__ import annotations

from pydantic import BaseModel, Field, SecretStr


class RetryPolicy(BaseModel):
    """Configurable retry behaviour for provider calls."""

    max_attempts: int = Field(default=3, ge=1, le=10)
    base_delay_seconds: float = Field(default=0.5, ge=0.0)
    max_delay_seconds: float = Field(default=30.0, ge=0.0)
    exponential_base: float = Field(default=2.0, ge=1.0)
    jitter: bool = True

    def delay_for_attempt(self, attempt: int) -> float:
        """Return delay in seconds before the given attempt (1-based)."""
        if attempt <= 1:
            return 0.0
        delay = min(
            self.base_delay_seconds * (self.exponential_base ** (attempt - 2)),
            self.max_delay_seconds,
        )
        if self.jitter:
            delay = delay * (0.5 + (attempt % 10) / 20.0)
        return delay


class ProviderConfig(BaseModel):
    """Configuration for a single provider instance."""

    name: str
    api_key: SecretStr | None = None
    base_url: str | None = None
    timeout_seconds: float = Field(default=60.0, ge=1.0)
    default_model: str | None = None
    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    extra_headers: dict[str, str] = Field(default_factory=dict)
    extra: dict[str, object] = Field(default_factory=dict)

    def api_key_str(self) -> str | None:
        if self.api_key is None:
            return None
        return self.api_key.get_secret_value()
