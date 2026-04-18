"""Meta-introspection : liste tous les outils avec exemples d'utilisation."""

import json
import logging

from tools import mcp

logger = logging.getLogger(__name__)

# Exemples d'utilisation pour chaque outil
_TOOL_EXAMPLES: dict[str, dict] = {
    "search_datasets": {
        "category": "Recherche",
        "description": "Rechercher des jeux de donnees sur Donnees Quebec",
        "example": {"query": "pistes cyclables", "organization": "ville-de-montreal"},
    },
    "search_montreal_datasets": {
        "category": "Recherche",
        "description": "Rechercher sur le portail de la Ville de Montreal",
        "example": {"query": "arbres"},
    },
    "get_dataset_info": {
        "category": "Metadonnees",
        "description": "Metadonnees completes d'un jeu de donnees",
        "example": {"dataset_id": "actes-criminels"},
    },
    "list_dataset_resources": {
        "category": "Metadonnees",
        "description": "Liste les fichiers d'un jeu de donnees",
        "example": {"dataset_id": "actes-criminels"},
    },
    "get_resource_info": {
        "category": "Metadonnees",
        "description": "Detail d'une ressource specifique",
        "example": {"resource_id": "<resource_id>"},
    },
    "get_organization_info": {
        "category": "Metadonnees",
        "description": "Detail d'une organisation",
        "example": {"organization_id": "ville-de-montreal"},
    },
    "list_organizations": {
        "category": "Metadonnees",
        "description": "Liste des organisations du catalogue",
        "example": {"query": "ville"},
    },
    "get_catalog_stats": {
        "category": "Metadonnees",
        "description": "Statistiques globales du catalogue",
        "example": {},
    },
    "query_resource_data": {
        "category": "Donnees",
        "description": "Interroger les donnees d'une ressource DataStore",
        "example": {"resource_id": "<resource_id>", "page_size": 10},
    },
    "query_resource_sql": {
        "category": "Donnees",
        "description": "Requete SQL sur le DataStore",
        "example": {"sql": 'SELECT "ville", COUNT(*) as total FROM "<resource_id>" GROUP BY "ville" LIMIT 10'},
    },
    "query_montreal_data": {
        "category": "Donnees",
        "description": "Interroger les donnees de Montreal",
        "example": {"resource_id": "<resource_id>", "page_size": 10},
    },
    "query_montreal_sql": {
        "category": "Donnees",
        "description": "Requete SQL sur les donnees de Montreal",
        "example": {"sql": 'SELECT "ARROND", COUNT(*) as nb FROM "<resource_id>" GROUP BY "ARROND" LIMIT 10'},
    },
    "download_resource": {
        "category": "Donnees",
        "description": "Telecharger une ressource non-DataStore (CSV, JSON, GeoJSON)",
        "example": {"resource_id": "<resource_id>", "max_rows": 50},
    },
    "preview_resource": {
        "category": "Donnees",
        "description": "Apercu rapide : schema + 5 premieres lignes",
        "example": {"resource_id": "<resource_id>"},
    },
    "find_and_query": {
        "category": "Intelligence",
        "description": "Recherche + interrogation en un seul appel",
        "example": {"query": "criminalite montreal", "page_size": 5},
    },
    "suggest_sql": {
        "category": "Intelligence",
        "description": "Genere des squelettes SQL a partir du schema",
        "example": {"resource_id": "<resource_id>"},
    },
    "compare_datasets": {
        "category": "Intelligence",
        "description": "Compare deux jeux de donnees",
        "example": {"dataset_id_1": "actes-criminels", "dataset_id_2": "interventions-pompiers"},
    },
    "auto_detect_resource": {
        "category": "Intelligence",
        "description": "Trouve le meilleur resource_id a partir d'un nom",
        "example": {"dataset_name": "pistes cyclables"},
    },
    "list_geospatial_layers": {
        "category": "Geospatial",
        "description": "Liste les couches WFS/WMS disponibles",
        "example": {"service": "wfs", "query": "casernes"},
    },
    "get_geospatial_features": {
        "category": "Geospatial",
        "description": "Recupere les entites d'une couche WFS",
        "example": {"layer_name": "msp:casernes_incendie", "max_features": 10},
    },
    "describe_geospatial_layer": {
        "category": "Geospatial",
        "description": "Schema d'une couche WFS",
        "example": {"layer_name": "msp:casernes_incendie"},
    },
    "get_map_url": {
        "category": "Geospatial",
        "description": "Genere une URL de carte WMS",
        "example": {"layers": "msp:casernes_incendie", "bbox": "-73.7,45.4,-73.4,45.6"},
    },
    "geocode": {
        "category": "Geospatial",
        "description": "Adresse -> coordonnees (lat/lng)",
        "example": {"address": "900 Boulevard Rene-Levesque, Quebec"},
    },
    "reverse_geocode": {
        "category": "Geospatial",
        "description": "Coordonnees -> adresse quebecoise",
        "example": {"latitude": 45.5017, "longitude": -73.5673},
    },
    "convert_coordinates": {
        "category": "Geospatial",
        "description": "Conversion EPSG:32198 (Lambert) <-> EPSG:4326 (WGS84)",
        "example": {"x": -73.5673, "y": 45.5017, "from_crs": "EPSG:4326", "to_crs": "EPSG:32198"},
    },
    "spatial_intersection": {
        "category": "Geospatial",
        "description": "Quel arrondissement/region contient ce point?",
        "example": {"latitude": 45.5017, "longitude": -73.5673, "layer_type": "regions_administratives"},
    },
    "get_version": {
        "category": "Systeme",
        "description": "Version et capacites du serveur MCP",
        "example": {},
    },
    "list_tools_with_examples": {
        "category": "Systeme",
        "description": "Liste tous les outils avec exemples (cet outil)",
        "example": {},
    },
}


@mcp.tool()
async def list_tools_with_examples(category: str | None = None) -> str:
    """Liste tous les outils MCP disponibles avec leurs descriptions et exemples d'utilisation.

    Permet la meta-introspection : un LLM peut decouvrir les outils disponibles et
    comprendre comment les utiliser.

    Parameters:
        category: Filtrer par categorie (Recherche, Metadonnees, Donnees, Intelligence, Geospatial, Systeme).
    """
    try:
        tools = _TOOL_EXAMPLES

        if category:
            cat_lower = category.lower()
            tools = {k: v for k, v in tools.items() if v["category"].lower() == cat_lower}

        # Grouper par categorie
        categories: dict[str, list] = {}
        for name, info in sorted(tools.items()):
            cat = info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "tool": name,
                "description": info["description"],
                "example_params": info["example"],
            })

        return json.dumps(
            {
                "total_tools": len(tools),
                "categories": categories,
                "tip": "Appelez un outil directement avec les parametres de l'exemple.",
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans list_tools_with_examples")
        return json.dumps({"error": "Impossible de lister les outils."}, ensure_ascii=False)
