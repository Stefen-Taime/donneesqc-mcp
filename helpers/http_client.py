"""Client HTTP async avec retry exponentiel."""

import asyncio
import logging
from typing import Any

import httpx

from helpers.config import HTTP_MAX_RETRIES, HTTP_TIMEOUT, HTTP_USER_AGENT

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _client  # noqa: PLW0603
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(HTTP_TIMEOUT),
            headers={"User-Agent": HTTP_USER_AGENT},
            follow_redirects=True,
        )
    return _client


async def _retry(
    fn,
    *,
    url: str,
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    """Exécute une requête HTTP avec retry et backoff exponentiel."""
    client = await get_client()
    last_error: Exception | None = None

    for attempt in range(HTTP_MAX_RETRIES):
        try:
            resp = await fn(client, url, params)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as e:
            logger.warning("HTTP %s pour %s (tentative %d/%d)", e.response.status_code, url, attempt + 1, HTTP_MAX_RETRIES)
            last_error = e
            if e.response.status_code < 500:
                raise
        except httpx.RequestError as e:
            logger.warning("Erreur réseau pour %s (tentative %d/%d): %s", url, attempt + 1, HTTP_MAX_RETRIES, e)
            last_error = e

        # Backoff exponentiel : 1s, 2s, 4s...
        if attempt < HTTP_MAX_RETRIES - 1:
            delay = 2**attempt
            logger.debug("Retry dans %ds pour %s", delay, url)
            await asyncio.sleep(delay)

    msg = f"Échec après {HTTP_MAX_RETRIES} tentatives pour {url}"
    raise RuntimeError(msg) from last_error


async def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET JSON avec retry exponentiel."""
    resp = await _retry(
        lambda client, u, p: client.get(u, params=p),
        url=url,
        params=params,
    )
    return resp.json()  # type: ignore[no-any-return]


async def fetch_text(url: str, params: dict[str, Any] | None = None) -> str:
    """GET retournant du texte brut (XML, etc.) avec retry exponentiel."""
    resp = await _retry(
        lambda client, u, p: client.get(u, params=p),
        url=url,
        params=params,
    )
    return resp.text


async def close() -> None:
    global _client  # noqa: PLW0603
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
