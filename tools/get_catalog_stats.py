"""Statistiques globales du catalogue Données Québec."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_catalog_stats() -> str:
    """Statistiques globales du catalogue Données Québec.

    Retourne le nombre total de jeux, d'organisations, et le top 10
    des organisations les plus prolifiques.
    """
    try:
        all_result = await ckan_api.package_search(DQ_API_URL, query="*:*", rows=0)
        orgs = await ckan_api.organization_list(DQ_API_URL, all_fields=True)

        top_orgs = sorted(orgs, key=lambda x: x.get("package_count", 0), reverse=True)[:10]

        return json.dumps(
            {
                "total_datasets": all_result.get("count", 0),
                "total_organizations": len(orgs),
                "top_organizations": [
                    {"name": o.get("display_name"), "datasets": o.get("package_count", 0)} for o in top_orgs
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans get_catalog_stats")
        return json.dumps({"error": "Impossible de récupérer les statistiques du catalogue."}, ensure_ascii=False)
