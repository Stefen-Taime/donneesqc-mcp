"""Point d'entrée du serveur MCP Données Québec."""

import logging

from helpers.config import LOG_LEVEL, MCP_ENV, MCP_HOST, MCP_PORT, SENTRY_DSN, SENTRY_SAMPLE_RATE

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Sentry (optionnel)
if SENTRY_DSN:
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=MCP_ENV,
            traces_sample_rate=SENTRY_SAMPLE_RATE,
            profiles_sample_rate=SENTRY_SAMPLE_RATE,
        )
        logger.info("Sentry initialisé (env=%s)", MCP_ENV)
    except ImportError:
        logger.warning("sentry-sdk non installé, monitoring désactivé")


def main() -> None:
    """Lance le serveur MCP."""
    from tools import mcp, register_all_tools

    register_all_tools()

    logger.info("Démarrage du serveur MCP Données Québec sur %s:%s", MCP_HOST, MCP_PORT)
    logger.info("16 outils : 8 Données Québec + 3 Montréal + 4 Géospatial + 1 Stats")

    mcp.run(  # host/port passés via **kwargs à uvicorn
        transport="streamable-http",
        host=MCP_HOST,  # ty: ignore[unknown-argument]
        port=MCP_PORT,  # ty: ignore[unknown-argument]
    )


if __name__ == "__main__":
    main()
