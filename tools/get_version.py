"""Endpoint /version — informations sur le serveur MCP."""

import json
import logging
import sys

from tools import mcp

logger = logging.getLogger(__name__)


def _get_version() -> str:
    """Lit la version depuis _version.py ou retourne un fallback."""
    try:
        from _version import version
    except Exception:
        return "0.0.0-dev"
    else:
        return version


@mcp.tool()
async def get_version() -> str:
    """Retourne les informations de version du serveur MCP Donnees Quebec.

    Inclut la version du serveur, la version Python, et les capacites disponibles.
    """
    try:
        return json.dumps(
            {
                "name": "donneesqc-mcp",
                "version": _get_version(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "capabilities": {
                    "donnees_quebec": True,
                    "ville_montreal": True,
                    "geospatial_igo": True,
                    "geocoding": True,
                    "coordinate_conversion": True,
                    "non_datastore_download": True,
                },
                "sources": [
                    "donneesquebec.ca (CKAN)",
                    "donnees.montreal.ca (CKAN)",
                    "IGO Gouvernement du Quebec (WMS/WFS)",
                    "Adresses Quebec (ICherche)",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception:
        logger.exception("Erreur dans get_version")
        return json.dumps({"error": "Impossible de recuperer les informations de version."}, ensure_ascii=False)
