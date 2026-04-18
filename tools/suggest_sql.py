"""Genere un squelette SQL a partir du schema d'une ressource DataStore."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)

# Types numeriques DataStore
_NUMERIC_TYPES = {
    "int", "int4", "int8", "float", "float4", "float8",
    "numeric", "integer", "bigint", "real", "double precision",
}
_DATE_TYPES = {"date", "timestamp", "timestamptz", "timestamp without time zone", "timestamp with time zone"}
_TEXT_TYPES = {"text", "varchar", "character varying", "char"}


@mcp.tool()
async def suggest_sql(resource_id: str) -> str:
    """Genere des squelettes SQL utiles a partir du schema d'une ressource DataStore.

    Analyse les colonnes et leurs types pour proposer des requetes pertinentes :
    - SELECT de base avec LIMIT
    - COUNT total
    - GROUP BY sur les colonnes texte
    - Agregations (SUM, AVG, MIN, MAX) sur les colonnes numeriques
    - Filtrage par date si applicable

    Parameters:
        resource_id: ID de la ressource DataStore.
    """
    try:
        # Recuperer le schema via une requete minimale
        result = await ckan_api.datastore_search(
            DQ_API_URL,
            resource_id=resource_id,
            limit=0,
        )

        fields = [f for f in result.get("fields", []) if f["id"] != "_id"]
        if not fields:
            return json.dumps({"error": "Aucun champ trouve pour cette ressource."}, ensure_ascii=False)

        table_ref = f'"{resource_id}"'
        all_cols = ", ".join(f'"{f["id"]}"' for f in fields)

        numeric_fields = [f for f in fields if f.get("type", "").lower() in _NUMERIC_TYPES]
        text_fields = [f for f in fields if f.get("type", "").lower() in _TEXT_TYPES]
        date_fields = [f for f in fields if f.get("type", "").lower() in _DATE_TYPES]

        suggestions: list[dict[str, str]] = []

        # 1. Apercu
        suggestions.append({
            "name": "Apercu des donnees",
            "sql": f"SELECT {all_cols}\nFROM {table_ref}\nLIMIT 10",
        })

        # 2. Comptage total
        suggestions.append({
            "name": "Nombre total de lignes",
            "sql": f"SELECT COUNT(*) as total\nFROM {table_ref}",
        })

        # 3. GROUP BY sur texte
        for f in text_fields[:3]:
            col = f'"{f["id"]}"'
            suggestions.append({
                "name": f"Repartition par {f['id']}",
                "sql": f"SELECT {col}, COUNT(*) as nb\nFROM {table_ref}\nGROUP BY {col}\nORDER BY nb DESC\nLIMIT 20",
            })

        # 4. Agregations numeriques
        if numeric_fields:
            agg_parts = []
            for nf in numeric_fields[:5]:
                col = f'"{nf["id"]}"'
                agg_parts.append(f"  AVG({col}) as avg_{nf['id']}")
                agg_parts.append(f"  MIN({col}) as min_{nf['id']}")
                agg_parts.append(f"  MAX({col}) as max_{nf['id']}")
            agg_sql = ",\n".join(agg_parts)
            suggestions.append({
                "name": "Statistiques numeriques",
                "sql": f"SELECT\n  COUNT(*) as total,\n{agg_sql}\nFROM {table_ref}",
            })

        # 5. Filtrage par date
        for df in date_fields[:1]:
            col = f'"{df["id"]}"'
            date_sql = (
                f"SELECT {all_cols}\nFROM {table_ref}\n"
                f"WHERE {col} >= '2024-01-01'\nORDER BY {col} DESC\nLIMIT 20"
            )
            suggestions.append({
                "name": f"Donnees recentes (par {df['id']})",
                "sql": date_sql,
            })

        # 6. Cross-tab si texte + numerique
        if text_fields and numeric_fields:
            tcol = f'"{text_fields[0]["id"]}"'
            ncol = f'"{numeric_fields[0]["id"]}"'
            cross_sql = (
                f"SELECT {tcol}, SUM({ncol}) as total\nFROM {table_ref}\n"
                f"GROUP BY {tcol}\nORDER BY total DESC\nLIMIT 20"
            )
            suggestions.append({
                "name": f"Somme de {numeric_fields[0]['id']} par {text_fields[0]['id']}",
                "sql": cross_sql,
            })

        return json.dumps(
            {
                "resource_id": resource_id,
                "schema": [{"name": f["id"], "type": f.get("type", "unknown")} for f in fields],
                "suggestions": suggestions,
                "tip": "Copiez une requete et executez-la avec query_resource_sql.",
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        logger.exception("Erreur dans suggest_sql")
        return json.dumps(
            {"error": f"Impossible de generer des suggestions SQL pour '{resource_id}'."},
            ensure_ascii=False,
        )
