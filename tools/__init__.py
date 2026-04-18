"""Enregistrement des 28 outils MCP.

Chaque outil est defini dans son propre fichier et enregistre ici
sur l'instance FastMCP partagee.
"""

from mcp.server.fastmcp import FastMCP

from helpers.config import MCP_HOST, MCP_PORT

mcp = FastMCP(
    name="donneesqc-mcp",
    host=MCP_HOST,
    port=MCP_PORT,
    instructions="""Tu es un assistant specialise dans les donnees ouvertes du Quebec.
Tu as acces au catalogue complet de Donnees Quebec (donneesquebec.ca),
aux donnees de la Ville de Montreal (donnees.montreal.ca) et aux
services geospatiaux du gouvernement du Quebec (IGO).

Tu peux :
- Rechercher et explorer des jeux de donnees par mots-cles, organisation ou tags
- Interroger directement les donnees (CSV/XLSX) via le DataStore
- Telecharger et lire les ressources non-DataStore (CSV, JSON, GeoJSON)
- Executer des requetes SQL pour des analyses avancees (agregations, jointures)
- Obtenir un apercu rapide (schema + 5 lignes) d'une ressource
- Rechercher et interroger des donnees en un seul appel (find_and_query)
- Generer des squelettes SQL automatiquement (suggest_sql)
- Comparer deux jeux de donnees (compare_datasets)
- Detecter automatiquement la meilleure ressource (auto_detect_resource)
- Explorer les donnees geospatiales (casernes, patrimoine, territoires, etc.)
- Geocoder des adresses quebecoises et faire du geocodage inverse
- Convertir des coordonnees Lambert MTQ (EPSG:32198) <-> WGS84 (EPSG:4326)
- Determiner quelle region/MRC/municipalite contient un point
- Generer des URLs de cartes

Conseils :
1. Utilise find_and_query pour un acces rapide en une seule etape
2. Ou commence par search_datasets / search_montreal_datasets pour chercher
3. Utilise auto_detect_resource pour trouver la meilleure ressource
4. Utilise preview_resource pour un apercu rapide du schema et des donnees
5. Verifie datastore_active avant query_resource_data (sinon download_resource)
6. Pour des analyses avancees, utilise suggest_sql puis query_resource_sql
7. Les donnees proviennent de sources officielles — cite toujours la source
""",
)


def register_all_tools() -> None:
    """Importe tous les modules tools pour declencher l'enregistrement @mcp.tool()."""
    from tools import (  # noqa: F401
        auto_detect_resource,
        compare_datasets,
        convert_coordinates,
        # Donnees Quebec (8 outils)
        describe_geospatial_layer,
        # Nouveaux — Data access (2 outils)
        download_resource,
        # Nouveaux — Intelligence & UX (4 outils)
        find_and_query,
        # Nouveaux — Geospatial enrichi (4 outils)
        geocode,
        get_catalog_stats,
        get_dataset_info,
        get_geospatial_features,
        get_map_url,
        get_organization_info,
        get_resource_info,
        # Nouveaux — DX / Systeme (2 outils)
        get_version,
        list_dataset_resources,
        list_geospatial_layers,
        list_organizations,
        list_tools_with_examples,
        preview_resource,
        # Montreal (3 outils)
        query_montreal_data,
        query_montreal_sql,
        # Donnees Quebec — requetes (2 outils)
        query_resource_data,
        query_resource_sql,
        reverse_geocode,
        search_datasets,
        search_montreal_datasets,
        spatial_intersection,
        suggest_sql,
    )
