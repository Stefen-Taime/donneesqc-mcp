"""Interroge les données d'une ressource via le DataStore CKAN."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def query_resource_data(
    resource_id: str,
    question: str | None = None,
    filters: str | None = None,
    fields: str | None = None,
    sort: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Interroge les données d'une ressource Données Québec via le DataStore.

    Fonctionne pour les CSV/XLSX importés dans le DataStore.
    Vérifiez que 'datastore_active' est True via get_resource_info.

    Workflow recommandé :
    1. search_datasets pour trouver le jeu
    2. list_dataset_resources pour voir les ressources
    3. query_resource_data avec page_size=20 pour aperçu
    4. Pour des analyses avancées, utiliser query_resource_sql

    Parameters:
        resource_id: ID de la ressource DataStore.
        question: Recherche plein texte dans toutes les colonnes.
        filters: Filtres JSON clé-valeur (ex: '{"ville": "Montréal"}').
        fields: Colonnes à retourner (séparées par des virgules).
        sort: Tri (ex: 'population desc').
        page: Numéro de page (défaut 1).
        page_size: Lignes par page (1-200, défaut 20).
    """
    try:
        page_size = max(1, min(page_size, 200))
        offset = (max(1, page) - 1) * page_size

        try:
            filters_dict = json.loads(filters) if filters else None
        except json.JSONDecodeError:
            return json.dumps({"error": f"Le paramètre 'filters' n'est pas du JSON valide: {filters}"}, ensure_ascii=False)

        fields_list = [f.strip() for f in fields.split(",")] if fields else None

        result = await ckan_api.datastore_search(
            DQ_API_URL,
            resource_id=resource_id,
            q=question,
            filters=filters_dict,
            fields=fields_list,
            sort=sort,
            limit=page_size,
            offset=offset,
        )

        return json.dumps(
            {
                "total": result.get("total", 0),
                "page": page,
                "page_size": page_size,
                "fields": [f["id"] for f in result.get("fields", []) if f["id"] != "_id"],
                "records": result.get("records", []),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans query_resource_data")
        return json.dumps({"error": f"Impossible d'interroger la ressource '{resource_id}'."}, ensure_ascii=False)
