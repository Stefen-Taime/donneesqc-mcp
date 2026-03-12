"""Tests pour les helpers CKAN API (Données Québec)."""

import pytest

from helpers import ckan_api
from helpers.config import DQ_API_URL


@pytest.mark.asyncio
async def test_package_search():
    """Vérifie que la recherche retourne des résultats."""
    result = await ckan_api.package_search(DQ_API_URL, query="transport", rows=5)
    assert "count" in result
    assert result["count"] > 0
    assert len(result["results"]) <= 5


@pytest.mark.asyncio
async def test_package_search_by_organization():
    """Vérifie le filtrage par organisation."""
    result = await ckan_api.package_search(DQ_API_URL, query="*:*", rows=3, fq="organization:ville-de-montreal")
    assert result["count"] > 0
    for pkg in result["results"]:
        assert pkg["organization"]["name"] == "ville-de-montreal"


@pytest.mark.asyncio
async def test_organization_list():
    """Vérifie que la liste des organisations est non vide."""
    orgs = await ckan_api.organization_list(DQ_API_URL, all_fields=True)
    assert len(orgs) > 0
    assert "name" in orgs[0]


@pytest.mark.asyncio
async def test_site_read():
    """Vérifie que le portail est en ligne via une recherche minimale."""
    # site_read retourne 400 sur donneesquebec.ca, on vérifie la connectivité autrement
    result = await ckan_api.package_search(DQ_API_URL, query="*:*", rows=0)
    assert result["count"] > 0


@pytest.mark.asyncio
async def test_tag_list():
    """Vérifie que des tags existent."""
    tags = await ckan_api.tag_list(DQ_API_URL)
    assert len(tags) > 0
