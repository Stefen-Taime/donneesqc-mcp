"""Auto-detection de resource_id a partir d'un nom de dataset."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def auto_detect_resource(
    dataset_name: str,
    prefer_format: str = "CSV",
    prefer_datastore: bool = True,
) -> str:
    """Trouve automatiquement le resource_id le plus pertinent a partir d'un nom de dataset.

    Recherche le dataset, puis selectionne la meilleure ressource selon les criteres :
    1. Prefere les ressources DataStore (interrogeables via SQL)
    2. Prefere le format specifie (CSV par defaut)
    3. Prefere la ressource la plus recente

    Parameters:
        dataset_name: Nom, slug ou termes de recherche du jeu de donnees.
        prefer_format: Format prefere (CSV, JSON, XLSX, etc.).
        prefer_datastore: Preferer les ressources DataStore (defaut true).
    """
    try:
        # Essayer d'abord comme slug exact
        try:
            pkg = await ckan_api.package_show(DQ_API_URL, dataset_name)
        except Exception:
            # Sinon, rechercher
            search_result = await ckan_api.package_search(DQ_API_URL, query=dataset_name, rows=5)
            results = search_result.get("results", [])
            if not results:
                return json.dumps(
                    {"error": f"Aucun jeu de donnees trouve pour '{dataset_name}'."},
                    ensure_ascii=False,
                )
            pkg = results[0]

        resources = pkg.get("resources", [])
        if not resources:
            return json.dumps(
                {"error": f"Le jeu '{pkg.get('title')}' n'a aucune ressource.", "dataset_id": pkg.get("id")},
                ensure_ascii=False,
            )

        # Scorer les ressources
        scored: list[tuple[int, dict]] = []
        for res in resources:
            score = 0
            fmt = (res.get("format") or "").upper()
            is_ds = res.get("datastore_active", False)

            if prefer_datastore and is_ds:
                score += 100
            if fmt == prefer_format.upper():
                score += 50
            if fmt in ("CSV", "JSON", "GEOJSON"):
                score += 10
            # Bonus pour les fichiers recents
            if res.get("last_modified"):
                score += 5

            scored.append((score, res))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]

        all_resources = [
            {
                "id": r.get("id"),
                "name": r.get("name"),
                "format": r.get("format"),
                "datastore_active": r.get("datastore_active", False),
                "score": s,
            }
            for s, r in scored
        ]

        return json.dumps(
            {
                "dataset": {
                    "id": pkg.get("id"),
                    "title": pkg.get("title"),
                    "name": pkg.get("name"),
                },
                "recommended_resource": {
                    "id": best.get("id"),
                    "name": best.get("name"),
                    "format": best.get("format"),
                    "datastore_active": best.get("datastore_active", False),
                    "url": best.get("url"),
                },
                "all_resources": all_resources,
                "tip": "Utilisez le resource_id recommande avec query_resource_data ou query_resource_sql."
                if best.get("datastore_active")
                else "Cette ressource n'est pas dans le DataStore. Utilisez download_resource.",
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        logger.exception("Erreur dans auto_detect_resource")
        return json.dumps(
            {"error": f"Impossible de detecter une ressource pour '{dataset_name}'."},
            ensure_ascii=False,
        )
