"""Compare deux jeux de donnees (colonnes, volumes, organisations)."""

import json
import logging

from helpers import ckan_api
from helpers.config import DQ_API_URL
from tools import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def compare_datasets(dataset_id_1: str, dataset_id_2: str) -> str:
    """Compare deux jeux de donnees de Donnees Quebec.

    Retourne un diff detaille : metadonnees, colonnes, volumes, organisations,
    formats et dates de mise a jour.

    Parameters:
        dataset_id_1: ID ou slug du premier jeu de donnees.
        dataset_id_2: ID ou slug du deuxieme jeu de donnees.
    """
    try:
        pkg1 = await ckan_api.package_show(DQ_API_URL, dataset_id_1)
        pkg2 = await ckan_api.package_show(DQ_API_URL, dataset_id_2)

        def _extract_info(pkg: dict) -> dict:
            resources = pkg.get("resources", [])
            formats = sorted({(r.get("format") or "inconnu").upper() for r in resources})
            datastore_count = sum(1 for r in resources if r.get("datastore_active"))
            return {
                "id": pkg.get("id"),
                "name": pkg.get("name"),
                "title": pkg.get("title"),
                "organization": pkg.get("organization", {}).get("title", ""),
                "license": pkg.get("license_title", "non specifiee"),
                "tags": sorted(t["name"] for t in pkg.get("tags", [])),
                "num_resources": len(resources),
                "datastore_resources": datastore_count,
                "formats": formats,
                "created": pkg.get("metadata_created"),
                "modified": pkg.get("metadata_modified"),
                "update_frequency": pkg.get("update_frequency", "non specifiee"),
            }

        info1 = _extract_info(pkg1)
        info2 = _extract_info(pkg2)

        # Comparer les tags
        tags1 = set(info1["tags"])
        tags2 = set(info2["tags"])
        common_tags = sorted(tags1 & tags2)
        only_in_1 = sorted(tags1 - tags2)
        only_in_2 = sorted(tags2 - tags1)

        # Comparer les formats
        formats1 = set(info1["formats"])
        formats2 = set(info2["formats"])

        # Essayer de comparer les colonnes DataStore
        columns_diff = None
        try:
            res1 = [r for r in pkg1.get("resources", []) if r.get("datastore_active")]
            res2 = [r for r in pkg2.get("resources", []) if r.get("datastore_active")]
            if res1 and res2:
                ds1 = await ckan_api.datastore_search(DQ_API_URL, resource_id=res1[0]["id"], limit=0)
                ds2 = await ckan_api.datastore_search(DQ_API_URL, resource_id=res2[0]["id"], limit=0)
                cols1 = {f["id"] for f in ds1.get("fields", []) if f["id"] != "_id"}
                cols2 = {f["id"] for f in ds2.get("fields", []) if f["id"] != "_id"}
                columns_diff = {
                    "dataset_1_resource": res1[0]["id"],
                    "dataset_2_resource": res2[0]["id"],
                    "common_columns": sorted(cols1 & cols2),
                    "only_in_dataset_1": sorted(cols1 - cols2),
                    "only_in_dataset_2": sorted(cols2 - cols1),
                    "dataset_1_total_rows": ds1.get("total", "N/A"),
                    "dataset_2_total_rows": ds2.get("total", "N/A"),
                }
        except Exception:
            logger.debug("Impossible de comparer les colonnes DataStore")

        result = {
            "dataset_1": info1,
            "dataset_2": info2,
            "comparison": {
                "same_organization": info1["organization"] == info2["organization"],
                "same_license": info1["license"] == info2["license"],
                "tags": {
                    "common": common_tags,
                    "only_in_dataset_1": only_in_1,
                    "only_in_dataset_2": only_in_2,
                },
                "formats": {
                    "common": sorted(formats1 & formats2),
                    "only_in_dataset_1": sorted(formats1 - formats2),
                    "only_in_dataset_2": sorted(formats2 - formats1),
                },
            },
        }

        if columns_diff:
            result["comparison"]["columns"] = columns_diff

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception:
        logger.exception("Erreur dans compare_datasets")
        return json.dumps(
            {"error": f"Impossible de comparer '{dataset_id_1}' et '{dataset_id_2}'. Verifiez les identifiants."},
            ensure_ascii=False,
        )
