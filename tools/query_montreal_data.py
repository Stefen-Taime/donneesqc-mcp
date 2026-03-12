"""Interroge les données d'une ressource montréalaise."""

import json
import logging

from helpers import ckan_api
from helpers.config import MTL_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def query_montreal_data(
    resource_id: str,
    question: str | None = None,
    filters: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Interroge les données d'une ressource de la Ville de Montréal via le DataStore.

    Parameters:
        resource_id: ID de la ressource DataStore montréalaise.
        question: Recherche plein texte.
        filters: Filtres JSON (ex: '{"ARROND": "Le Plateau-Mont-Royal"}').
        page: Numéro de page (défaut 1).
        page_size: Lignes par page (1-200, défaut 20).
    """
    try:
        page_size = max(1, min(page_size, 200))
        offset = (max(1, page) - 1) * page_size

        try:
            filters_dict = json.loads(filters) if filters else None
        except json.JSONDecodeError:
            return json.dumps(
                {"error": f"Le paramètre 'filters' n'est pas du JSON valide: {filters}"},
                ensure_ascii=False,
            )

        result = await ckan_api.datastore_search(
            MTL_API_URL, resource_id=resource_id, q=question, filters=filters_dict, limit=page_size, offset=offset
        )

        return json.dumps(
            {
                "total": result.get("total", 0),
                "page": page,
                "page_size": page_size,
                "fields": [f["id"] for f in result.get("fields", []) if f["id"] != "_id"],
                "records": result.get("records", []),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans query_montreal_data")
        return json.dumps(
            {"error": f"Impossible d'interroger la ressource montréalaise '{resource_id}'."},
            ensure_ascii=False,
        )
