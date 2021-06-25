"""DbtArtifacts tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_dbt_artifacts.streams import (
    CatalogStream,
    ManifestStream,
    RunResultsStream,
    SourcesStream,
)

STREAM_TYPES = [
    CatalogStream,
    ManifestStream,
    RunResultsStream,
    SourcesStream,
]


class TapDbtArtifacts(Tap):
    """DbtArtifacts tap class."""

    name = "tap-dbt-artifacts"

    config_jsonschema = th.PropertiesList(
        th.Property("dbt_target_dir", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
