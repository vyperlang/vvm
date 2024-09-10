import pytest
from packaging.specifiers import Specifier
from packaging.version import Version

from vvm import detect_version_specifier
from vvm.main import pick_vyper_version

LAST_PER_MINOR = {
    1: Version("0.1.0b17"),
    2: Version("0.2.16"),
    3: Version("0.3.10"),
}


def test_foo_vyper_version(foo_source, all_versions, latest_version):
    specifier = detect_version_specifier(foo_source)
    assert str(specifier) == f"=={all_versions}"
    assert all_versions.major == 0
    assert pick_vyper_version(specifier) == all_versions


@pytest.mark.parametrize(
    "version_str,decorator,pragma,expected_specifier,expected_version",
    [
        ("^0.1.1", "public", "@version", "~=0.1", "latest"),
        ("~0.3.0", "external", "pragma version", "~=0.3.0", "0.3.10"),
        ("0.1.0b17", "public", "@version", "==0.1.0b17", "0.1.0b17"),
        (">=0.3.0-beta17", "external", "@version", ">=0.3.0-beta17", "latest"),
        ("0.4.0rc6", "external", "pragma version", "==0.4.0rc6", "0.4.0rc6"),
    ],
)
def test_vyper_version(version_str, decorator, pragma, expected_specifier, expected_version, latest_version):
    source = f"""
# {pragma} {version_str}

@{decorator}
def foo() -> int128:
    return 42
    """
    detected = detect_version_specifier(source)
    assert detected == Specifier(expected_specifier)
    if expected_version == "latest":
        expected_version = str(latest_version)
    assert pick_vyper_version(detected) == Version(expected_version)
