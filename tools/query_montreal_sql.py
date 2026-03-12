"""Requête SQL sur les données de la Ville de Montréal."""

import json
import logging

from helpers import ckan_api
from helpers.config import MTL_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def query_montreal_sql(sql: str) -> str:
    """Requête SQL sur les données de donnees.montreal.ca (lecture seule).

    Mêmes capacités que query_resource_sql mais sur le DataStore montréalais.

    Parameters:
        sql: Requête SELECT SQL. Les tables sont les resource_id montréalais.
    """
    try:
        result = await ckan_api.datastore_search_sql(MTL_API_URL, sql)

        return json.dumps(
            {
                "fields": [f["id"] for f in result.get("fields", [])],
                "records": result.get("records", []),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans query_montreal_sql")
        return json.dumps(
            {"error": "Erreur SQL sur donnees.montreal.ca. Vérifiez la syntaxe et les resource_id."},
            ensure_ascii=False,
        )
