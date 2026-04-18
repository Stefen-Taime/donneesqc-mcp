"""Tool composite : search -> resources -> query en un seul appel."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def find_and_query(
    query: str,
    question: str | None = None,
    page_size: int = 5,
    prefer_format: str = "CSV",
) -> str:
    """Recherche un jeu de donnees, trouve une ressource DataStore, et interroge les donnees en un seul appel.

    Enchaine automatiquement : search_datasets -> list_resources -> query_resource_data.
    Evite 3 allers-retours LLM.

    Parameters:
        query: Termes de recherche (ex: 'pistes cyclables montreal').
        question: Recherche plein texte dans les donnees (optionnel).
        page_size: Nombre de lignes de donnees a retourner (defaut 5).
        prefer_format: Format prefere pour la ressource (defaut CSV).
    """
    try:
        # Etape 1 : Rechercher des datasets
        search_result = await ckan_api.package_search(DQ_API_URL, query=query, rows=5)
        datasets = search_result.get("results", [])

        if not datasets:
            return json.dumps(
                {"error": f"Aucun jeu de donnees trouve pour '{query}'."},
                ensure_ascii=False,
            )

        # Etape 2 : Trouver une ressource DataStore
        selected_dataset = None
        selected_resource = None

        for pkg in datasets:
            resources = pkg.get("resources", [])
            # Preferer les ressources DataStore au format souhaite
            for res in resources:
                if res.get("datastore_active"):
                    fmt = (res.get("format") or "").upper()
                    if fmt == prefer_format.upper():
                        selected_dataset = pkg
                        selected_resource = res
                        break
            if selected_resource:
                break

            # Fallback : prendre la premiere ressource DataStore
            for res in resources:
                if res.get("datastore_active"):
                    selected_dataset = pkg
                    selected_resource = res
                    break
            if selected_resource:
                break

        if not selected_resource:
            # Retourner les datasets trouves sans donnees
            return json.dumps(
                {
                    "search_results": len(datasets),
                    "datasets": [
                        {
                            "id": pkg.get("id"),
                            "name": pkg.get("name"),
                            "title": pkg.get("title"),
                            "resources": [
                                {
                                    "id": r.get("id"),
                                    "format": r.get("format"),
                                    "datastore_active": r.get("datastore_active", False),
                                }
                                for r in pkg.get("resources", [])
                            ],
                        }
                        for pkg in datasets[:3]
                    ],
                    "note": (
                        "Aucune ressource DataStore trouvee."
                        " Utilisez download_resource pour les ressources non-DataStore."
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )

        # Etape 3 : Interroger les donnees
        data_result = await ckan_api.datastore_search(
            DQ_API_URL,
            resource_id=selected_resource["id"],
            q=question,
            limit=min(page_size, 100),
        )

        return json.dumps(
            {
                "dataset": {
                    "id": selected_dataset.get("id"),
                    "title": selected_dataset.get("title"),
                    "organization": selected_dataset.get("organization", {}).get("title", ""),
                    "url": f"https://www.donneesquebec.ca/recherche/dataset/{selected_dataset.get('name')}",
                },
                "resource": {
                    "id": selected_resource.get("id"),
                    "name": selected_resource.get("name"),
                    "format": selected_resource.get("format"),
                },
                "data": {
                    "total": data_result.get("total", 0),
                    "fields": [f["id"] for f in data_result.get("fields", []) if f["id"] != "_id"],
                    "records": data_result.get("records", []),
                },
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        logger.exception("Erreur dans find_and_query")
        return json.dumps(
            {"error": f"Erreur lors de la recherche et interrogation pour '{query}'."},
            ensure_ascii=False,
        )
