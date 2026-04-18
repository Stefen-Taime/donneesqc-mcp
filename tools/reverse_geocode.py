"""Geocodage inverse : coordonnees (lat/lng) -> adresse quebecoise."""

import json
import logging

from helpers.config import GEOCODER_URL
from helpers.http_client import fetch_json
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def reverse_geocode(latitude: float, longitude: float, limit: int = 1) -> str:
    """Convertit des coordonnees geographiques en adresse quebecoise.

    Utilise le service ICherche (Adresses Quebec) du gouvernement du Quebec.

    Parameters:
        latitude: Latitude en degres decimaux (ex: 45.5017).
        longitude: Longitude en degres decimaux (ex: -73.5673).
        limit: Nombre maximal de resultats (defaut 1, max 5).
    """
    try:
        limit = max(1, min(limit, 5))

        data = await fetch_json(
            f"{GEOCODER_URL}/reverse",
            params={
                "loc": f"{longitude},{latitude}",
                "limit": limit,
                "type": "adresses",
            },
        )

        features = data.get("features", [])
        results = []
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [])

            results.append({
                "address": props.get("recherche", props.get("nom", "")),
                "street_number": props.get("numero", ""),
                "street": props.get("rue", ""),
                "municipality": props.get("municipalite", ""),
                "mrc": props.get("mrc", ""),
                "region": props.get("region", ""),
                "postal_code": props.get("codePostal", ""),
                "longitude": coords[0] if len(coords) > 0 else None,
                "latitude": coords[1] if len(coords) > 1 else None,
                "distance_m": props.get("distance", None),
            })

        return json.dumps(
            {
                "query": {"latitude": latitude, "longitude": longitude},
                "total": len(results),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        logger.exception("Erreur dans reverse_geocode")
        return json.dumps(
            {"error": f"Impossible de geocoder les coordonnees ({latitude}, {longitude})."},
            ensure_ascii=False,
        )
