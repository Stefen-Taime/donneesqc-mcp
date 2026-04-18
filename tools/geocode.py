"""Geocodage : adresse -> coordonnees (lat/lng) via Adresses Quebec / ICherche."""

import json
import logging

from helpers.config import GEOCODER_URL
from helpers.http_client import fetch_json
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def geocode(address: str, limit: int = 5) -> str:
    """Convertit une adresse quebecoise en coordonnees geographiques (lat/lng).

    Utilise le service ICherche (Adresses Quebec) du gouvernement du Quebec.

    Parameters:
        address: Adresse a geocoder (ex: '900 Boulevard Rene-Levesque, Quebec').
        limit: Nombre maximal de resultats (defaut 5, max 10).
    """
    try:
        limit = max(1, min(limit, 10))

        data = await fetch_json(
            f"{GEOCODER_URL}/geocode",
            params={"q": address, "limit": limit, "type": "adresses"},
        )

        features = data.get("features", [])
        results = []
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [])

            results.append({
                "address": props.get("recherche", props.get("nom", "")),
                "municipality": props.get("municipalite", ""),
                "mrc": props.get("mrc", ""),
                "region": props.get("region", ""),
                "longitude": coords[0] if len(coords) > 0 else None,
                "latitude": coords[1] if len(coords) > 1 else None,
                "confidence": props.get("score", None),
            })

        return json.dumps(
            {
                "query": address,
                "total": len(results),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        logger.exception("Erreur dans geocode")
        return json.dumps(
            {"error": f"Impossible de geocoder l'adresse '{address}'. Verifiez le format."},
            ensure_ascii=False,
        )
