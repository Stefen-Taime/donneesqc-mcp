"""Intersection spatiale : determine quelle region/arrondissement contient un point."""

import json
import logging

from helpers import geo_api
from tools import mcp

logger = logging.getLogger(__name__)

# Couches WFS utiles pour l'intersection
_INTERSECTION_LAYERS = {
    "regions_administratives": "msp_reg_admin_s",
    "mrc": "msp_mrc_s",
    "municipalites": "msp_munic_s",
    "arrondissements_montreal": "msp_arrond_s",
    "circonscriptions_provinciales": "msp_ce_s",
    "circonscriptions_federales": "msp_cef_s",
}


@mcp.tool()
async def spatial_intersection(
    latitude: float,
    longitude: float,
    layer_type: str = "regions_administratives",
) -> str:
    """Determine quelle region, MRC, municipalite ou arrondissement contient un point.

    Utilise les couches WFS du gouvernement du Quebec pour effectuer une
    intersection spatiale (point-in-polygon).

    Parameters:
        latitude: Latitude en degres decimaux (ex: 45.5017).
        longitude: Longitude en degres decimaux (ex: -73.5673).
        layer_type: Type de couche pour l'intersection.
            Valeurs possibles: regions_administratives, mrc, municipalites,
            arrondissements_montreal, circonscriptions_provinciales, circonscriptions_federales.
    """
    try:
        if layer_type not in _INTERSECTION_LAYERS:
            return json.dumps(
                {
                    "error": f"Type de couche inconnu: '{layer_type}'.",
                    "valid_types": list(_INTERSECTION_LAYERS.keys()),
                },
                ensure_ascii=False,
            )

        layer_name = _INTERSECTION_LAYERS[layer_type]

        # Utiliser un CQL_FILTER INTERSECTS pour trouver le polygone contenant le point
        cql = f"INTERSECTS(geometry, POINT({longitude} {latitude}))"

        result = await geo_api.get_features(
            type_name=layer_name,
            max_features=5,
            cql_filter=cql,
        )

        features = result.get("features", [])

        if not features:
            # Fallback : essayer avec un BBOX serre autour du point
            delta = 0.01  # ~1km
            bbox = f"{longitude - delta},{latitude - delta},{longitude + delta},{latitude + delta}"
            result = await geo_api.get_features(
                type_name=layer_name,
                max_features=5,
                bbox=bbox,
            )
            features = result.get("features", [])

        if not features:
            return json.dumps(
                {
                    "query": {"latitude": latitude, "longitude": longitude, "layer_type": layer_type},
                    "result": None,
                    "note": "Aucune entite trouvee a ces coordonnees. Le point est peut-etre en dehors du Quebec.",
                },
                ensure_ascii=False,
                indent=2,
            )

        # Extraire les proprietes
        matches = []
        for feat in features:
            props = feat.get("properties", {})
            # Filtrer les proprietes utiles (exclure les geometries longues)
            clean_props = {k: v for k, v in props.items() if not isinstance(v, (dict, list))}
            matches.append(clean_props)

        return json.dumps(
            {
                "query": {"latitude": latitude, "longitude": longitude, "layer_type": layer_type},
                "total": len(matches),
                "results": matches,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        logger.exception("Erreur dans spatial_intersection")
        return json.dumps(
            {
                "error": f"Impossible d'effectuer l'intersection spatiale a ({latitude}, {longitude}).",
                "tip": "Le service WFS est peut-etre temporairement indisponible.",
            },
            ensure_ascii=False,
        )
