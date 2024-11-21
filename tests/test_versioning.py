import pytest
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version

from vvm import detect_vyper_version_from_source
from vvm.exceptions import UnexpectedVersionError
from vvm.utils.versioning import _pick_vyper_version, detect_version_specifier_set


def test_foo_vyper_version(foo_source, vyper_version):
    specifier = detect_version_specifier_set(foo_source)
    assert str(specifier) == f"=={vyper_version}"
    assert vyper_version.major == 0
    assert _pick_vyper_version(specifier) == vyper_version


@pytest.mark.parametrize(
    "version_str,decorator,pragma,expected_specifier_set,expected_version",
    [
        # npm's ^ gets converted to ~=
        ("^0.2.0", "public", "@version", "~=0.2.0", "0.2.16"),
        ("^0.4.0", "external", "pragma version", "~=0.4.0", "0.4.0"),
        ("^0.1.0b16", "public", "@version", "~=0.1.0b16", "0.1.0b17"),
        # indented comment is supported
        ("0.4.0", "external", "    pragma version", "==0.4.0", "0.4.0"),
        # pep440 >= and < are preserved
        (">=0.3.10, <0.4.0", "external", "pragma version", ">=0.3.10, <0.4.0", "0.3.10"),
        # beta and release candidate are supported
        ("0.1.0b17", "public", "@version", "==0.1.0b17", "0.1.0b17"),
        ("0.4.0rc6", "external", "pragma version", "==0.4.0rc6", "0.4.0rc6"),
        (">=0.3.0-beta17", "external", "@version", ">=0.3.0b17", "latest"),
    ],
)
def test_vyper_version(
    version_str, decorator, pragma, expected_specifier_set, expected_version, latest_version
):
    source = f"""
# {pragma} {version_str}

@{decorator}
def foo() -> int128:
    return 42
    """
    detected = detect_version_specifier_set(source)
    assert detected == SpecifierSet(expected_specifier_set)
    if expected_version == "latest":
        expected_version = str(latest_version)
    assert detect_vyper_version_from_source(source) == Version(expected_version)


@pytest.mark.parametrize(
    "version_str",
    [
        "~0.2.0",
        ">= 0.3.1 < 0.4.0",
        "0.3.1 - 0.3.2",
        "0.3.1 || 0.3.2",
        "=0.3.1",
    ],
)
def test_unsported_vyper_version(version_str):
    # npm's complex ranges are not supported although old vyper versions can handle them
    source = f"""
# @version {version_str}
    """
    with pytest.raises(InvalidSpecifier):
        detect_version_specifier_set(source)


def test_no_version_in_source():
    assert detect_vyper_version_from_source("def foo() -> int128: return 42") is None


def test_version_does_not_exist():
    with pytest.raises(UnexpectedVersionError) as excinfo:
        detect_vyper_version_from_source("# pragma version 2024.0.1")
    assert str(excinfo.value) == "No installable Vyper satisfies the specifier ==2024.0.1"
