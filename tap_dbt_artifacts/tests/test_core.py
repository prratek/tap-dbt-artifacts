"""Tests standard tap features using the built-in SDK tests library."""

from pathlib import Path

from singer_sdk.helpers._util import read_json_file
from singer_sdk.tap_base import Tap
from singer_sdk.testing import get_standard_tap_tests

from tap_dbt_artifacts.tap import TapDbtArtifacts

if Path(".secrets/config.json").exists():
    SAMPLE_CONFIG = read_json_file(".secrets/config.json")
else:
    SAMPLE_CONFIG = {
        "dbt_target_dir": "/home/runner/work/tap-dbt-artifacts/tap-dbt-artifacts/jaffle_shop/target"
    }


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapDbtArtifacts, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# Test that discovery returns streams for all 4 artifacts
def test_discover_stream_output():
    tap: Tap = TapDbtArtifacts(config=SAMPLE_CONFIG, parse_env_config=True)
    streams = tap.discover_streams()
    stream_ids = {stream.tap_stream_id for stream in streams}
    assert stream_ids == {"manifest", "catalog", "sources", "run_results"}
