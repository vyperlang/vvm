import vvm


def test_compile_source(foo_source):
    output = vvm.compile_source(foo_source)
    assert "<stdin>" in output


def test_compile_files(foo_path):
    output = vvm.compile_files([foo_path])
    assert foo_path.as_posix() in output


def test_compile_standard(input_json, foo_source):
    input_json["sources"] = {"contracts/Foo.vy": {"content": foo_source}}
    result = vvm.compile_standard(input_json)

    assert "contracts/Foo.vy" in result["contracts"]
