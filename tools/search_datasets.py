"""Recherche de jeux de données sur Données Québec."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def search_datasets(
    query: str,
    page: int = 1,
    page_size: int = 20,
    organization: str | None = None,
    tags: str | None = None,
) -> str:
    """Recherche de jeux de données sur Données Québec par mots-clés.

    Le portail contient des données du gouvernement du Québec et de
    nombreuses municipalités (Montréal, Québec, Laval, Sherbrooke, Gatineau, etc.).

    Parameters:
        query: Termes de recherche (ex: 'transport', 'criminalité montréal').
        page: Numéro de page (défaut 1).
        page_size: Résultats par page (1-100, défaut 20).
        organization: Filtrer par organisation (ex: 'ville-de-montreal').
        tags: Filtrer par tags séparés par des virgules.
    """
    try:
        page_size = max(1, min(page_size, 100))
        start = (max(1, page) - 1) * page_size

        fq_parts: list[str] = []
        if organization:
            fq_parts.append(f"organization:{organization}")
        if tags:
            for tag in tags.split(","):
                fq_parts.append(f'tags:"{tag.strip()}"')
        fq = " AND ".join(fq_parts) if fq_parts else None

        result = await ckan_api.package_search(DQ_API_URL, query=query, rows=page_size, start=start, fq=fq)

        datasets = []
        for pkg in result.get("results", []):
            datasets.append({
                "id": pkg.get("id"),
                "name": pkg.get("name"),
                "title": pkg.get("title"),
                "description": (pkg.get("notes") or "")[:300],
                "organization": pkg.get("organization", {}).get("title", ""),
                "tags": [t["name"] for t in pkg.get("tags", [])],
                "num_resources": pkg.get("num_resources", 0),
                "last_modified": pkg.get("metadata_modified"),
                "url": f"https://www.donneesquebec.ca/recherche/dataset/{pkg.get('name')}",
            })

        return json.dumps(
            {"count": result.get("count", 0), "page": page, "page_size": page_size, "datasets": datasets},
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans search_datasets")
        return json.dumps({"error": "Impossible de rechercher les jeux de données. Vérifiez les paramètres et réessayez."}, ensure_ascii=False)
