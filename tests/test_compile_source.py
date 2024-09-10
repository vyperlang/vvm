import pytest
from packaging.version import Version

import vvm


def test_compile_source(foo_source, all_versions):
    if Version("0.4.0b1") <= all_versions <= Version("0.4.0b5"):
        pytest.skip("vyper 0.4.0b1 to 0.4.0b5 have a bug with combined_json")
    output = vvm.compile_source(foo_source)
    assert "<stdin>" in output


def test_compile_files(foo_path, all_versions):
    if Version("0.4.0b1") <= all_versions <= Version("0.4.0b5"):
        pytest.skip("vyper 0.4.0b1 to 0.4.0b5 have a bug with combined_json")
    output = vvm.compile_files([foo_path])
    assert foo_path.as_posix() in output


def test_compile_standard(input_json, foo_source):
    input_json["sources"] = {"contracts/Foo.vy": {"content": foo_source}}
    result = vvm.compile_standard(input_json)

    assert "contracts/Foo.vy" in result["contracts"]


@pytest.mark.parametrize("version_str", ["0.1.0b16", "0.1.0beta17"])
def test_pragmas_in_vyper_010(version_str):
    source = f"""
# @version {version_str}

@public
def foo() -> int128:
    return 42
    """
    vvm.compile_source(source, vyper_version=version_str)
