"""Tests unitaires pour les outils géospatiaux IGO (mockés)."""

import json
from unittest.mock import AsyncMock, patch

import pytest


# ── list_geospatial_layers ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_geospatial_layers_wfs():
    mock_caps = {
        "total": 3,
        "layers": [
            {"name": "msp:casernes_incendie", "title": "Casernes d'incendie", "abstract": "Localisation des casernes"},
            {"name": "msp:postes_police", "title": "Postes de police", "abstract": ""},
            {"name": "mern:ecoles", "title": "Écoles du Québec", "abstract": "Établissements scolaires"},
        ],
    }
    with patch("tools.list_geospatial_layers.geo_api.get_wfs_capabilities", new_callable=AsyncMock, return_value=mock_caps):
        from tools.list_geospatial_layers import list_geospatial_layers

        result = json.loads(await list_geospatial_layers(service="wfs"))
        assert result["service"] == "WFS"
        assert result["total"] == 3


@pytest.mark.asyncio
async def test_list_geospatial_layers_wms():
    mock_caps = {"total": 1, "layers": [{"name": "carte_base", "title": "Carte de base", "abstract": ""}]}
    with patch("tools.list_geospatial_layers.geo_api.get_wms_capabilities", new_callable=AsyncMock, return_value=mock_caps):
        from tools.list_geospatial_layers import list_geospatial_layers

        result = json.loads(await list_geospatial_layers(service="wms"))
        assert result["service"] == "WMS"
        assert result["total"] == 1


@pytest.mark.asyncio
async def test_list_geospatial_layers_with_query():
    mock_caps = {
        "total": 2,
        "layers": [
            {"name": "msp:casernes_incendie", "title": "Casernes d'incendie", "abstract": ""},
            {"name": "mern:ecoles", "title": "Écoles du Québec", "abstract": ""},
        ],
    }
    with patch("tools.list_geospatial_layers.geo_api.get_wfs_capabilities", new_callable=AsyncMock, return_value=mock_caps):
        from tools.list_geospatial_layers import list_geospatial_layers

        result = json.loads(await list_geospatial_layers(query="casernes"))
        assert result["total"] == 1
        assert result["layers"][0]["name"] == "msp:casernes_incendie"


@pytest.mark.asyncio
async def test_list_geospatial_layers_error():
    with patch("tools.list_geospatial_layers.geo_api.get_wfs_capabilities", new_callable=AsyncMock, side_effect=RuntimeError("timeout")):
        from tools.list_geospatial_layers import list_geospatial_layers

        result = json.loads(await list_geospatial_layers())
        assert "error" in result


# ── get_geospatial_features ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_geospatial_features():
    mock_result = {
        "features": [
            {
                "properties": {"nom": "Caserne 42", "municipalite": "Montréal"},
                "geometry": {"type": "Point", "coordinates": [-73.5673, 45.5017]},
            },
            {
                "properties": {"nom": "Caserne 15", "municipalite": "Laval"},
                "geometry": {"type": "Point", "coordinates": [-73.7500, 45.5833]},
            },
        ],
    }
    with patch("tools.get_geospatial_features.geo_api.get_features", new_callable=AsyncMock, return_value=mock_result):
        from tools.get_geospatial_features import get_geospatial_features

        result = json.loads(await get_geospatial_features(layer_name="msp:casernes_incendie"))
        assert result["total_returned"] == 2
        assert result["features"][0]["properties"]["nom"] == "Caserne 42"
        assert result["features"][0]["geometry_type"] == "Point"


@pytest.mark.asyncio
async def test_get_geospatial_features_error():
    with patch("tools.get_geospatial_features.geo_api.get_features", new_callable=AsyncMock, side_effect=RuntimeError("couche introuvable")):
        from tools.get_geospatial_features import get_geospatial_features

        result = json.loads(await get_geospatial_features(layer_name="inexistant"))
        assert "error" in result


# ── describe_geospatial_layer ────────────────────────────────────────

@pytest.mark.asyncio
async def test_describe_geospatial_layer():
    mock_xml = '<xsd:schema><xsd:element name="nom" type="xsd:string"/></xsd:schema>'
    with patch("tools.describe_geospatial_layer.geo_api.describe_feature_type", new_callable=AsyncMock, return_value=mock_xml):
        from tools.describe_geospatial_layer import describe_geospatial_layer

        result = json.loads(await describe_geospatial_layer(layer_name="msp:casernes_incendie"))
        assert result["layer"] == "msp:casernes_incendie"
        assert "xsd:schema" in result["schema_xml"]


@pytest.mark.asyncio
async def test_describe_geospatial_layer_error():
    with patch("tools.describe_geospatial_layer.geo_api.describe_feature_type", new_callable=AsyncMock, side_effect=RuntimeError("erreur")):
        from tools.describe_geospatial_layer import describe_geospatial_layer

        result = json.loads(await describe_geospatial_layer(layer_name="inexistant"))
        assert "error" in result


# ── get_map_url ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_map_url():
    from tools.get_map_url import get_map_url

    result = json.loads(await get_map_url(layers="msp:casernes_incendie", bbox="-73.7,45.4,-73.4,45.6"))
    assert "map_url" in result
    assert "msp:casernes_incendie" in result["map_url"]
    assert "GetMap" in result["map_url"]
    assert result["bbox"] == "-73.7,45.4,-73.4,45.6"


@pytest.mark.asyncio
async def test_get_map_url_custom_size():
    from tools.get_map_url import get_map_url

    result = json.loads(await get_map_url(layers="test", bbox="0,0,1,1", width=1024, height=768))
    assert "width=1024" in result["map_url"]
    assert "height=768" in result["map_url"]
