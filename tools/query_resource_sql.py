"""Requête SQL directe sur le DataStore — fonctionnalité absente de data.gouv.fr."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def query_resource_sql(sql: str) -> str:
    """Exécute une requête SQL sur le DataStore de Données Québec (lecture seule).

    Fonctionnalité unique — absente de data.gouv.fr.
    Permet des agrégations (GROUP BY, COUNT, SUM, AVG), des jointures
    entre ressources, des sous-requêtes et du SQL arbitraire.

    Les tables sont référencées par leur resource_id entre guillemets.

    Parameters:
        sql: Requête SQL SELECT (lecture seule).
             Exemple: SELECT "ville", COUNT(*) as total
                      FROM "abc-123-def"
                      GROUP BY "ville"
                      ORDER BY total DESC
                      LIMIT 20
    """
    try:
        result = await ckan_api.datastore_search_sql(DQ_API_URL, sql)

        return json.dumps(
            {
                "fields": [f["id"] for f in result.get("fields", [])],
                "records": result.get("records", []),
                "sql": result.get("sql", sql),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans query_resource_sql")
        return json.dumps({"error": "Erreur SQL. Vérifiez la syntaxe et les resource_id utilisés."}, ensure_ascii=False)
