"""Liste des organisations publiant sur Données Québec."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_organizations(query: str | None = None) -> str:
    """Liste les organisations publiant des données sur Données Québec.

    Inclut les ministères du Québec, les villes, les sociétés d'État
    et autres organismes publics. Triées par nombre de jeux publiés.

    Parameters:
        query: Filtre optionnel sur le nom (ex: 'montreal', 'santé').
    """
    try:
        orgs = await ckan_api.organization_list(DQ_API_URL, all_fields=True)

        if query:
            q_lower = query.lower()
            orgs = [o for o in orgs if q_lower in o.get("display_name", "").lower() or q_lower in o.get("name", "").lower()]

        summary = []
        for org in orgs:
            summary.append({
                "id": org.get("name"),
                "title": org.get("display_name") or org.get("title"),
                "num_datasets": org.get("package_count", 0),
                "description": (org.get("description") or "")[:200],
            })

        summary.sort(key=lambda x: x["num_datasets"], reverse=True)

        return json.dumps({"total": len(summary), "organizations": summary[:100]}, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Erreur dans list_organizations")
        return json.dumps({"error": "Impossible de lister les organisations."}, ensure_ascii=False)
