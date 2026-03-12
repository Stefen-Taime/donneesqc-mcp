"""Tests unitaires pour le client HTTP (retry, backoff, erreurs)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from helpers import http_client


@pytest.mark.asyncio
async def test_fetch_json_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"success": True, "result": "ok"}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.is_closed = False

    with patch.object(http_client, "_client", mock_client):
        result = await http_client.fetch_json("https://example.com/api")
        assert result["success"] is True


@pytest.mark.asyncio
async def test_fetch_text_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    mock_response.text = "<xml>contenu</xml>"

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.is_closed = False

    with patch.object(http_client, "_client", mock_client):
        result = await http_client.fetch_text("https://example.com/wfs")
        assert "<xml>" in result


@pytest.mark.asyncio
async def test_fetch_json_retry_on_500():
    """Vérifie le retry sur erreur 500 avec succès au 2e essai."""
    error_response = httpx.Response(status_code=500, request=httpx.Request("GET", "https://example.com"))
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.raise_for_status = MagicMock()
    success_response.json.return_value = {"success": True}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[
        httpx.HTTPStatusError("500", request=error_response.request, response=error_response),
        success_response,
    ])
    mock_client.is_closed = False

    with patch.object(http_client, "_client", mock_client), patch("helpers.http_client.asyncio.sleep", new_callable=AsyncMock):
        result = await http_client.fetch_json("https://example.com/api")
        assert result["success"] is True
        assert mock_client.get.call_count == 2


@pytest.mark.asyncio
async def test_fetch_json_no_retry_on_404():
    """Vérifie qu'on ne retry PAS sur une erreur 4xx."""
    error_response = httpx.Response(status_code=404, request=httpx.Request("GET", "https://example.com"))

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.HTTPStatusError("404", request=error_response.request, response=error_response))
    mock_client.is_closed = False

    with patch.object(http_client, "_client", mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await http_client.fetch_json("https://example.com/api")
        # Un seul appel, pas de retry
        assert mock_client.get.call_count == 1


@pytest.mark.asyncio
async def test_fetch_json_all_retries_fail():
    """Vérifie l'exception finale après épuisement des retries."""
    error_response = httpx.Response(status_code=500, request=httpx.Request("GET", "https://example.com"))

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.HTTPStatusError("500", request=error_response.request, response=error_response))
    mock_client.is_closed = False

    with (
        patch.object(http_client, "_client", mock_client),
        patch("helpers.http_client.asyncio.sleep", new_callable=AsyncMock),
        patch.object(http_client, "HTTP_MAX_RETRIES", 3),
    ):
        with pytest.raises(RuntimeError, match="Échec après"):
            await http_client.fetch_json("https://example.com/api")


@pytest.mark.asyncio
async def test_fetch_json_retry_on_network_error():
    """Vérifie le retry sur erreur réseau."""
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.raise_for_status = MagicMock()
    success_response.json.return_value = {"ok": True}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[
        httpx.ConnectError("connexion refusée"),
        success_response,
    ])
    mock_client.is_closed = False

    with patch.object(http_client, "_client", mock_client), patch("helpers.http_client.asyncio.sleep", new_callable=AsyncMock):
        result = await http_client.fetch_json("https://example.com/api")
        assert result["ok"] is True


@pytest.mark.asyncio
async def test_close_client():
    mock_client = AsyncMock()
    mock_client.is_closed = False

    with patch.object(http_client, "_client", mock_client):
        await http_client.close()
        mock_client.aclose.assert_awaited_once()
