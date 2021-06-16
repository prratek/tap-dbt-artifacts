"""Stream type classes for tap-dbt-artifacts."""

from pathlib import Path
from typing import Dict, List

from tap_dbt_artifacts.client import DbtArtifactsStream


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ManifestStream(DbtArtifactsStream):
    """Stream for manifest.json"""
    name = "manifest"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "manifest.schema.json"

    @staticmethod
    def _listify_columns(node: dict) -> dict:
        if node.get("columns"):
            node["columns"] = [node["columns"][col] for col in node["columns"]]
        return node

    @staticmethod
    def _listify_cluster_by(node: dict) -> dict:
        if node.get("config", {}).get("cluster_by") and isinstance(node["config"]["cluster_by"], str):
            node["config"]["cluster_by"] = [node["config"]["cluster_by"]]
        if node.get("unrendered_config", {}).get("cluster_by") and isinstance(node["unrendered_config"]["cluster_by"], str):
            node["unrendered_config"]["cluster_by"] = [node["unrendered_config"]["cluster_by"]]
        return node

    @staticmethod
    def _stringify_accepted_values(node: dict) -> dict:
        if node.get("test_metadata", {}).get("kwargs", {}).get("values"):
            node["test_metadata"]["kwargs"]["values"] = [str(val) for val in node["test_metadata"]["kwargs"]["values"]]
        return node

    @staticmethod
    def _wrap_nested_array(nested_arr: List[List], key_name: str) -> List[Dict[str, List]]:
        return [{key_name: val} for val in nested_arr]

    def _wrap_node_nested_arrays(self, node: dict) -> dict:
        if node.get("sources"):
            node["sources"] = self._wrap_nested_array(node["sources"], "source")
        if node.get("refs"):
            node["refs"] = self._wrap_nested_array(node["refs"], "ref")
        return node

    def process_record(self, record: dict) -> dict:
        fields_to_listify = ["nodes", "sources", "macros", "docs", "exposures", "selectors"]
        parent_child_fields = ["parent_map", "child_map"]

        for field in fields_to_listify:
            record[field] = [self._listify_columns(record[field][entry]) for entry in record[field]]
            if field == "nodes":
                record[field] = [
                    self._stringify_accepted_values(self._listify_cluster_by(self._wrap_node_nested_arrays(entry)))
                    for entry in record[field]
                ]

        for field in parent_child_fields:
            record[field] = [
                {"node": node, "parents": record[field][node]}
                for node in record[field]
            ]
        return record