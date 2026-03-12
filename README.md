# 🍁 Données Québec MCP Server

[![CI](https://github.com/mcsedition/donneesqc-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/mcsedition/donneesqc-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)

Model Context Protocol (MCP) server that allows AI chatbots (Claude, ChatGPT, Gemini, etc.) to search, explore, and analyze datasets from [Données Québec](https://donneesquebec.ca), [Ville de Montréal](https://donnees.montreal.ca), and Quebec's geospatial services ([IGO](https://igouverte.org)), directly through conversation.

Instead of manually browsing the portal, you can simply ask questions like _"Quels jeux de données existent sur la criminalité à Montréal ?"_ or _"Combien d'actes criminels par arrondissement en 2025 ?"_ and get instant answers — including SQL-powered analytics.

> **Compared to [data.gouv.fr MCP](https://github.com/datagouv/datagouv-mcp):**
> ⚡ SQL queries on DataStore · 🗺️ Geospatial OGC layers · 📦 3 data sources · 

## 🌐 Connect your chatbot to the MCP server

Use the hosted endpoint (coming soon) or run locally. The configuration depends on your client:

[Claude Code](#claude-code) | [Claude Desktop](#claude-desktop) | [ChatGPT](#chatgpt) | [Cursor](#cursor) | [VS Code](#vs-code) | [Gemini CLI](#gemini-cli) | [Le Chat (Mistral)](#le-chat-mistral) | [Windsurf](#windsurf)

### Claude Code

```bash
claude mcp add --transport http donneesqc http://localhost:8000/mcp
```

### Claude Desktop

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "donneesqc": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

### ChatGPT

*Paid plans only.* Go to `Settings` > `Apps and connectors` > enable **Developer mode** > `Add new connector` with URL `http://localhost:8000/mcp`.

### Cursor

```json
{
  "mcpServers": {
    "donneesqc": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

### VS Code

Add to `mcp.json` (run **MCP: Open User Configuration** from Command Palette):

```json
{
  "servers": {
    "donneesqc": {
      "url": "http://localhost:8000/mcp",
      "type": "http"
    }
  }
}
```

### Gemini CLI

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "donneesqc": {
      "httpUrl": "http://localhost:8000/mcp"
    }
  }
}
```

### Le Chat (Mistral)

`Intelligence` > `Connectors` > `Add connector` > `Custom MCP Connector` > URL: `http://localhost:8000/mcp`.

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "donneesqc": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

## 🖥️ Run locally

### 🐳 With Docker (Recommended)

```bash
git clone https://github.com/mcsedition/donneesqc-mcp.git
cd donneesqc-mcp
docker compose up -d
```

### ⚙️ Manual Installation

```bash
git clone https://github.com/mcsedition/donneesqc-mcp.git
cd donneesqc-mcp
uv sync
cp .env.example .env
set -a && source .env && set +a
uv run main.py
```

**Environment variables:**

| Variable | Default | Description |
|---|---|---|
| `MCP_HOST` | `0.0.0.0` | Host to bind to. Use `127.0.0.1` for local dev. |
| `MCP_PORT` | `8000` | Port for the HTTP server. |
| `MCP_ENV` | `local` | Environment name (Sentry). |
| `DQ_API_URL` | `https://www.donneesquebec.ca/recherche/api/3/action` | Données Québec CKAN API. |
| `MTL_API_URL` | `https://donnees.montreal.ca/api/3/action` | Montréal CKAN API. |
| `GEO_WFS_URL` | `https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi` | IGO WFS endpoint. |
| `GEO_WMS_URL` | `https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi` | IGO WMS endpoint. |
| `LOG_LEVEL` | `INFO` | Python log level. |
| `SENTRY_DSN` | _(unset)_ | Sentry DSN for monitoring. |

## 🚚 Transport support

Built with the [official Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk). **Streamable HTTP only** — STDIO and SSE are not supported.

**Endpoints:**
- `POST /mcp` — JSON-RPC messages
- `GET /health` — Health probe

## 🛠️ Available Tools (16)

### Données Québec — datasets (8 tools)

| Tool | Description |
|---|---|
| `search_datasets` | Search by keywords, organization, tags |
| `get_dataset_info` | Full metadata for a dataset |
| `list_dataset_resources` | List files/resources in a dataset |
| `get_resource_info` | Detailed info on a specific resource |
| `query_resource_data` | Query DataStore with filters and pagination |
| `query_resource_sql` | ⚡ **Direct SQL** — aggregations, joins, subqueries |
| `list_organizations` | Ministries, cities, agencies |
| `get_organization_info` | Organization details |
| `get_catalog_stats` | Catalog-wide statistics |

### Ville de Montréal (3 tools)

| Tool | Description |
|---|---|
| `search_montreal_datasets` | Search donnees.montreal.ca |
| `query_montreal_data` | Query Montreal DataStore |
| `query_montreal_sql` | SQL on Montreal data |

### Geospatial / IGO (4 tools)

| Tool | Description |
|---|---|
| `list_geospatial_layers` | WFS/WMS layers from IGO |
| `get_geospatial_features` | GeoJSON features from WFS |
| `describe_geospatial_layer` | Layer schema (fields, types) |
| `get_map_url` | WMS map image URL |

## 🧪 Tests

```bash
# Run all tests
uv run pytest

# Verbose
uv run pytest -v

# Interactive testing with MCP Inspector
npx @modelcontextprotocol/inspector --http-url "http://127.0.0.1:8000/mcp"
```

## 🤝 Contributing

- **1 feature = 1 PR**
- All code must be reviewed and tested by a human before submission.

```bash
# Lint and format
uv run ruff check --fix && uv run ruff format

# Type check
uv run ty check

# Install pre-commit hooks
uv run pre-commit install
```

### Releases

```bash
./tag_version.sh 1.0.0          # Create release
./tag_version.sh 1.0.0 --dry-run  # Preview
```

## 📊 Data Sources

- **[Données Québec](https://donneesquebec.ca)** — Provincial portal (government + municipalities), CKAN-based
- **[donnees.montreal.ca](https://donnees.montreal.ca)** — Montreal municipal portal, richest in Quebec
- **[IGO](https://igouverte.org)** — Infrastructure Géomatique Ouverte, OGC services (WMS/WFS)

## 📄 License

MIT — see [LICENSE](LICENSE).

---

*A [mcsÉdition](https://mcsedition.com) project — Montréal, Québec 🇨🇦*
