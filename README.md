# Données Québec MCP

[![CI](https://github.com/Stefen-Taime/donneesqc-mcp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Stefen-Taime/donneesqc-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)

Serveur [Model Context Protocol (MCP)](https://modelcontextprotocol.io) qui permet aux agents IA (Claude, ChatGPT, Gemini, etc.) de rechercher, explorer et analyser les jeux de données de [Données Québec](https://donneesquebec.ca), de la [Ville de Montréal](https://donnees.montreal.ca) et des services géospatiaux du gouvernement du Québec ([IGO](https://igouverte.org)), directement par conversation.

Au lieu de naviguer manuellement sur les portails, posez simplement vos questions :
_« Quels jeux de données existent sur la criminalité à Montréal ? »_ ou _« Combien d'actes criminels par arrondissement en 2025 ? »_ et obtenez des réponses instantanées, incluant des analyses SQL.

**Fonctionnalités clés :** Requêtes SQL sur le DataStore | Couches géospatiales OGC | 3 sources de données | Bilingue FR/EN

*[English version below](#english)*

---

## Exemples de requêtes

Voici ce que vous pouvez demander directement à votre agent IA :

### 1. Analyse SQL — criminalité par quartier

> « Quels sont les 10 postes de quartier avec le plus d'actes criminels à Montréal ? »

| Rang | PDQ | Total actes |
|------|-----|-------------|
| 1 | 38 (Centre-Sud) | 24 942 |
| 2 | 21 (Plateau-Mont-Royal) | 23 041 |
| 3 | 20 (Ville-Marie Est) | 20 135 |
| 4 | 48 (Saint-Laurent) | 16 163 |
| 5 | 26 (Côte-des-Neiges) | 15 955 |

*L'agent exécute automatiquement une requête SQL `GROUP BY` sur le DataStore montréalais.*

### 2. Exploration multi-outils — arbres publics

> « Trouve les données sur les arbres publics de Montréal, explore la structure, puis dis-moi combien d'arbres par arrondissement. »

L'agent enchaîne 3 outils : `search_montreal_datasets` pour trouver le jeu, `query_montreal_data` pour explorer les colonnes, puis `query_montreal_sql` pour l'agrégation. Résultat : **333 556 arbres** répartis dans 13 arrondissements, Mercier-Hochelaga-Maisonneuve en tête (37 871).

### 3. Statistiques du catalogue

> « Combien d'organisations publient des données sur Données Québec ? »

**139 organisations**, **1 584 jeux de données**. La Ville de Montréal domine avec 383 jeux (24 % du catalogue), suivie de Laval (133) et du MELCCFP (119).

### 4. Tendance temporelle

> « Quelle est la tendance mensuelle des actes criminels à Montréal ? »

L'agent identifie un pic au printemps/été (~2 700/mois) et une baisse en hiver (~1 700-2 000/mois) via une requête SQL avec `GROUP BY` sur les dates.

### 5. Données géospatiales — patrimoine culturel

> « Quelles couches géospatiales sont disponibles pour le patrimoine culturel du Québec ? »

L'agent interroge le WFS IGO et trouve 7 couches du Ministère de la Culture : sites patrimoniaux nationaux, déclarés, cités, terrains protégés — avec schéma complet (nom, adresse, période de construction, statut juridique).

**[Voir tous les exemples avec réponses complètes](EXAMPLES.md)**

---

## Connecter votre agent IA au serveur MCP

Utilisez le endpoint hébergé (bientôt disponible) ou lancez localement. La configuration dépend de votre client :

[Claude Code](#claude-code) | [Claude Desktop](#claude-desktop) | [ChatGPT](#chatgpt) | [Cursor](#cursor) | [VS Code](#vs-code) | [Gemini CLI](#gemini-cli) | [Le Chat (Mistral)](#le-chat-mistral) | [Windsurf](#windsurf)

### Claude Code

```bash
claude mcp add --transport http donneesqc http://localhost:8000/mcp
```

> **Note :** Si Claude Code bloque les appels réseau vers les API externes, ajoutez les domaines à la whitelist dans votre `.claude/settings.json` :
>
> ```json
> {
>   "permissions": {
>     "allow": [
>       "WebFetch(domain:registreentreprises.gouv.qc.ca)",
>       "WebFetch(domain:www.donneesquebec.ca)"
>     ]
>   }
> }
> ```

### Claude Desktop

Ajoutez dans votre fichier de configuration Claude Desktop :

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

*Forfaits payants seulement.* Allez dans `Settings` > `Apps and connectors` > activez le **Developer mode** > `Add new connector` avec l'URL `http://localhost:8000/mcp`.

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

Ajoutez dans `mcp.json` (lancez **MCP: Open User Configuration** depuis la palette de commandes) :

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

Ajoutez dans `~/.gemini/settings.json` :

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

`Intelligence` > `Connectors` > `Add connector` > `Custom MCP Connector` > URL : `http://localhost:8000/mcp`.

### Windsurf

Ajoutez dans `~/.codeium/windsurf/mcp_config.json` :

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

## Lancer localement

### Avec Docker (recommandé)

```bash
git clone https://github.com/Stefen-Taime/donneesqc-mcp.git
cd donneesqc-mcp
docker compose up -d
```

### Installation manuelle

```bash
git clone https://github.com/Stefen-Taime/donneesqc-mcp.git
cd donneesqc-mcp
uv sync
cp .env.example .env
set -a && source .env && set +a
uv run python main.py
```

**Variables d'environnement :**

| Variable | Défaut | Description |
|---|---|---|
| `MCP_HOST` | `0.0.0.0` | Adresse d'écoute. Utilisez `127.0.0.1` en développement local. |
| `MCP_PORT` | `8000` | Port du serveur HTTP. |
| `MCP_ENV` | `local` | Nom de l'environnement (Sentry). |
| `DQ_API_URL` | `https://www.donneesquebec.ca/recherche/api/3/action` | API CKAN de Données Québec. |
| `MTL_API_URL` | `https://donnees.montreal.ca/api/3/action` | API CKAN de Montréal. |
| `GEO_WFS_URL` | `https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi` | Endpoint WFS IGO. |
| `GEO_WMS_URL` | `https://geoegl.msp.gouv.qc.ca/ws/igo_gouvouvert.fcgi` | Endpoint WMS IGO. |
| `LOG_LEVEL` | `INFO` | Niveau de journalisation Python. |
| `SENTRY_DSN` | _(non défini)_ | DSN Sentry pour le monitoring. |

## Transport

Construit avec le [SDK Python MCP officiel](https://github.com/modelcontextprotocol/python-sdk). **Streamable HTTP uniquement** — STDIO et SSE ne sont pas supportés.

**Endpoints :**
- `POST /mcp` — Messages JSON-RPC
- `GET /health` — Sonde de santé

## Outils disponibles (16)

### Données Québec — jeux de données (9 outils)

| Outil | Description |
|---|---|
| `search_datasets` | Recherche par mots-clés, organisation, tags |
| `get_dataset_info` | Métadonnées complètes d'un jeu de données |
| `list_dataset_resources` | Liste les fichiers/ressources d'un jeu |
| `get_resource_info` | Détail d'une ressource spécifique |
| `query_resource_data` | Interroge le DataStore avec filtres et pagination |
| `query_resource_sql` | **SQL direct** — agrégations, jointures, sous-requêtes |
| `list_organizations` | Ministères, villes, organismes |
| `get_organization_info` | Détail d'une organisation |
| `get_catalog_stats` | Statistiques globales du catalogue |

### Ville de Montréal (3 outils)

| Outil | Description |
|---|---|
| `search_montreal_datasets` | Recherche sur donnees.montreal.ca |
| `query_montreal_data` | Interroge le DataStore montréalais |
| `query_montreal_sql` | SQL sur les données montréalaises |

### Géospatial / IGO (4 outils)

| Outil | Description |
|---|---|
| `list_geospatial_layers` | Couches WFS/WMS depuis IGO |
| `get_geospatial_features` | Entités GeoJSON depuis le WFS |
| `describe_geospatial_layer` | Schéma d'une couche (champs, types) |
| `get_map_url` | URL d'image cartographique WMS |

## Tests

```bash
# Lancer tous les tests
uv run pytest

# Mode verbeux
uv run pytest -v

# Test interactif avec MCP Inspector
npx @modelcontextprotocol/inspector --http-url "http://127.0.0.1:8000/mcp"
```

## Contribuer

- **1 fonctionnalité = 1 PR**
- Tout le code doit être révisé et testé par un humain avant soumission.

```bash
# Lint et formatage
uv run ruff check --fix && uv run ruff format

# Vérification de types
uv run ty check

# Installer les hooks pre-commit
uv run pre-commit install
```

### Releases

```bash
./tag_version.sh 1.0.0            # Créer une release
./tag_version.sh 1.0.0 --dry-run  # Aperçu
```

## Sources de données

- **[Données Québec](https://donneesquebec.ca)** — Portail provincial (gouvernement + municipalités), basé sur CKAN
- **[donnees.montreal.ca](https://donnees.montreal.ca)** — Portail municipal de Montréal, le plus riche au Québec
- **[IGO](https://igouverte.org)** — Infrastructure Géomatique Ouverte, services OGC (WMS/WFS)

## Licence

MIT — voir [LICENSE](LICENSE).

---

## English

MCP server that lets AI agents (Claude, ChatGPT, Gemini, etc.) search, explore, and analyze open datasets from [Données Québec](https://donneesquebec.ca), [Ville de Montréal](https://donnees.montreal.ca), and Quebec's geospatial services ([IGO](https://igouverte.org)) through conversation.

Instead of manually browsing portals, simply ask questions like _"What datasets exist about crime in Montreal?"_ or _"How many criminal acts per borough in 2025?"_ and get instant answers — including SQL-powered analytics.

All setup instructions, tool descriptions, and environment variables are documented in the French section above. The configuration snippets (JSON, bash) are language-independent and apply as-is.

### Quick start

```bash
git clone https://github.com/Stefen-Taime/donneesqc-mcp.git
cd donneesqc-mcp
docker compose up -d
```

Then connect your AI client to `http://localhost:8000/mcp` — see the [connection section above](#connecter-votre-agent-ia-au-serveur-mcp) for client-specific configs.

### Available tools (16)

- **Données Québec** (9): dataset search, metadata, DataStore queries, direct SQL, organizations, catalog stats
- **Ville de Montréal** (3): dataset search, DataStore queries, SQL
- **Geospatial / IGO** (4): WFS/WMS layer listing, GeoJSON features, layer schema, map image URLs

---

*Un projet [mcsÉdition](https://mcsedition.org/fr) — Montréal, Québec*
