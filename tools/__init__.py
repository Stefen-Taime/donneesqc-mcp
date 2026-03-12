"""Enregistrement des 16 outils MCP.

Chaque outil est défini dans son propre fichier et enregistré ici
sur l'instance FastMCP partagée.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="donneesqc-mcp",
    instructions="""Tu es un assistant spécialisé dans les données ouvertes du Québec.
Tu as accès au catalogue complet de Données Québec (donneesquebec.ca),
aux données de la Ville de Montréal (donnees.montreal.ca) et aux
services géospatiaux du gouvernement du Québec (IGO).

Tu peux :
- Rechercher et explorer des jeux de données par mots-clés, organisation ou tags
- Interroger directement les données (CSV/XLSX) via le DataStore
- Exécuter des requêtes SQL pour des analyses avancées (agrégations, jointures)
- Explorer les données géospatiales (casernes, patrimoine, territoires, etc.)
- Générer des URLs de cartes

Conseils :
1. Commence par search_datasets ou search_montreal_datasets pour trouver un jeu
2. Utilise list_dataset_resources pour voir les fichiers disponibles
3. Vérifie que 'datastore_active' est True avant query_resource_data
4. Pour des analyses avancées, utilise query_resource_sql avec du SQL
5. Les données proviennent de sources officielles — cite toujours la source
""",
)


def register_all_tools() -> None:
    """Importe tous les modules tools pour déclencher l'enregistrement @mcp.tool()."""
    from tools import (  # noqa: F401
        describe_geospatial_layer,
        get_catalog_stats,
        get_dataset_info,
        get_geospatial_features,
        get_map_url,
        get_organization_info,
        get_resource_info,
        list_dataset_resources,
        list_geospatial_layers,
        list_organizations,
        query_montreal_data,
        query_montreal_sql,
        query_resource_data,
        query_resource_sql,
        search_datasets,
        search_montreal_datasets,
    )
