"""Tests pour les nouveaux helpers (Retry-After, fetch_bytes, coords)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from helpers import http_client
from helpers.coords import lambert_to_wgs84, wgs84_to_lambert

# ── Retry-After sur 429 ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retry_after_on_429():
    """Verifie le respect du Retry-After sur une reponse 429."""
    error_resp = httpx.Response(
        status_code=429,
        headers={"Retry-After": "2"},
        request=httpx.Request("GET", "https://example.com"),
    )
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.raise_for_status = MagicMock()
    success_response.json.return_value = {"ok": True}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        side_effect=[
            httpx.HTTPStatusError("429", request=error_resp.request, response=error_resp),
            success_response,
        ]
    )
    mock_client.is_closed = False

    with (
        patch.object(http_client, "_client", mock_client),
        patch("helpers.http_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        result = await http_client.fetch_json("https://example.com/api")
        assert result["ok"] is True
        # Verifier que le sleep a ete appele avec le Retry-After
        mock_sleep.assert_awaited()
        assert mock_sleep.call_args[0][0] == 2.0


@pytest.mark.asyncio
async def test_retry_after_capped_at_60s():
    """Verifie que le Retry-After est plafonne a 60 secondes."""
    error_resp = httpx.Response(
        status_code=429,
        headers={"Retry-After": "120"},
        request=httpx.Request("GET", "https://example.com"),
    )
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.raise_for_status = MagicMock()
    success_response.json.return_value = {"ok": True}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(
        side_effect=[
            httpx.HTTPStatusError("429", request=error_resp.request, response=error_resp),
            success_response,
        ]
    )
    mock_client.is_closed = False

    with (
        patch.object(http_client, "_client", mock_client),
        patch("helpers.http_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        result = await http_client.fetch_json("https://example.com/api")
        assert result["ok"] is True
        # Devrait etre cap a 60s, pas 120s
        mock_sleep.assert_awaited()
        assert mock_sleep.call_args[0][0] == 60.0


# ── _get_retry_after ─────────────────────────────────────────────────


def test_get_retry_after_numeric():
    resp = httpx.Response(200, headers={"Retry-After": "5"}, request=httpx.Request("GET", "http://x.com"))
    assert http_client._get_retry_after(resp) == 5.0


def test_get_retry_after_missing():
    resp = httpx.Response(200, headers={}, request=httpx.Request("GET", "http://x.com"))
    assert http_client._get_retry_after(resp) is None


def test_get_retry_after_invalid():
    resp = httpx.Response(200, headers={"Retry-After": "not-a-number"}, request=httpx.Request("GET", "http://x.com"))
    assert http_client._get_retry_after(resp) is None


# ── Conversion de coordonnees ────────────────────────────────────────


def test_wgs84_to_lambert_montreal():
    """Convertit Montreal WGS84 -> Lambert MTQ (EPSG:32198)."""
    x, y = wgs84_to_lambert(-73.5673, 45.5017)
    # EPSG:32198 Quebec Lambert — Montreal est a X~-396000, Y~181000
    assert -500000 < x < -300000
    assert 100000 < y < 300000


def test_lambert_to_wgs84_montreal():
    """Convertit Montreal Lambert -> WGS84."""
    # Coordonnees Lambert pour Montreal (EPSG:32198)
    lon, lat = lambert_to_wgs84(-396122.0, 181374.0)
    # Devrait etre dans la zone du Quebec
    assert -80 < lon < -60
    assert 44 < lat < 62


def test_roundtrip_conversion():
    """Verifie la conversion aller-retour."""
    original_lon, original_lat = -73.5673, 45.5017
    x, y = wgs84_to_lambert(original_lon, original_lat)
    lon, lat = lambert_to_wgs84(x, y)
    assert abs(lon - original_lon) < 0.001
    assert abs(lat - original_lat) < 0.001
