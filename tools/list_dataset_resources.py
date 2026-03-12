"""Liste les ressources (fichiers) d'un jeu de données."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_dataset_resources(dataset_id: str) -> str:
    """Liste les fichiers et ressources d'un jeu de données Données Québec.

    Retourne format, taille, disponibilité DataStore et URL de chaque ressource.

    Parameters:
        dataset_id: Identifiant ou slug du jeu de données.
    """
    try:
        pkg = await ckan_api.package_show(DQ_API_URL, dataset_id)
        resources = [
            {
                "id": res.get("id"),
                "name": res.get("name") or res.get("description", "Sans nom"),
                "format": res.get("format", "inconnu"),
                "size_bytes": res.get("size"),
                "datastore_active": res.get("datastore_active", False),
                "url": res.get("url"),
                "last_modified": res.get("last_modified"),
            }
            for res in pkg.get("resources", [])
        ]

        return json.dumps(
            {"dataset": pkg.get("title"), "total_resources": len(resources), "resources": resources},
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans list_dataset_resources")
        return json.dumps({"error": f"Impossible de lister les ressources du jeu '{dataset_id}'."}, ensure_ascii=False)
