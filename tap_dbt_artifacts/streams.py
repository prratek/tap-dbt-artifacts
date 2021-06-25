"""Stream type classes for tap-dbt-artifacts."""

from pathlib import Path
from typing import Dict, List

from tap_dbt_artifacts.client import DbtArtifactsStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


def create_id_col(record: dict, col_name: str = "id") -> dict:
    record[col_name] = record["metadata"]["invocation_id"]
    return record


class CatalogStream(DbtArtifactsStream):
    """Stream for manifest.json"""

    name = "catalog"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "catalog.schema.json"

    @staticmethod
    def _listify_columns(node: dict) -> dict:
        if node.get("columns"):
            node["columns"] = [node["columns"][col] for col in node["columns"]]
        return node

    def process_record(self, record: dict) -> dict:
        fields_to_listify = ["nodes", "sources"]
        record = create_id_col(record)

        for field in fields_to_listify:
            record[field] = [
                self._listify_columns(record[field][entry]) for entry in record[field]
            ]
            if field == "nodes":
                record[field] = [entry for entry in record[field]]

        return record


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
        if node.get("config", {}).get("cluster_by") and isinstance(
            node["config"]["cluster_by"], str
        ):
            node["config"]["cluster_by"] = [node["config"]["cluster_by"]]
        if node.get("unrendered_config", {}).get("cluster_by") and isinstance(
            node["unrendered_config"]["cluster_by"], str
        ):
            node["unrendered_config"]["cluster_by"] = [
                node["unrendered_config"]["cluster_by"]
            ]
        return node

    @staticmethod
    def _stringify_accepted_values(node: dict) -> dict:
        if node.get("test_metadata", {}).get("kwargs", {}).get("values"):
            node["test_metadata"]["kwargs"]["values"] = [
                str(val) for val in node["test_metadata"]["kwargs"]["values"]
            ]
        return node

    @staticmethod
    def _wrap_nested_array(
        nested_arr: List[List], key_name: str
    ) -> List[Dict[str, List]]:
        return [{key_name: val} for val in nested_arr]

    def _wrap_node_nested_arrays(self, node: dict) -> dict:
        if node.get("sources"):
            node["sources"] = self._wrap_nested_array(node["sources"], "source")
        if node.get("refs"):
            node["refs"] = self._wrap_nested_array(node["refs"], "ref")
        return node

    def process_record(self, record: dict) -> dict:
        fields_to_listify = [
            "nodes",
            "sources",
            "macros",
            "docs",
            "exposures",
            "selectors",
        ]
        parent_child_fields = ["parent_map", "child_map"]
        record = create_id_col(record)

        for field in fields_to_listify:
            record[field] = [
                self._listify_columns(record[field][entry]) for entry in record[field]
            ]
            if field == "nodes":
                record[field] = [
                    self._stringify_accepted_values(
                        self._listify_cluster_by(self._wrap_node_nested_arrays(entry))
                    )
                    for entry in record[field]
                ]
            elif field == "exposures":
                record[field] = [
                    self._wrap_node_nested_arrays(entry) for entry in record[field]
                ]

        for field in parent_child_fields:
            record[field] = [
                {"node": node, "parents": record[field][node]} for node in record[field]
            ]
        return record


class RunResultsStream(DbtArtifactsStream):
    """Stream for manifest.json"""

    name = "run_results"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "run-results.schema.json"

    @staticmethod
    def _stringify_message(result: dict) -> dict:
        result["message"] = str(result["message"])
        return result

    def process_record(self, record: dict) -> dict:
        record = create_id_col(record)
        record["results"] = [
            self._stringify_message(result) for result in record["results"]
        ]
        return record


class SourcesStream(DbtArtifactsStream):
    """Stream for manifest.json"""

    name = "sources"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "sources.schema.json"

    def process_record(self, record: dict) -> dict:
        record = create_id_col(record)
        return record
