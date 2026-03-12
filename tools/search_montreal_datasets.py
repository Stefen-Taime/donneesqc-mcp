"""Recherche dans le catalogue de données ouvertes de Montréal."""

import json
import logging

from helpers import ckan_api
from helpers.config import MTL_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def search_montreal_datasets(query: str, page: int = 1, page_size: int = 20) -> str:
    """Recherche dans le catalogue de données ouvertes de la Ville de Montréal.

    Le portail donnees.montreal.ca contient des données spécifiques à la
    ville : actes criminels, travaux routiers, arbres publics, pistes
    cyclables, qualité de l'eau, contrats municipaux, etc.

    Parameters:
        query: Termes de recherche (ex: 'pistes cyclables', 'actes criminels').
        page: Numéro de page (défaut 1).
        page_size: Résultats par page (1-100, défaut 20).
    """
    try:
        page_size = max(1, min(page_size, 100))
        start = (max(1, page) - 1) * page_size

        result = await ckan_api.package_search(MTL_API_URL, query=query, rows=page_size, start=start)

        datasets = []
        for pkg in result.get("results", []):
            datasets.append({
                "id": pkg.get("id"),
                "name": pkg.get("name"),
                "title": pkg.get("title"),
                "description": (pkg.get("notes") or "")[:300],
                "organization": pkg.get("organization", {}).get("title", "Ville de Montréal"),
                "num_resources": pkg.get("num_resources", 0),
                "last_modified": pkg.get("metadata_modified"),
                "url": f"https://donnees.montreal.ca/dataset/{pkg.get('name')}",
            })

        return json.dumps(
            {"count": result.get("count", 0), "page": page, "page_size": page_size, "datasets": datasets},
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans search_montreal_datasets")
        return json.dumps({"error": "Impossible de rechercher sur donnees.montreal.ca."}, ensure_ascii=False)
