"""Métadonnées complètes d'un jeu de données."""

import json
import logging
from typing import Any

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """Métadonnées complètes d'un jeu de données de Données Québec.

    Retourne toutes les informations incluant ressources, organisation,
    licence, dates et tags.

    Parameters:
        dataset_id: Identifiant ou slug du jeu (ex: '9ed153b2-...' ou 'actes-criminels').
    """
    try:
        pkg = await ckan_api.package_show(DQ_API_URL, dataset_id)

        resources = []
        for res in pkg.get("resources", []):
            resources.append({
                "id": res.get("id"),
                "name": res.get("name"),
                "format": res.get("format"),
                "size": res.get("size"),
                "url": res.get("url"),
                "datastore_active": res.get("datastore_active", False),
                "last_modified": res.get("last_modified"),
            })

        info: dict[str, Any] = {
            "id": pkg.get("id"),
            "name": pkg.get("name"),
            "title": pkg.get("title"),
            "description": pkg.get("notes"),
            "organization": pkg.get("organization", {}).get("title", ""),
            "license": pkg.get("license_title"),
            "tags": [t["name"] for t in pkg.get("tags", [])],
            "created": pkg.get("metadata_created"),
            "modified": pkg.get("metadata_modified"),
            "update_frequency": pkg.get("update_frequency", "non spécifié"),
            "num_resources": len(resources),
            "resources": resources,
            "url": f"https://www.donneesquebec.ca/recherche/dataset/{pkg.get('name')}",
        }

        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Erreur dans get_dataset_info")
        return json.dumps({"error": f"Impossible de récupérer le jeu de données '{dataset_id}'. Vérifiez l'identifiant."}, ensure_ascii=False)
