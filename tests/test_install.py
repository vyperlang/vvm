import vvm


def test_get_installed_vyper_versions(all_versions):
    assert "exe" not in str(all_versions)
    assert all_versions in vvm.install.get_installed_vyper_versions()
