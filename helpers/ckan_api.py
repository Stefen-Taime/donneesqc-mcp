"""Helper pour les API CKAN (Données Québec et Montréal).

Les deux portails utilisent CKAN 2.10+. Ce helper expose des fonctions
réutilisables par les tools individuels.
"""

import json
import logging
import re
from typing import Any

from helpers.http_client import fetch_json

logger = logging.getLogger(__name__)


def _extract_result(data: dict[str, Any]) -> Any:
    """Extrait le champ 'result' d'une réponse CKAN."""
    if not data.get("success"):
        error = data.get("error", {})
        msg = error.get("message", "Erreur CKAN inconnue")
        raise RuntimeError(f"Erreur API CKAN: {msg}")
    return data["result"]


async def package_search(
    api_url: str,
    query: str = "*:*",
    rows: int = 20,
    start: int = 0,
    sort: str = "score desc, metadata_modified desc",
    fq: str | None = None,
) -> dict[str, Any]:
    """Recherche de jeux de données."""
    params: dict[str, Any] = {"q": query, "rows": min(rows, 1000), "start": start, "sort": sort}
    if fq:
        params["fq"] = fq
    data = await fetch_json(f"{api_url}/package_search", params=params)
    return _extract_result(data)


async def package_show(api_url: str, package_id: str) -> dict[str, Any]:
    """Métadonnées complètes d'un jeu de données."""
    data = await fetch_json(f"{api_url}/package_show", params={"id": package_id})
    return _extract_result(data)


async def resource_show(api_url: str, resource_id: str) -> dict[str, Any]:
    """Détail d'une ressource spécifique."""
    data = await fetch_json(f"{api_url}/resource_show", params={"id": resource_id})
    return _extract_result(data)


async def datastore_search(
    api_url: str,
    resource_id: str,
    q: str | None = None,
    filters: dict[str, str] | None = None,
    fields: list[str] | None = None,
    sort: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Interrogation du DataStore avec filtres."""
    params: dict[str, Any] = {"resource_id": resource_id, "limit": min(limit, 32000), "offset": offset}
    if q:
        params["q"] = q
    if filters:
        params["filters"] = json.dumps(filters)
    if fields:
        params["fields"] = ",".join(fields)
    if sort:
        params["sort"] = sort
    data = await fetch_json(f"{api_url}/datastore_search", params=params)
    return _extract_result(data)


_SQL_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> None:
    """Valide qu'une requête SQL est en lecture seule (SELECT uniquement).

    Raises:
        ValueError: Si la requête contient des instructions d'écriture.
    """
    stripped = sql.strip().rstrip(";").strip()
    if not stripped.upper().startswith("SELECT"):
        msg = "Seules les requêtes SELECT sont autorisées."
        raise ValueError(msg)
    if _SQL_FORBIDDEN.search(stripped):
        msg = "La requête contient des instructions interdites (INSERT, UPDATE, DELETE, DROP, etc.)."
        raise ValueError(msg)


async def datastore_search_sql(api_url: str, sql: str) -> dict[str, Any]:
    """Requête SQL directe sur le DataStore (SELECT uniquement)."""
    validate_sql(sql)
    data = await fetch_json(f"{api_url}/datastore_search_sql", params={"sql": sql})
    return _extract_result(data)


async def organization_list(api_url: str, all_fields: bool = False) -> list[Any]:
    """Liste des organisations."""
    data = await fetch_json(f"{api_url}/organization_list", params={"all_fields": str(all_fields).lower()})
    return _extract_result(data)


async def organization_show(api_url: str, org_id: str, include_datasets: bool = False) -> dict[str, Any]:
    """Détail d'une organisation."""
    data = await fetch_json(
        f"{api_url}/organization_show",
        params={"id": org_id, "include_datasets": str(include_datasets).lower()},
    )
    return _extract_result(data)


async def tag_list(api_url: str, query: str | None = None) -> list[str]:
    """Liste des tags."""
    params: dict[str, Any] = {}
    if query:
        params["query"] = query
    data = await fetch_json(f"{api_url}/tag_list", params=params)
    return _extract_result(data)


async def site_read(api_url: str) -> Any:
    """Santé du portail CKAN."""
    data = await fetch_json(f"{api_url}/site_read")
    return _extract_result(data)
