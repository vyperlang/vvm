import vvm


def test_get_installed_vyper_versions(vyper_version):
    assert "exe" not in str(vyper_version)
    assert vyper_version in vvm.install.get_installed_vyper_versions()
