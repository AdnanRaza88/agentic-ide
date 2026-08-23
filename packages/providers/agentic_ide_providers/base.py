"""Base adapter utilities (retry, timeout, HTTP helpers)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, TypeVar

import httpx

from agentic_ide_contracts.interfaces.model_provider import (
    ModelCapabilities,
    ModelInfo,
)
from agentic_ide_providers.config import ProviderConfig, RetryPolicy
from agentic_ide_providers.errors import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    TimeoutError,
    TransientError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseProviderAdapter:
    """Shared behaviour for HTTP-based model provider adapters."""

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config
        self._client: httpx.AsyncClient | None = None

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ProviderConfig:
        return self._config

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = dict(self._config.extra_headers)
            key = self._config.api_key_str()
            if key:
                headers.setdefault("Authorization", f"Bearer {key}")
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url or "",
                headers=headers,
                timeout=httpx.Timeout(self._config.timeout_seconds),
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _with_retry(
        self,
        operation: str,
        fn: Callable[[], Any],
        *,
        retry_policy: RetryPolicy | None = None,
    ) -> Any:
        policy = retry_policy or self._config.retry
        last_exc: Exception | None = None
        for attempt in range(1, policy.max_attempts + 1):
            try:
                return await fn()
            except (TimeoutError, TransientError, RateLimitError) as exc:
                last_exc = exc
                if attempt >= policy.max_attempts or not getattr(exc, "retryable", True):
                    raise
                delay = policy.delay_for_attempt(attempt + 1)
                logger.warning(
                    "%s.%s attempt %s failed (%s); retrying in %.2fs",
                    self.name, operation, attempt, exc, delay,
                )
                await asyncio.sleep(delay)
            except ProviderError:
                raise
            except httpx.TimeoutException as exc:
                last_exc = TimeoutError(str(exc), provider=self.name, retryable=True, raw=exc)
                if attempt >= policy.max_attempts:
                    raise last_exc from exc
                delay = policy.delay_for_attempt(attempt + 1)
                await asyncio.sleep(delay)
            except httpx.HTTPStatusError as exc:
                mapped = self._map_http_error(exc)
                if not mapped.retryable or attempt >= policy.max_attempts:
                    raise mapped from exc
                last_exc = mapped
                delay = policy.delay_for_attempt(attempt + 1)
                await asyncio.sleep(delay)
            except Exception as exc:  # noqa: BLE001
                raise ProviderError(
                    f"Unexpected error in {operation}: {exc}",
                    provider=self.name,
                    raw=exc,
                ) from exc
        assert last_exc is not None
        raise last_exc

    def _map_http_error(self, exc: httpx.HTTPStatusError) -> ProviderError:
        status = exc.response.status_code
        body: Any = None
        try:
            body = exc.response.json()
        except Exception:  # noqa: BLE001
            body = exc.response.text
        msg = f"HTTP {status}"
        if isinstance(body, dict):
            msg = body.get("error", {}).get("message") or body.get("message") or msg
        if status in (401, 403):
            return AuthenticationError(str(msg), provider=self.name, status_code=status, raw=body)
        if status == 429:
            return RateLimitError(str(msg), provider=self.name, status_code=status, raw=body)
        if status >= 500:
            return TransientError(str(msg), provider=self.name, status_code=status, raw=body)
        return ProviderError(str(msg), provider=self.name, status_code=status, retryable=False, raw=body)

    async def list_models(self) -> list[ModelInfo]:
        return []

    async def get_capabilities(self, model_id: str) -> ModelCapabilities | None:
        return None

    async def health(self) -> bool:
        try:
            await self.list_models()
            return True
        except AuthenticationError:
            return False
        except Exception:  # noqa: BLE001
            return False
