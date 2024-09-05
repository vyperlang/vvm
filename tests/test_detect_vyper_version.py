import pytest

from vvm import detect_vyper_version_from_source


def test_detect_vyper_version_from_source(foo_source, all_versions):
    assert detect_vyper_version_from_source(foo_source) == str(all_versions)

@pytest.mark.parametrize(
    "version_str,decorator",
    [
        ("0.1.0b17", "public"),
        ("0.3.0-beta17", "external"),
        ("0.4.0rc6", "external"),
    ],
)
def test_detect_vyper_version_beta(version_str, decorator):
    source = f"""
# @version {version_str}

@{decorator}
def foo() -> int128:
    return 42
    """
    assert detect_vyper_version_from_source(source) == version_str
