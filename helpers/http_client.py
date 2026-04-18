"""Client HTTP async avec retry exponentiel et support Retry-After."""

import asyncio
import logging
from typing import Any

import httpx

from helpers.config import DOWNLOAD_MAX_BYTES, HTTP_MAX_RETRIES, HTTP_TIMEOUT, HTTP_USER_AGENT

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


def _get_retry_after(response: httpx.Response) -> float | None:
    """Extrait le delai Retry-After d'une reponse 429."""
    header = response.headers.get("Retry-After")
    if header is None:
        return None
    try:
        return float(header)
    except ValueError:
        return None


async def _retry(
    fn,
    *,
    url: str,
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    """Execute une requete HTTP avec retry, backoff exponentiel et support Retry-After."""
    client = await get_client()
    last_error: Exception | None = None

    for attempt in range(HTTP_MAX_RETRIES):
        try:
            resp = await fn(client, url, params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "HTTP %s pour %s (tentative %d/%d)",
                e.response.status_code,
                url,
                attempt + 1,
                HTTP_MAX_RETRIES,
            )
            last_error = e

            # Respecter Retry-After sur 429
            if e.response.status_code == 429:
                retry_after = _get_retry_after(e.response)
                if retry_after is not None and attempt < HTTP_MAX_RETRIES - 1:
                    delay = min(retry_after, 60.0)  # cap a 60s
                    logger.info("429 Retry-After: %ss pour %s", delay, url)
                    await asyncio.sleep(delay)
                    continue

            if e.response.status_code < 500 and e.response.status_code != 429:
                raise
        except httpx.RequestError as e:
            logger.warning(
                "Erreur reseau pour %s (tentative %d/%d): %s",
                url,
                attempt + 1,
                HTTP_MAX_RETRIES,
                e,
            )
            last_error = e
        else:
            return resp

        # Backoff exponentiel : 1s, 2s, 4s...
        if attempt < HTTP_MAX_RETRIES - 1:
            delay = 2**attempt
            logger.debug("Retry dans %ds pour %s", delay, url)
            await asyncio.sleep(delay)

    msg = f"Echec apres {HTTP_MAX_RETRIES} tentatives pour {url}"
    raise RuntimeError(msg) from last_error


async def fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET JSON avec retry exponentiel."""
    resp = await _retry(
        lambda client, u, p: client.get(u, params=p),
        url=url,
        params=params,
    )
    return resp.json()


async def fetch_text(url: str, params: dict[str, Any] | None = None) -> str:
    """GET retournant du texte brut (XML, etc.) avec retry exponentiel."""
    resp = await _retry(
        lambda client, u, p: client.get(u, params=p),
        url=url,
        params=params,
    )
    return resp.text


async def fetch_bytes(url: str, *, max_bytes: int | None = None) -> bytes:
    """GET retournant des bytes bruts (CSV, XLSX, etc.) avec limite de taille.

    Args:
        url: URL du fichier a telecharger.
        max_bytes: Taille maximale en octets (defaut: DOWNLOAD_MAX_BYTES).

    Raises:
        RuntimeError: Si le fichier depasse la limite de taille.
    """
    limit = max_bytes or DOWNLOAD_MAX_BYTES
    client = await get_client()

    async with client.stream("GET", url) as resp:
        resp.raise_for_status()

        # Verifier Content-Length si disponible
        content_length = resp.headers.get("content-length")
        if content_length and int(content_length) > limit:
            msg = f"Fichier trop volumineux ({int(content_length)} octets > {limit} octets max)"
            raise RuntimeError(msg)

        chunks: list[bytes] = []
        total = 0
        async for chunk in resp.aiter_bytes(chunk_size=65536):
            total += len(chunk)
            if total > limit:
                msg = f"Fichier trop volumineux (> {limit} octets max)"
                raise RuntimeError(msg)
            chunks.append(chunk)

    return b"".join(chunks)


async def close() -> None:
    global _client  # noqa: PLW0603
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
