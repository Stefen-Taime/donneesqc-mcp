"""Tests unitaires pour les 12 nouveaux outils MCP (mockes)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

# ── download_resource ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_download_resource_csv():
    mock_res = {
        "id": "r1",
        "name": "data.csv",
        "url": "https://example.com/data.csv",
        "format": "CSV",
    }
    csv_content = b"nom,age\nAlice,30\nBob,25\n"

    with (
        patch(
            "tools.download_resource.ckan_api.resource_show",
            new_callable=AsyncMock,
            return_value=mock_res,
        ),
        patch(
            "tools.download_resource.fetch_bytes",
            new_callable=AsyncMock,
            return_value=csv_content,
        ),
    ):
        from tools.download_resource import download_resource

        result = json.loads(await download_resource(resource_id="r1"))
        assert result["format"] == "CSV"
        assert result["total_returned"] == 2
        assert result["fields"] == ["nom", "age"]
        assert result["records"][0]["nom"] == "Alice"


@pytest.mark.asyncio
async def test_download_resource_json():
    mock_res = {
        "id": "r1",
        "name": "data.json",
        "url": "https://example.com/data.json",
        "format": "JSON",
    }
    json_content = b'[{"nom": "Alice"}, {"nom": "Bob"}]'

    with (
        patch(
            "tools.download_resource.ckan_api.resource_show",
            new_callable=AsyncMock,
            return_value=mock_res,
        ),
        patch(
            "tools.download_resource.fetch_bytes",
            new_callable=AsyncMock,
            return_value=json_content,
        ),
    ):
        from tools.download_resource import download_resource

        result = json.loads(await download_resource(resource_id="r1"))
        assert result["format"] == "JSON"
        assert result["returned"] == 2


@pytest.mark.asyncio
async def test_download_resource_geojson():
    mock_res = {
        "id": "r1",
        "name": "geo.geojson",
        "url": "https://example.com/geo.geojson",
        "format": "GeoJSON",
    }
    geojson_content = (
        b'{"type": "FeatureCollection", "features": [{"type": "Feature",'
        b' "properties": {"nom": "A"}, "geometry": {"type": "Point", "coordinates": [0, 0]}}]}'
    )

    with (
        patch(
            "tools.download_resource.ckan_api.resource_show",
            new_callable=AsyncMock,
            return_value=mock_res,
        ),
        patch(
            "tools.download_resource.fetch_bytes",
            new_callable=AsyncMock,
            return_value=geojson_content,
        ),
    ):
        from tools.download_resource import download_resource

        result = json.loads(await download_resource(resource_id="r1"))
        assert result["format"] == "GeoJSON"
        assert result["total_features"] == 1


@pytest.mark.asyncio
async def test_download_resource_unsupported_format():
    mock_res = {
        "id": "r1",
        "name": "data.pdf",
        "url": "https://example.com/data.pdf",
        "format": "PDF",
    }

    with patch(
        "tools.download_resource.ckan_api.resource_show",
        new_callable=AsyncMock,
        return_value=mock_res,
    ):
        from tools.download_resource import download_resource

        result = json.loads(await download_resource(resource_id="r1"))
        assert "error" in result
        assert "pdf" in result["error"].lower()


@pytest.mark.asyncio
async def test_download_resource_error():
    with patch(
        "tools.download_resource.ckan_api.resource_show",
        new_callable=AsyncMock,
        side_effect=RuntimeError("not found"),
    ):
        from tools.download_resource import download_resource

        result = json.loads(await download_resource(resource_id="invalid"))
        assert "error" in result


# ── preview_resource ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_preview_resource():
    mock_result = {
        "total": 500,
        "fields": [
            {"id": "_id", "type": "int"},
            {"id": "nom", "type": "text"},
            {"id": "age", "type": "int4"},
        ],
        "records": [
            {"_id": 1, "nom": "Alice", "age": 30},
            {"_id": 2, "nom": "Bob", "age": 25},
        ],
    }

    with patch(
        "tools.preview_resource.ckan_api.datastore_search",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from tools.preview_resource import preview_resource

        result = json.loads(await preview_resource(resource_id="r1"))
        assert result["total_rows"] == 500
        assert result["num_columns"] == 2  # _id excluded
        assert result["schema"][0]["name"] == "nom"
        assert result["schema"][0]["type"] == "text"
        assert len(result["sample_rows"]) == 2
        assert "_id" not in result["sample_rows"][0]


@pytest.mark.asyncio
async def test_preview_resource_error():
    with patch(
        "tools.preview_resource.ckan_api.datastore_search",
        new_callable=AsyncMock,
        side_effect=RuntimeError("not in datastore"),
    ):
        from tools.preview_resource import preview_resource

        result = json.loads(await preview_resource(resource_id="invalid"))
        assert "error" in result


# ── find_and_query ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_find_and_query_success():
    mock_search = {
        "count": 1,
        "results": [
            {
                "id": "pkg1",
                "name": "pistes-cyclables",
                "title": "Pistes cyclables",
                "organization": {"title": "Ville de Montreal"},
                "resources": [
                    {
                        "id": "res1",
                        "name": "data.csv",
                        "format": "CSV",
                        "datastore_active": True,
                    },
                ],
            },
        ],
    }
    mock_data = {
        "total": 100,
        "fields": [{"id": "_id"}, {"id": "nom"}, {"id": "longueur"}],
        "records": [{"nom": "Piste A", "longueur": 5.2}],
    }

    with (
        patch(
            "tools.find_and_query.ckan_api.package_search",
            new_callable=AsyncMock,
            return_value=mock_search,
        ),
        patch(
            "tools.find_and_query.ckan_api.datastore_search",
            new_callable=AsyncMock,
            return_value=mock_data,
        ),
    ):
        from tools.find_and_query import find_and_query

        result = json.loads(await find_and_query(query="pistes cyclables"))
        assert result["dataset"]["title"] == "Pistes cyclables"
        assert result["resource"]["id"] == "res1"
        assert result["data"]["total"] == 100


@pytest.mark.asyncio
async def test_find_and_query_no_results():
    mock_search = {"count": 0, "results": []}

    with patch(
        "tools.find_and_query.ckan_api.package_search",
        new_callable=AsyncMock,
        return_value=mock_search,
    ):
        from tools.find_and_query import find_and_query

        result = json.loads(await find_and_query(query="inexistant"))
        assert "error" in result


@pytest.mark.asyncio
async def test_find_and_query_no_datastore():
    mock_search = {
        "count": 1,
        "results": [
            {
                "id": "pkg1",
                "name": "test",
                "title": "Test",
                "resources": [
                    {"id": "res1", "format": "PDF", "datastore_active": False},
                ],
            },
        ],
    }

    with patch(
        "tools.find_and_query.ckan_api.package_search",
        new_callable=AsyncMock,
        return_value=mock_search,
    ):
        from tools.find_and_query import find_and_query

        result = json.loads(await find_and_query(query="test"))
        assert "note" in result


# ── suggest_sql ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_sql():
    mock_result = {
        "fields": [
            {"id": "_id", "type": "int"},
            {"id": "ville", "type": "text"},
            {"id": "population", "type": "int4"},
            {"id": "date_maj", "type": "timestamp"},
        ],
        "records": [],
    }

    with patch(
        "tools.suggest_sql.ckan_api.datastore_search",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from tools.suggest_sql import suggest_sql

        result = json.loads(await suggest_sql(resource_id="r1"))
        assert len(result["schema"]) == 3  # _id excluded
        assert len(result["suggestions"]) >= 3
        # Verifier qu'on a un apercu, un count, et un group by
        names = [s["name"] for s in result["suggestions"]]
        assert "Apercu des donnees" in names
        assert "Nombre total de lignes" in names


@pytest.mark.asyncio
async def test_suggest_sql_error():
    with patch(
        "tools.suggest_sql.ckan_api.datastore_search",
        new_callable=AsyncMock,
        side_effect=RuntimeError("not found"),
    ):
        from tools.suggest_sql import suggest_sql

        result = json.loads(await suggest_sql(resource_id="invalid"))
        assert "error" in result


# ── compare_datasets ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_compare_datasets():
    mock_pkg1 = {
        "id": "p1",
        "name": "dataset-1",
        "title": "Dataset 1",
        "organization": {"title": "Org A"},
        "license_title": "CC-BY-4.0",
        "tags": [{"name": "transport"}, {"name": "velo"}],
        "metadata_created": "2020-01-01",
        "metadata_modified": "2024-01-01",
        "resources": [{"format": "CSV", "datastore_active": True, "id": "r1"}],
    }
    mock_pkg2 = {
        "id": "p2",
        "name": "dataset-2",
        "title": "Dataset 2",
        "organization": {"title": "Org B"},
        "license_title": "CC-BY-4.0",
        "tags": [{"name": "transport"}, {"name": "bus"}],
        "metadata_created": "2021-01-01",
        "metadata_modified": "2024-06-01",
        "resources": [{"format": "JSON", "datastore_active": False}],
    }

    with patch(
        "tools.compare_datasets.ckan_api.package_show",
        new_callable=AsyncMock,
        side_effect=[mock_pkg1, mock_pkg2],
    ):
        from tools.compare_datasets import compare_datasets

        result = json.loads(await compare_datasets("dataset-1", "dataset-2"))
        assert result["dataset_1"]["title"] == "Dataset 1"
        assert result["dataset_2"]["title"] == "Dataset 2"
        assert result["comparison"]["same_license"] is True
        assert result["comparison"]["same_organization"] is False
        assert "transport" in result["comparison"]["tags"]["common"]
        assert "velo" in result["comparison"]["tags"]["only_in_dataset_1"]
        assert "bus" in result["comparison"]["tags"]["only_in_dataset_2"]


@pytest.mark.asyncio
async def test_compare_datasets_error():
    with patch(
        "tools.compare_datasets.ckan_api.package_show",
        new_callable=AsyncMock,
        side_effect=RuntimeError("not found"),
    ):
        from tools.compare_datasets import compare_datasets

        result = json.loads(await compare_datasets("invalid1", "invalid2"))
        assert "error" in result


# ── auto_detect_resource ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_auto_detect_resource_by_slug():
    mock_pkg = {
        "id": "p1",
        "name": "pistes-cyclables",
        "title": "Pistes cyclables",
        "resources": [
            {
                "id": "r1", "name": "data.csv", "format": "CSV",
                "datastore_active": True, "url": "http://a.com/1",
                "last_modified": "2024-01-01",
            },
            {
                "id": "r2", "name": "data.json", "format": "JSON",
                "datastore_active": False, "url": "http://a.com/2",
                "last_modified": None,
            },
        ],
    }

    with patch(
        "tools.auto_detect_resource.ckan_api.package_show",
        new_callable=AsyncMock,
        return_value=mock_pkg,
    ):
        from tools.auto_detect_resource import auto_detect_resource

        result = json.loads(await auto_detect_resource(dataset_name="pistes-cyclables"))
        assert result["recommended_resource"]["id"] == "r1"
        assert result["recommended_resource"]["datastore_active"] is True


@pytest.mark.asyncio
async def test_auto_detect_resource_by_search():
    mock_search = {
        "count": 1,
        "results": [
            {
                "id": "p1",
                "name": "arbres",
                "title": "Arbres",
                "resources": [
                    {
                        "id": "r1", "name": "data.json", "format": "JSON",
                        "datastore_active": True, "url": "http://a.com/1",
                        "last_modified": "2024-01-01",
                    },
                ],
            },
        ],
    }

    with (
        patch(
            "tools.auto_detect_resource.ckan_api.package_show",
            new_callable=AsyncMock,
            side_effect=RuntimeError("not found"),
        ),
        patch(
            "tools.auto_detect_resource.ckan_api.package_search",
            new_callable=AsyncMock,
            return_value=mock_search,
        ),
    ):
        from tools.auto_detect_resource import auto_detect_resource

        result = json.loads(await auto_detect_resource(dataset_name="arbres"))
        assert result["recommended_resource"]["id"] == "r1"


@pytest.mark.asyncio
async def test_auto_detect_resource_not_found():
    mock_search = {"count": 0, "results": []}

    with (
        patch(
            "tools.auto_detect_resource.ckan_api.package_show",
            new_callable=AsyncMock,
            side_effect=RuntimeError("not found"),
        ),
        patch(
            "tools.auto_detect_resource.ckan_api.package_search",
            new_callable=AsyncMock,
            return_value=mock_search,
        ),
    ):
        from tools.auto_detect_resource import auto_detect_resource

        result = json.loads(await auto_detect_resource(dataset_name="inexistant"))
        assert "error" in result


# ── geocode ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_geocode():
    mock_response = {
        "features": [
            {
                "properties": {
                    "recherche": "900 Boulevard Rene-Levesque, Quebec",
                    "municipalite": "Quebec",
                    "mrc": "Quebec",
                    "region": "Capitale-Nationale",
                    "score": 95.5,
                },
                "geometry": {"type": "Point", "coordinates": [-71.2180, 46.8066]},
            },
        ],
    }

    with patch(
        "tools.geocode.fetch_json",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from tools.geocode import geocode

        result = json.loads(await geocode(address="900 Boulevard Rene-Levesque, Quebec"))
        assert result["total"] == 1
        assert result["results"][0]["municipality"] == "Quebec"
        assert result["results"][0]["longitude"] == -71.2180


@pytest.mark.asyncio
async def test_geocode_error():
    with patch(
        "tools.geocode.fetch_json",
        new_callable=AsyncMock,
        side_effect=RuntimeError("service unavailable"),
    ):
        from tools.geocode import geocode

        result = json.loads(await geocode(address="invalid"))
        assert "error" in result


# ── reverse_geocode ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reverse_geocode():
    mock_response = {
        "features": [
            {
                "properties": {
                    "recherche": "1000 Rue de la Gauchetiere O, Montreal",
                    "numero": "1000",
                    "rue": "Rue de la Gauchetiere O",
                    "municipalite": "Montreal",
                    "mrc": "Montreal",
                    "region": "Montreal",
                    "codePostal": "H3B 4W5",
                    "distance": 12.5,
                },
                "geometry": {"type": "Point", "coordinates": [-73.5673, 45.5017]},
            },
        ],
    }

    with patch(
        "tools.reverse_geocode.fetch_json",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        from tools.reverse_geocode import reverse_geocode

        result = json.loads(await reverse_geocode(latitude=45.5017, longitude=-73.5673))
        assert result["total"] == 1
        assert result["results"][0]["municipality"] == "Montreal"
        assert result["results"][0]["postal_code"] == "H3B 4W5"


@pytest.mark.asyncio
async def test_reverse_geocode_error():
    with patch(
        "tools.reverse_geocode.fetch_json",
        new_callable=AsyncMock,
        side_effect=RuntimeError("service unavailable"),
    ):
        from tools.reverse_geocode import reverse_geocode

        result = json.loads(await reverse_geocode(latitude=0.0, longitude=0.0))
        assert "error" in result


# ── convert_coordinates ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_convert_coordinates_wgs84_to_lambert():
    from tools.convert_coordinates import convert_coordinates

    result = json.loads(
        await convert_coordinates(x=-73.5673, y=45.5017, from_crs="EPSG:4326", to_crs="EPSG:32198")
    )
    assert "output" in result
    assert result["input"]["crs"] == "EPSG:4326 (WGS84)"
    assert result["output"]["crs"] == "EPSG:32198 (Lambert MTQ)"
    # Verifier que les valeurs sont raisonnables pour Montreal
    assert result["output"]["x"] != 0
    assert result["output"]["y"] != 0


@pytest.mark.asyncio
async def test_convert_coordinates_lambert_to_wgs84():
    from tools.convert_coordinates import convert_coordinates

    # Coordonnees Lambert (EPSG:32198) pour Montreal : X~-396122, Y~181374
    result = json.loads(
        await convert_coordinates(x=-396122.0, y=181374.0, from_crs="EPSG:32198", to_crs="EPSG:4326")
    )
    assert "output" in result
    assert result["output"]["crs"] == "EPSG:4326 (WGS84)"
    # Longitude devrait etre negative (Quebec)
    assert result["output"]["longitude"] < 0
    assert 44 < result["output"]["latitude"] < 62


@pytest.mark.asyncio
async def test_convert_coordinates_same_crs():
    from tools.convert_coordinates import convert_coordinates

    result = json.loads(
        await convert_coordinates(x=0, y=0, from_crs="EPSG:4326", to_crs="EPSG:4326")
    )
    assert "error" in result


@pytest.mark.asyncio
async def test_convert_coordinates_invalid_crs():
    from tools.convert_coordinates import convert_coordinates

    result = json.loads(
        await convert_coordinates(x=0, y=0, from_crs="EPSG:9999", to_crs="EPSG:4326")
    )
    assert "error" in result


# ── spatial_intersection ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_spatial_intersection():
    mock_result = {
        "features": [
            {
                "properties": {"NOM": "Montreal", "CODE": "06", "POPULATION": 2000000},
                "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
            },
        ],
    }

    with patch(
        "tools.spatial_intersection.geo_api.get_features",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        from tools.spatial_intersection import spatial_intersection

        result = json.loads(
            await spatial_intersection(latitude=45.5017, longitude=-73.5673, layer_type="regions_administratives")
        )
        assert result["total"] == 1
        assert result["results"][0]["NOM"] == "Montreal"


@pytest.mark.asyncio
async def test_spatial_intersection_invalid_layer():
    from tools.spatial_intersection import spatial_intersection

    result = json.loads(
        await spatial_intersection(latitude=45.5, longitude=-73.5, layer_type="invalid")
    )
    assert "error" in result
    assert "valid_types" in result


@pytest.mark.asyncio
async def test_spatial_intersection_no_result():
    mock_empty = {"features": []}

    with patch(
        "tools.spatial_intersection.geo_api.get_features",
        new_callable=AsyncMock,
        return_value=mock_empty,
    ):
        from tools.spatial_intersection import spatial_intersection

        result = json.loads(
            await spatial_intersection(latitude=0.0, longitude=0.0, layer_type="regions_administratives")
        )
        assert result["result"] is None or result["total"] == 0


# ── get_version ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_version():
    from tools.get_version import get_version

    result = json.loads(await get_version())
    assert result["name"] == "donneesqc-mcp"
    assert "version" in result
    assert "python_version" in result
    assert result["capabilities"]["donnees_quebec"] is True
    assert result["capabilities"]["geocoding"] is True


# ── list_tools_with_examples ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_tools_with_examples():
    from tools.list_tools_with_examples import list_tools_with_examples

    result = json.loads(await list_tools_with_examples())
    assert result["total_tools"] > 20
    assert "categories" in result
    assert "Recherche" in result["categories"]
    assert "Geospatial" in result["categories"]
    assert "Intelligence" in result["categories"]


@pytest.mark.asyncio
async def test_list_tools_with_examples_filter():
    from tools.list_tools_with_examples import list_tools_with_examples

    result = json.loads(await list_tools_with_examples(category="Geospatial"))
    assert result["total_tools"] >= 4
    # Toutes les categories devraient etre Geospatial
    for cat_tools in result["categories"].values():
        for tool in cat_tools:
            assert tool["tool"] in [
                "geocode", "reverse_geocode", "convert_coordinates",
                "spatial_intersection", "list_geospatial_layers",
                "get_geospatial_features", "describe_geospatial_layer", "get_map_url",
            ]
