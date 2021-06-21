"""Tests standard tap features using the built-in SDK tests library."""

import os

from singer_sdk.testing import get_standard_tap_tests

from tap_dbt_artifacts.tap import TapDbtArtifacts

SAMPLE_CONFIG = {
    "dbt_target_dir": os.environ.get("DBT_TARGET_DIR")
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapDbtArtifacts,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.
