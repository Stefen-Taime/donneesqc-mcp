"""Configuration centralisée — variables d'environnement."""

import os

# Serveur MCP
MCP_HOST: str = os.environ.get("MCP_HOST", "0.0.0.0")
MCP_PORT: int = int(os.environ.get("MCP_PORT", "8000"))
MCP_ENV: str = os.environ.get("MCP_ENV", "local")
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

# Données Québec (CKAN)
DQ_API_URL: str = os.environ.get("DQ_API_URL", "https://www.donneesquebec.ca/recherche/api/3/action")
DQ_BASE_URL: str = os.environ.get("DQ_BASE_URL", "https://www.donneesquebec.ca/recherche")

# Ville de Montréal (CKAN)
MTL_API_URL: str = os.environ.get("MTL_API_URL", "https://donnees.montreal.ca/api/3/action")
MTL_BASE_URL: str = os.environ.get("MTL_BASE_URL", "https://donnees.montreal.ca")

# Géospatial — services OGC (IGO)
GEO_WMS_URL: str = os.environ.get("GEO_WMS_URL", "https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi")
GEO_WFS_URL: str = os.environ.get("GEO_WFS_URL", "https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi")

# Geocoding — Adresses Québec (API REST)
GEOCODER_URL: str = os.environ.get(
    "GEOCODER_URL",
    "https://geoegl.msp.gouv.qc.ca/apis/icherche",
)

# Observabilité
SENTRY_DSN: str | None = os.environ.get("SENTRY_DSN")
SENTRY_SAMPLE_RATE: float = float(os.environ.get("SENTRY_SAMPLE_RATE", "1.0"))

# HTTP
HTTP_TIMEOUT: float = float(os.environ.get("HTTP_TIMEOUT", "30.0"))
HTTP_MAX_RETRIES: int = int(os.environ.get("HTTP_MAX_RETRIES", "3"))
HTTP_USER_AGENT: str = "donneesqc-mcp (https://github.com/Stefen-Taime/donneesqc-mcp)"

# Limites de téléchargement
DOWNLOAD_MAX_BYTES: int = int(os.environ.get("DOWNLOAD_MAX_BYTES", str(50 * 1024 * 1024)))  # 50 Mo
