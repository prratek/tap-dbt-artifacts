"""dbtArtifacts tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_dbt_artifacts.streams import (
    DbtArtifactsStream,
    ManifestStream,
)

STREAM_TYPES = [
    ManifestStream,
]


class TapDbtArtifacts(Tap):
    """dbtArtifacts tap class."""
    name = "tap-dbt-artifacts"

    config_jsonschema = th.PropertiesList(
        th.Property("dbt_target_dir", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
