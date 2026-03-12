"""Fixtures partagées pour les tests."""

import pytest

from helpers import http_client


@pytest.fixture(autouse=True)
async def _cleanup_http_client():
    """Ferme le client HTTP après chaque test pour éviter les erreurs d'event loop."""
    yield
    await http_client.close()
