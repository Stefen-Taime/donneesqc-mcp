"""Tests unitaires pour les outils Ville de Montréal (mockés)."""

import json
from unittest.mock import AsyncMock, patch

import pytest


# ── search_montreal_datasets ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_montreal_datasets():
    mock_result = {
        "count": 15,
        "results": [
            {
                "id": "mtl-001",
                "name": "pistes-cyclables",
                "title": "Réseau cyclable",
                "notes": "Pistes cyclables de la Ville de Montréal",
                "organization": {"title": "Ville de Montréal"},
                "num_resources": 2,
                "metadata_modified": "2024-05-01",
            },
        ],
    }
    with patch("tools.search_montreal_datasets.ckan_api.package_search", new_callable=AsyncMock, return_value=mock_result):
        from tools.search_montreal_datasets import search_montreal_datasets

        result = json.loads(await search_montreal_datasets(query="pistes cyclables"))
        assert result["count"] == 15
        assert result["datasets"][0]["name"] == "pistes-cyclables"
        assert "donnees.montreal.ca" in result["datasets"][0]["url"]


@pytest.mark.asyncio
async def test_search_montreal_datasets_pagination():
    mock_result = {"count": 50, "results": []}
    with patch("tools.search_montreal_datasets.ckan_api.package_search", new_callable=AsyncMock, return_value=mock_result) as mock:
        from tools.search_montreal_datasets import search_montreal_datasets

        await search_montreal_datasets(query="arbres", page=3, page_size=10)
        assert mock.call_args[1]["start"] == 20  # (3-1) * 10
        assert mock.call_args[1]["rows"] == 10


@pytest.mark.asyncio
async def test_search_montreal_datasets_error():
    with patch("tools.search_montreal_datasets.ckan_api.package_search", new_callable=AsyncMock, side_effect=RuntimeError("connexion refusée")):
        from tools.search_montreal_datasets import search_montreal_datasets

        result = json.loads(await search_montreal_datasets(query="test"))
        assert "error" in result


# ── query_montreal_data ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_query_montreal_data():
    mock_result = {
        "total": 500,
        "fields": [{"id": "_id"}, {"id": "ARROND"}, {"id": "NB_CRIMES"}],
        "records": [{"ARROND": "Le Plateau-Mont-Royal", "NB_CRIMES": 120}],
    }
    with patch("tools.query_montreal_data.ckan_api.datastore_search", new_callable=AsyncMock, return_value=mock_result):
        from tools.query_montreal_data import query_montreal_data

        result = json.loads(await query_montreal_data(resource_id="mtl-r1"))
        assert result["total"] == 500
        assert "_id" not in result["fields"]
        assert result["records"][0]["ARROND"] == "Le Plateau-Mont-Royal"


@pytest.mark.asyncio
async def test_query_montreal_data_with_filters():
    mock_result = {"total": 10, "fields": [{"id": "ARROND"}], "records": []}
    with patch("tools.query_montreal_data.ckan_api.datastore_search", new_callable=AsyncMock, return_value=mock_result) as mock:
        from tools.query_montreal_data import query_montreal_data

        await query_montreal_data(resource_id="r1", filters='{"ARROND": "Rosemont"}')
        assert mock.call_args[1]["filters"] == {"ARROND": "Rosemont"}


@pytest.mark.asyncio
async def test_query_montreal_data_invalid_filters():
    from tools.query_montreal_data import query_montreal_data

    result = json.loads(await query_montreal_data(resource_id="r1", filters="{invalide"))
    assert "error" in result
    assert "JSON" in result["error"]


# ── query_montreal_sql ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_query_montreal_sql():
    mock_result = {
        "fields": [{"id": "ARROND"}, {"id": "total"}],
        "records": [
            {"ARROND": "Ville-Marie", "total": 3500},
            {"ARROND": "Le Plateau-Mont-Royal", "total": 2100},
        ],
    }
    with patch("tools.query_montreal_sql.ckan_api.datastore_search_sql", new_callable=AsyncMock, return_value=mock_result):
        from tools.query_montreal_sql import query_montreal_sql

        result = json.loads(await query_montreal_sql(sql='SELECT "ARROND", COUNT(*) as total FROM "r1" GROUP BY "ARROND"'))
        assert len(result["records"]) == 2
        assert result["fields"] == ["ARROND", "total"]


@pytest.mark.asyncio
async def test_query_montreal_sql_error():
    with patch("tools.query_montreal_sql.ckan_api.datastore_search_sql", new_callable=AsyncMock, side_effect=RuntimeError("erreur SQL")):
        from tools.query_montreal_sql import query_montreal_sql

        result = json.loads(await query_montreal_sql(sql="INVALID SQL"))
        assert "error" in result
