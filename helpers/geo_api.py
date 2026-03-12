"""Helper pour les services géospatiaux OGC du Québec (IGO).

WMS = images cartographiques, WFS = données vectorielles (GeoJSON).
"""

import logging
import time
from typing import Any
from xml.etree import ElementTree as ET

from helpers.config import GEO_WFS_URL, GEO_WMS_URL
from helpers.http_client import fetch_json, fetch_text

logger = logging.getLogger(__name__)

# Cache TTL pour les GetCapabilities (évite de re-télécharger le XML à chaque appel)
_CACHE_TTL_SECONDS = 300  # 5 minutes
_capabilities_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _get_cached(key: str) -> dict[str, Any] | None:
    """Retourne le résultat en cache si non expiré."""
    if key in _capabilities_cache:
        timestamp, data = _capabilities_cache[key]
        if time.monotonic() - timestamp < _CACHE_TTL_SECONDS:
            logger.debug("Cache hit pour %s", key)
            return data
        del _capabilities_cache[key]
    return None


def _set_cached(key: str, data: dict[str, Any]) -> None:
    """Met en cache un résultat GetCapabilities."""
    _capabilities_cache[key] = (time.monotonic(), data)


def clear_cache() -> None:
    """Vide le cache des capabilities (utile pour les tests)."""
    _capabilities_cache.clear()


async def get_wfs_capabilities() -> dict[str, Any]:
    """Récupère la liste des couches WFS (avec cache)."""
    cached = _get_cached("wfs")
    if cached is not None:
        return cached

    xml_text = await fetch_text(
        GEO_WFS_URL,
        params={"service": "WFS", "request": "GetCapabilities", "version": "2.0.0"},
    )
    result = _parse_capabilities(xml_text, "FeatureType")
    _set_cached("wfs", result)
    return result


async def get_wms_capabilities() -> dict[str, Any]:
    """Récupère la liste des couches WMS (avec cache)."""
    cached = _get_cached("wms")
    if cached is not None:
        return cached

    xml_text = await fetch_text(
        GEO_WMS_URL,
        params={"service": "WMS", "request": "GetCapabilities", "version": "1.3.0"},
    )
    result = _parse_capabilities(xml_text, "Layer")
    _set_cached("wms", result)
    return result


async def get_features(
    type_name: str,
    max_features: int = 100,
    bbox: str | None = None,
    cql_filter: str | None = None,
) -> dict[str, Any]:
    """Récupère les entités d'une couche WFS en GeoJSON."""
    params: dict[str, Any] = {
        "service": "WFS",
        "request": "GetFeature",
        "version": "2.0.0",
        "typeName": type_name,
        "count": min(max_features, 5000),
        "outputFormat": "application/json",
    }
    if bbox:
        params["bbox"] = bbox
    if cql_filter:
        params["CQL_FILTER"] = cql_filter
    return await fetch_json(GEO_WFS_URL, params=params)


async def describe_feature_type(type_name: str) -> str:
    """Décrit le schéma d'une couche WFS (XML)."""
    return await fetch_text(
        GEO_WFS_URL,
        params={
            "service": "WFS",
            "request": "DescribeFeatureType",
            "version": "2.0.0",
            "typeName": type_name,
        },
    )


def build_wms_url(
    layers: str,
    bbox: str,
    width: int = 800,
    height: int = 600,
    srs: str = "EPSG:4326",
) -> str:
    """Construit une URL GetMap WMS."""
    params = (
        f"service=WMS&request=GetMap&version=1.3.0"
        f"&layers={layers}&crs={srs}&bbox={bbox}"
        f"&width={width}&height={height}&format=image/png"
    )
    return f"{GEO_WMS_URL}?{params}"


def simplify_coords(geom: dict[str, Any]) -> str:
    """Simplifie les coordonnées pour le contexte LLM."""
    coords = geom.get("coordinates")
    if coords is None:
        return "N/A"
    geom_type = geom.get("type", "")
    if geom_type == "Point":
        return f"[{coords[0]:.6f}, {coords[1]:.6f}]"
    if geom_type in ("LineString", "MultiPoint"):
        return f"{len(coords)} points"
    if geom_type == "Polygon":
        return f"{len(coords[0])} vertices"
    if geom_type in ("MultiPolygon", "MultiLineString"):
        return f"{len(coords)} parties"
    return str(coords)[:100]


def _parse_capabilities(xml_text: str, element_tag: str) -> dict[str, Any]:
    """Parse un GetCapabilities WFS ou WMS en liste de couches."""
    root = ET.fromstring(xml_text)  # noqa: S314
    layers: list[dict[str, str]] = []

    for el in root.iter():
        if not el.tag.endswith(element_tag):
            continue
        # Essayer avec et sans namespace
        name_el = None
        title_el = None
        abstract_el = None
        for ns_prefix in ("", "{http://www.opengis.net/wfs/2.0}", "{http://www.opengis.net/wms}"):
            if name_el is None:
                name_el = el.find(f"{ns_prefix}Name")
            if title_el is None:
                title_el = el.find(f"{ns_prefix}Title")
            if abstract_el is None:
                abstract_el = el.find(f"{ns_prefix}Abstract")

        if name_el is not None and name_el.text:
            layers.append(
                {
                    "name": name_el.text,
                    "title": title_el.text if title_el is not None and title_el.text else "",
                    "abstract": abstract_el.text if abstract_el is not None and abstract_el.text else "",
                }
            )

    return {"total": len(layers), "layers": layers}
