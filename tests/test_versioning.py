import pytest
from packaging.specifiers import Specifier
from packaging.version import Version

from vvm import detect_vyper_version_from_source
from vvm.exceptions import UnexpectedVersionError
from vvm.utils.versioning import _detect_version_specifier, _pick_vyper_version

LAST_PER_MINOR = {
    1: Version("0.1.0b17"),
    2: Version("0.2.16"),
    3: Version("0.3.10"),
}


def test_foo_vyper_version(foo_source, all_versions, latest_version):
    specifier = _detect_version_specifier(foo_source)
    assert str(specifier) == f"=={all_versions}"
    assert all_versions.major == 0
    assert _pick_vyper_version(specifier) == all_versions


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
def test_vyper_version(
    version_str, decorator, pragma, expected_specifier, expected_version, latest_version
):
    source = f"""
# {pragma} {version_str}

@{decorator}
def foo() -> int128:
    return 42
    """
    detected = _detect_version_specifier(source)
    assert detected == Specifier(expected_specifier)
    if expected_version == "latest":
        expected_version = str(latest_version)
    assert detect_vyper_version_from_source(source) == Version(expected_version)


def test_no_version_in_source():
    with pytest.raises(UnexpectedVersionError) as excinfo:
        detect_vyper_version_from_source("def foo() -> int128: return 42")
    assert str(excinfo.value) == "No version detected in source code"


def test_version_does_not_exist(all_versions):
    with pytest.raises(UnexpectedVersionError) as excinfo:
        detect_vyper_version_from_source(f"# pragma version 2024.0.1")
    assert str(excinfo.value) == "No installable Vyper satisfies the specifier ==2024.0.1"
