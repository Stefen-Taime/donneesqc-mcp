"""Détail d'une organisation Données Québec."""

import json
import logging
from typing import Any

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_organization_info(org_id: str, include_datasets: bool = False) -> str:
    """Détail d'une organisation et optionnellement ses jeux de données.

    Parameters:
        org_id: Identifiant de l'organisation (ex: 'ville-de-montreal').
        include_datasets: Inclure la liste de ses jeux de données (défaut False).
    """
    try:
        org = await ckan_api.organization_show(DQ_API_URL, org_id, include_datasets=include_datasets)

        info: dict[str, Any] = {
            "id": org.get("name"),
            "title": org.get("display_name") or org.get("title"),
            "description": org.get("description"),
            "image_url": org.get("image_display_url"),
            "num_datasets": org.get("package_count", 0),
            "created": org.get("created"),
        }

        if include_datasets:
            info["datasets"] = [
                {"id": p["name"], "title": p["title"], "modified": p.get("metadata_modified")}
                for p in org.get("packages", [])[:50]
            ]

        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Erreur dans get_organization_info")
        return json.dumps({"error": f"Impossible de récupérer l'organisation '{org_id}'."}, ensure_ascii=False)
