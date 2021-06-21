"""Custom client handling, including dbtArtifactsStream base class."""

import abc
import json
from typing import Optional, Iterable

from singer_sdk.streams import Stream


class DbtArtifactsStream(Stream):
    """Stream class for dbtArtifacts streams."""

    @property
    def artifact_path(self) -> str:
        return f"{self._config['dbt_target_dir']}/{self.name}.json"

    @abc.abstractmethod
    def process_record(self, record: dict) -> dict:
        return record

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        with open(self.artifact_path) as f:
            data = json.load(f)
            yield self.process_record(data)
