"""Décrit le schéma d'une couche géospatiale."""

import json
import logging

from helpers import geo_api
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def describe_geospatial_layer(layer_name: str) -> str:
    """Décrit le schéma d'une couche géospatiale (champs et types).

    Utile avant d'interroger une couche pour connaître les attributs
    disponibles et construire des filtres CQL pertinents.

    Parameters:
        layer_name: Nom de la couche WFS (ex: 'msp:casernes_incendie').
    """
    try:
        schema_xml = await geo_api.describe_feature_type(layer_name)

        return json.dumps(
            {"layer": layer_name, "schema_xml": schema_xml[:5000]},
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans describe_geospatial_layer")
        return json.dumps({"error": f"Impossible de décrire la couche '{layer_name}'."}, ensure_ascii=False)
