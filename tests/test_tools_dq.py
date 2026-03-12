"""Tests unitaires pour les outils Données Québec (mockés)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

# ── search_datasets ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_datasets_returns_results():
    mock_result = {
        "count": 2,
        "results": [
            {
                "id": "abc-123",
                "name": "actes-criminels",
                "title": "Actes criminels",
                "notes": "Description des actes criminels",
                "organization": {"title": "Ville de Montréal"},
                "tags": [{"name": "criminalité"}, {"name": "sécurité"}],
                "num_resources": 3,
                "metadata_modified": "2024-01-01",
            },
        ],
    }
    with patch(
        "tools.search_datasets.ckan_api.package_search",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from tools.search_datasets import search_datasets

        result = json.loads(await search_datasets(query="criminalité"))
        assert result["count"] == 2
        assert len(result["datasets"]) == 1
        assert result["datasets"][0]["name"] == "actes-criminels"
        assert result["datasets"][0]["tags"] == ["criminalité", "sécurité"]


@pytest.mark.asyncio
async def test_search_datasets_with_filters():
    mock_result = {"count": 1, "results": []}
    with patch(
        "tools.search_datasets.ckan_api.package_search",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as mock:
        from tools.search_datasets import search_datasets

        await search_datasets(
            query="transport",
            organization="ville-de-montreal",
            tags="bus,métro",
        )
        call_kwargs = mock.call_args
        assert "organization:ville-de-montreal" in call_kwargs.kwargs.get(
            "fq",
            call_kwargs[1].get("fq", ""),
        )


@pytest.mark.asyncio
async def test_search_datasets_page_size_clamped():
    mock_result = {"count": 0, "results": []}
    with patch(
        "tools.search_datasets.ckan_api.package_search",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as mock:
        from tools.search_datasets import search_datasets

        await search_datasets(query="test", page_size=500)
        # page_size devrait être clampé à 100
        assert mock.call_args[1]["rows"] == 100


@pytest.mark.asyncio
async def test_search_datasets_error_returns_json():
    with patch(
        "tools.search_datasets.ckan_api.package_search",
        new_callable=AsyncMock,
        side_effect=RuntimeError("timeout"),
    ):
        from tools.search_datasets import search_datasets

        result = json.loads(await search_datasets(query="test"))
        assert "error" in result


# ── get_dataset_info ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_dataset_info_returns_metadata():
    mock_pkg = {
        "id": "abc-123",
        "name": "actes-criminels",
        "title": "Actes criminels",
        "notes": "Description",
        "organization": {"title": "SPVM"},
        "license_title": "CC-BY-4.0",
        "tags": [{"name": "crime"}],
        "metadata_created": "2020-01-01",
        "metadata_modified": "2024-06-01",
        "resources": [
            {
                "id": "res-1",
                "name": "données 2024",
                "format": "CSV",
                "size": 1024,
                "url": "https://example.com/data.csv",
                "datastore_active": True,
                "last_modified": "2024-06-01",
            }
        ],
    }
    with patch(
        "tools.get_dataset_info.ckan_api.package_show",
        new_callable=AsyncMock,
        return_value=mock_pkg,
    ):
        from tools.get_dataset_info import get_dataset_info

        result = json.loads(await get_dataset_info("actes-criminels"))
        assert result["title"] == "Actes criminels"
        assert result["num_resources"] == 1
        assert result["resources"][0]["datastore_active"] is True


@pytest.mark.asyncio
async def test_get_dataset_info_error():
    with patch(
        "tools.get_dataset_info.ckan_api.package_show",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Not found"),
    ):
        from tools.get_dataset_info import get_dataset_info

        result = json.loads(await get_dataset_info("inexistant"))
        assert "error" in result


# ── list_dataset_resources ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_dataset_resources():
    mock_pkg = {
        "title": "Actes criminels",
        "resources": [
            {
                "id": "r1",
                "name": "2024.csv",
                "format": "CSV",
                "size": 500,
                "datastore_active": True,
                "url": "https://x.com/1",
                "last_modified": "2024-01-01",
            },
            {
                "id": "r2",
                "name": "2023.csv",
                "format": "CSV",
                "size": 400,
                "datastore_active": False,
                "url": "https://x.com/2",
                "last_modified": "2023-01-01",
            },
        ],
    }
    with patch(
        "tools.list_dataset_resources.ckan_api.package_show",
        new_callable=AsyncMock,
        return_value=mock_pkg,
    ):
        from tools.list_dataset_resources import list_dataset_resources

        result = json.loads(await list_dataset_resources("actes-criminels"))
        assert result["total_resources"] == 2
        assert result["resources"][0]["datastore_active"] is True


# ── get_resource_info ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_resource_info():
    mock_res = {
        "id": "r1",
        "name": "data.csv",
        "description": "Fichier principal",
        "format": "CSV",
        "mimetype": "text/csv",
        "size": 2048,
        "url": "https://example.com/data.csv",
        "datastore_active": True,
        "package_id": "pkg-1",
        "created": "2020-01-01",
        "last_modified": "2024-01-01",
    }
    with patch(
        "tools.get_resource_info.ckan_api.resource_show",
        new_callable=AsyncMock,
        return_value=mock_res,
    ):
        from tools.get_resource_info import get_resource_info

        result = json.loads(await get_resource_info("r1"))
        assert result["format"] == "CSV"
        assert result["datastore_active"] is True


# ── query_resource_data ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_query_resource_data():
    mock_result = {
        "total": 100,
        "fields": [{"id": "_id"}, {"id": "ville"}, {"id": "population"}],
        "records": [{"ville": "Montréal", "population": 1700000}],
    }
    with patch(
        "tools.query_resource_data.ckan_api.datastore_search",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from tools.query_resource_data import query_resource_data

        result = json.loads(await query_resource_data(resource_id="r1"))
        assert result["total"] == 100
        assert "_id" not in result["fields"]
        assert result["records"][0]["ville"] == "Montréal"


@pytest.mark.asyncio
async def test_query_resource_data_invalid_filters():
    from tools.query_resource_data import query_resource_data

    result = json.loads(
        await query_resource_data(resource_id="r1", filters="pas du json"),
    )
    assert "error" in result
    assert "JSON" in result["error"]


# ── query_resource_sql ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_query_resource_sql():
    mock_result = {
        "fields": [{"id": "ville"}, {"id": "total"}],
        "records": [{"ville": "Québec", "total": 42}],
        "sql": 'SELECT ville, COUNT(*) as total FROM "r1" GROUP BY ville',
    }
    with patch(
        "tools.query_resource_sql.ckan_api.datastore_search_sql",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from tools.query_resource_sql import query_resource_sql

        result = json.loads(
            await query_resource_sql(
                sql='SELECT ville, COUNT(*) as total FROM "r1" GROUP BY ville',
            )
        )
        assert result["records"][0]["total"] == 42


# ── list_organizations ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_organizations():
    mock_orgs = [
        {
            "name": "ville-de-montreal",
            "display_name": "Ville de Montréal",
            "package_count": 200,
            "description": "",
        },
        {
            "name": "msp",
            "display_name": "Min. Sécurité publique",
            "package_count": 50,
            "description": "",
        },
    ]
    with patch(
        "tools.list_organizations.ckan_api.organization_list",
        new_callable=AsyncMock,
        return_value=mock_orgs,
    ):
        from tools.list_organizations import list_organizations

        result = json.loads(await list_organizations())
        assert result["total"] == 2
        # Triées par package_count desc
        assert result["organizations"][0]["id"] == "ville-de-montreal"


@pytest.mark.asyncio
async def test_list_organizations_with_filter():
    mock_orgs = [
        {
            "name": "ville-de-montreal",
            "display_name": "Ville de Montréal",
            "package_count": 200,
            "description": "",
        },
        {
            "name": "msp",
            "display_name": "Min. Sécurité publique",
            "package_count": 50,
            "description": "",
        },
    ]
    with patch(
        "tools.list_organizations.ckan_api.organization_list",
        new_callable=AsyncMock,
        return_value=mock_orgs,
    ):
        from tools.list_organizations import list_organizations

        result = json.loads(await list_organizations(query="montreal"))
        assert result["total"] == 1


# ── get_organization_info ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_organization_info():
    mock_org = {
        "name": "ville-de-montreal",
        "display_name": "Ville de Montréal",
        "description": "Municipalité",
        "image_display_url": "https://example.com/logo.png",
        "package_count": 200,
        "created": "2015-01-01",
    }
    with patch(
        "tools.get_organization_info.ckan_api.organization_show",
        new_callable=AsyncMock,
        return_value=mock_org,
    ):
        from tools.get_organization_info import get_organization_info

        result = json.loads(await get_organization_info("ville-de-montreal"))
        assert result["title"] == "Ville de Montréal"
        assert result["num_datasets"] == 200


# ── get_catalog_stats ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_catalog_stats():
    mock_search = {"count": 5000}
    mock_orgs = [
        {"display_name": "Ville de Montréal", "package_count": 200},
        {"display_name": "MSP", "package_count": 50},
    ]
    with (
        patch(
            "tools.get_catalog_stats.ckan_api.package_search",
            new_callable=AsyncMock,
            return_value=mock_search,
        ),
        patch(
            "tools.get_catalog_stats.ckan_api.organization_list",
            new_callable=AsyncMock,
            return_value=mock_orgs,
        ),
    ):
        from tools.get_catalog_stats import get_catalog_stats

        result = json.loads(await get_catalog_stats())
        assert result["total_datasets"] == 5000
        assert result["total_organizations"] == 2
        assert result["top_organizations"][0]["name"] == "Ville de Montréal"
