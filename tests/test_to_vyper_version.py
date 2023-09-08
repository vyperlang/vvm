import pytest
from packaging.version import Version

from vvm.utils.convert import to_vyper_version


@pytest.mark.parametrize(
    "version_str",
    ["0.1.0b17", "0.1.0beta17", "0.1.0-beta17", "0.1.0.beta17", "0.1.0B17", "0.1.0.Beta.17"],
)
def test_to_vyper_version(version_str):
    assert to_vyper_version(version_str) == Version("0.1.0-beta.17")
