"""Récupère les entités géographiques d'une couche WFS."""

import json
import logging

from helpers import geo_api
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_geospatial_features(
    layer_name: str,
    max_features: int = 50,
    bbox: str | None = None,
    cql_filter: str | None = None,
) -> str:
    """Récupère les entités géographiques d'une couche WFS en GeoJSON.

    Permet d'extraire des données vectorielles avec attributs et
    géométries (points, lignes, polygones).

    Parameters:
        layer_name: Nom complet de la couche (ex: 'msp:casernes_incendie').
        max_features: Nombre max d'entités (défaut 50, max 5000).
        bbox: Emprise géographique 'minx,miny,maxx,maxy' en EPSG:4326.
              Ex: '-73.65,45.45,-73.50,45.55' pour le centre de Montréal.
        cql_filter: Filtre CQL optionnel (ex: "municipalite='Montréal'").
    """
    try:
        result = await geo_api.get_features(
            type_name=layer_name,
            max_features=max_features,
            bbox=bbox,
            cql_filter=cql_filter,
        )

        features = result.get("features", [])
        summary = {
            "layer": layer_name,
            "type": "FeatureCollection",
            "total_returned": len(features),
            "features": [],
        }

        for feat in features[:max_features]:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            summary["features"].append({
                "properties": props,
                "geometry_type": geom.get("type", "unknown"),
                "coordinates_sample": geo_api.simplify_coords(geom),
            })

        return json.dumps(summary, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Erreur dans get_geospatial_features")
        return json.dumps({"error": f"Impossible de récupérer les entités de la couche '{layer_name}'."}, ensure_ascii=False)
